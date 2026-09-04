"""GC420t: geração de comandos e transporte CUPS sem filtros."""
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'zebra-raw' / 'profiles.json'

@dataclass
class Settings:
    width: float = 100
    length: float = 150
    method: str = 'T'
    media: str = 'Y'
    speed: int = 2
    darkness: int = 10
    top: int = 0
    left: int = 0
    tear: int = 0

    def validate(self):
        for key, low, high in [('width', 1, 104), ('length', 1, 990), ('speed', 2, 4), ('darkness', 0, 30), ('top', -120, 120), ('left', -9999, 9999), ('tear', -120, 120)]:
            value = getattr(self, key)
            if not low <= value <= high:
                raise ValueError(f'{key}: valor deve estar entre {low} e {high}.')
            if key not in ('width', 'length') and int(value) != value:
                raise ValueError(f'{key}: use um número inteiro.')
        if self.method not in ('T', 'D') or self.media not in ('Y', 'N', 'M', 'A'):
            raise ValueError('Método de impressão ou mídia inválidos.')

    def zpl(self, persist=False):
        self.validate()
        return (f'^XA^MT{self.method}^MN{self.media}^MMT'
                f'^PW{round(self.width * 8)}^LL{round(self.length * 8)}'
                f'^PR{self.speed}~SD{self.darkness:02d}^LT{self.top}^LS{self.left}'
                f'~TA{self.tear}' + ('^JUS' if persist else '') + '^XZ\n').encode('ascii')


def run(args, data=None):
    try:
        result = subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=20, env={**os.environ, 'LC_ALL': 'C'})
    except FileNotFoundError as e:
        raise RuntimeError('Instale os clientes CUPS (lp, lpstat e cancel).') from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError('CUPS não respondeu em 20 s. Confira a fila antes de reenviar: o trabalho pode ter sido aceito.') from e
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace').strip() or 'Falha no CUPS.')
    return result.stdout.decode(errors='replace').strip()


def printers():
    rows = []
    for line in run(['lpstat', '-v']).splitlines():
        match = re.match(r'device for ([^:]+): (.+)', line)
        if match and 'usb://' in match[2].lower() and ('gc420t' in match[2].lower()):
            rows.append((match[1], match[2]))
    return rows


def read_zpl(path):
    p = Path(path)
    if p.suffix.lower() not in ('.txt', '.zpl'):
        raise ValueError('Escolha um arquivo .zpl ou .txt.')
    if p.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('Limite de arquivo: 32 MiB.')
    data = p.read_bytes()
    if not data.strip():
        raise ValueError('Arquivo vazio.')
    if b'\x00' in data[:1024] or data.startswith((b'\xff\xfe', b'\xfe\xff')):
        raise ValueError('Arquivo parece UTF-16. Exporte o ZPL em UTF-8 sem BOM ou na codificação da impressora.')
    if b'^XA' not in data or b'^XZ' not in data:
        raise ValueError('Não foi encontrado um formato ZPL com ^XA e ^XZ. EPL/PDF não são aceitos.')
    return data


def submit(printer, data, title, repeats=1):
    if printer not in dict(printers()):
        raise ValueError('Selecione uma fila USB da GC420t disponível.')
    if not 1 <= repeats <= 100:
        raise ValueError('Repetições devem estar entre 1 e 100.')
    if len(data) * repeats > 64 * 1024 * 1024:
        raise ValueError('Trabalho excede 64 MiB. Reduza as repetições.')
    return run(['lp', '-d', printer, '-o', 'raw', '-o', 'job-sheets=none', '-t', title], data * repeats)


def load_profiles():
    try:
        return json.loads(CONFIG.read_text())
    except FileNotFoundError:
        return {'profiles': {'Padrão': asdict(Settings())}, 'selected': 'Padrão'}


def save_profiles(value):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    temp = CONFIG.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False))
    temp.replace(CONFIG)
