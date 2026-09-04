# Zebra RAW — GC420t USB

Utilitário gráfico em português para Linux, Python 3 e GTK 3. Usa a fila CUPS existente e envia bytes com `lp -d FILA -o raw -o job-sheets=none`. Não precisa de servidor web, internet, privilégios administrativos ou bibliotecas pip.

## Executar

```sh
cd zebra-raw
./run.sh
```

## Instaladores Debian/Ubuntu e openSUSE

Baixe o código completo ou clone este repositório. Na pasta do projeto:

```sh
# Debian / Ubuntu
sudo sh install-debian-ubuntu.sh

# openSUSE Tumbleweed / Leap
sudo sh install-opensuse.sh
```

Os instaladores geram e instalam um pacote nativo, resolvem dependências pelo gerenciador da distribuição e adicionam **Zebra RAW** ao menu de aplicativos. Execute a interface como usuário normal. Não criam filas, não alteram a impressora e não enviam etiquetas durante a instalação.

Os pacotes ficam em `dist/`. Para instalar um pacote já gerado:

```sh
sudo apt install ./zebra-raw_1.0.0_all.deb
sudo zypper install --allow-unsigned-rpm ./zebra-raw-1.0.0-1.noarch.rpm
```

O RPM local não é assinado; a opção permite somente a instalação desse pacote sem assinatura, mantendo a verificação dos repositórios. Para remover: `sudo apt remove zebra-raw` ou `sudo zypper remove zebra-raw`. Os perfis pessoais são preservados. Atualizações são instaladas sobre a versão anterior pelo mesmo procedimento.

Requisitos: Python 3.8+, PyGObject, GTK 3 e clientes CUPS. É preciso ter uma fila USB GC420t configurada no CUPS e permissão de impressão. O nome `(EPL)` anunciado pelo dispositivo não impede o uso de ZPL via RAW. A aplicação não usa rede externa; comunica-se com o serviço CUPS local.

### Gerar os pacotes sem instalar

```sh
# Debian/Ubuntu: depende de dpkg-dev
./scripts/build-deb.sh
# openSUSE: depende de rpm-build, tar e gzip
./scripts/build-rpm.sh
```

Pacotes independentes de arquitetura (`all` / `noarch`). O workflow do GitHub testa o código e a instalação em Debian, Ubuntu e openSUSE Tumbleweed, disponibilizando os pacotes como artefatos de execução. Nenhuma licença de redistribuição foi escolhida para este projeto.

## Imprimir

1. Selecione a fila USB da GC420t.
2. Escolha um `.zpl` ou `.txt` contendo um formato `^XA ... ^XZ`.
3. Opcionalmente selecione o envio das configurações antes do arquivo.
4. Clique em **Enviar arquivo RAW**.

Os bytes são preservados, inclusive codificação e finais de linha. A prévia é textual e pode mostrar caracteres substitutos se a codificação não for UTF-8; isso não altera os bytes enviados. Não é renderização visual de ZPL. Arquivos UTF-16 são recusados. A codificação dos campos deve corresponder à configuração/comandos da impressora. Limites locais: arquivo de 32 MiB e trabalho de 64 MiB.

**Repetições** repetem o arquivo integralmente no mesmo trabalho RAW, sem depender de cópias do driver. Um arquivo com `^PQ10` repetido 3 vezes solicita 30 etiquetas. Arquivos podem conter várias etiquetas, imagens, downloads e outros comandos ZPL; selecione arquivos de origem conhecida. A validação básica não é um interpretador completo de ZPL; espera prefixos padrão `^` e `~`.

## Configuração

- Largura imprimível até 104 mm (832 dots), comprimento até 990 mm; resolução fixa de 8 dots/mm (203 dpi nominal).
- Transferência térmica com ribbon (`^MTT`) ou térmico direto (`^MTD`).
- Espaço/entalhe (`^MNY`), marca preta (`^MNM`), contínua (`^MNN`) ou detecção automática (`^MNA`).
- Velocidade conservadora de 2, 3 ou 4 pol/s; limite do modelo: 4 pol/s.
- Intensidade 0–30, deslocamento vertical, posição à esquerda e destaque manual.
- Modo de saída fixado em destaque manual (`^MMT`); sem corte, RFID, rede ou dispensador opcional.

Largura é área de impressão, não largura do rolo com suporte. O ajuste não escala desenhos. O comprimento indicado é o da etiqueta, sem o espaço; mídia descontínua depende também da calibração do sensor. Ajustes em dots: 8 dots = 1 mm. Deslocamento à esquerda usa o sinal nativo de `^LS`.

**Salvar perfil local** grava apenas no computador, em `$XDG_CONFIG_HOME/zebra-raw/profiles.json` (normalmente `~/.config/zebra-raw/profiles.json`). Digite um nome novo para criar outro perfil. Carregar um perfil não envia comandos. O perfil inicial é um exemplo de 100 × 150 mm com ribbon; ajuste conforme o material instalado.

**Aplicar na impressora** envia os ajustes. Com **Gravar também na memória**, acrescenta `^JUS`, que salva todos os parâmetros persistentes atuais da impressora. Sem essa opção, alterações podem desaparecer após desligar. Exportar cria um arquivo ZPL com os mesmos comandos exibidos em **Ver comandos ZPL**.

O utilitário não substitui comandos existentes nos arquivos: `^PW`, `^LL`, `^MT`, `^PR`, `~SD` e outros comandos posteriores podem prevalecer. Para ajustes uniformes, corrija esses comandos na origem do arquivo. Perfis são valores locais; não representam leitura de configuração do equipamento.

## Manutenção

- Calibrar mídia (`~JC`): pode avançar várias etiquetas; carregue papel/ribbon adequado e aplique o método de impressão antes.
- Imprimir configuração (`~WC`): relatório produzido pela impressora.
- Etiqueta de teste: moldura, texto e código de barras, usando os ajustes atuais; requer pelo menos 40 × 25 mm.
- Estado e trabalhos da fila CUPS.
- Cancelamento do último trabalho enviado nesta sessão. Dados já transmitidos à impressora não são recolhidos pelo cancelamento.

A aceitação pelo CUPS não prova que a etiqueta saiu. Consulte o LED da GC420t e o relatório impresso para falhas físicas. Nenhuma ação de impressão é executada automaticamente ao iniciar.

## Validação

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile core.py zebra.py
```

Testes cobrem geração e limites, persistência opcional, preservação binária, transporte RAW, repetições e seleção exclusiva de filas USB GC420t. A janela GTK e a descoberta de uma fila USB real foram verificadas no ambiente de desenvolvimento. A impressão física e calibração precisam ser verificadas com o material carregado; não foram disparadas durante o desenvolvimento.

## Referências

- [Manual GC420t](https://www.zebra.com/content/dam/support-dam/en/documentation/unrestricted/guide/product/gc420t-ug-en.pdf)
- [Especificações GC420](https://cpws.zebra.com/cpws/docs/gc420/gc420_specs.htm)
- [CUPS — envio sem filtros](https://openprinting.github.io/cups/)

O apêndice do manual contém exemplos genéricos de outros equipamentos (inclusive velocidades maiores). Este aplicativo limita a velocidade à especificação própria da GC420t e não expõe acessórios ausentes.
