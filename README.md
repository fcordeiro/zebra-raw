# Zebra RAW — impressoras térmicas Zebra USB

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
sudo apt install ./zebra-raw_1.2.1_all.deb
sudo zypper install --allow-unsigned-rpm ./zebra-raw-1.2.1-1.noarch.rpm
```

O RPM local não é assinado; a opção permite somente a instalação desse pacote sem assinatura, mantendo a verificação dos repositórios. Para remover: `sudo apt remove zebra-raw` ou `sudo zypper remove zebra-raw`. Os perfis pessoais são preservados. Atualizações são instaladas sobre a versão anterior pelo mesmo procedimento.

No Linux, os requisitos são Python 3.8+, PyGObject, GTK 3 e clientes CUPS. É preciso ter uma fila de impressora Zebra configurada e permissão de impressão. No Windows, o executável portátil usa a fila nativa do sistema. A aplicação trabalha com ZPL enviado em modo RAW; equipamentos configurados para EPL ou outro idioma precisam receber ZPL conforme a documentação do próprio modelo. A aplicação não usa rede externa.

### Gerar os pacotes sem instalar

```sh
# Debian/Ubuntu: depende de dpkg-dev
./scripts/build-deb.sh
# openSUSE: depende de rpm-build, tar e gzip
./scripts/build-rpm.sh
```

Pacotes independentes de arquitetura (`all` / `noarch`). O workflow do GitHub testa o código e a instalação em Debian, Ubuntu e openSUSE Tumbleweed, disponibilizando os pacotes como artefatos de execução. Nenhuma licença de redistribuição foi escolhida para este projeto.

### Windows portátil

O workflow **Testar e empacotar** também gera `Zebra-RAW.exe` para Windows. Baixe o artefato `windows-portable` da execução do GitHub Actions e execute o arquivo; ele é autocontido e não requer instalador, Python, GTK ou permissões de administrador no computador de destino. Para imprimir, basta que a impressora Zebra esteja instalada como uma fila do Windows.

## Imprimir

1. Selecione a fila da impressora Zebra.
2. Escolha um `.zpl` ou `.txt` contendo um formato `^XA ... ^XZ`.
3. Opcionalmente selecione o envio das configurações antes do arquivo.
4. Clique em **Enviar arquivo RAW**.

Os bytes são preservados, inclusive codificação e finais de linha. A prévia é textual e pode mostrar caracteres substitutos se a codificação não for UTF-8; isso não altera os bytes enviados. Não é renderização visual de ZPL. Arquivos UTF-16 são recusados. A codificação dos campos deve corresponder à configuração/comandos da impressora. Limites locais: arquivo de 32 MiB e trabalho de 64 MiB.

**Repetições** repetem o arquivo integralmente no mesmo trabalho RAW, sem depender de cópias do driver. Um arquivo com `^PQ10` repetido 3 vezes solicita 30 etiquetas. Arquivos podem conter várias etiquetas, imagens, downloads e outros comandos ZPL; selecione arquivos de origem conhecida. A validação básica não é um interpretador completo de ZPL; espera prefixos padrão `^` e `~`.

## Configuração

- Resolução selecionável: 203 dpi (8 dots/mm), 300 dpi (12 dots/mm) ou 600 dpi (24 dots/mm). Configure a que corresponde à sua impressora.
- Largura e comprimento de 1 a 1.000 mm, limitados a 32.000 dots pelo ZPL. Confirme também os limites físicos do equipamento e da mídia.
- Transferência térmica com ribbon (`^MTT`) ou térmico direto (`^MTD`).
- Espaço/entalhe (`^MNY`), marca preta (`^MNM`), contínua (`^MNN`) ou detecção automática (`^MNA`).
- Velocidade de 1 a 14 pol/s; selecione um valor suportado pelo seu modelo e pela mídia.
- Intensidade 0–30, deslocamento vertical, posição à esquerda e destaque manual.
- Modo de saída fixado em destaque manual (`^MMT`); sem corte, RFID, rede ou dispensador opcional.

Largura é área de impressão, não largura do rolo com suporte. O ajuste não escala desenhos. O comprimento indicado é o da etiqueta, sem o espaço; mídia descontínua depende também da calibração do sensor. Ajustes em dots dependem da resolução selecionada. Deslocamento à esquerda usa o sinal nativo de `^LS`.

**Salvar perfil local** grava apenas no computador, em `$XDG_CONFIG_HOME/zebra-raw/profiles.json` (normalmente `~/.config/zebra-raw/profiles.json`). Digite um nome novo para criar outro perfil. Carregar um perfil não envia comandos. O perfil inicial é um exemplo de 100 × 150 mm com ribbon; ajuste conforme o material instalado.

**Aplicar na impressora** envia os ajustes. Com **Gravar também na memória**, acrescenta `^JUS`, que salva todos os parâmetros persistentes atuais da impressora. Sem essa opção, alterações podem desaparecer após desligar. Exportar cria um arquivo ZPL com os mesmos comandos exibidos em **Ver comandos ZPL**.

O utilitário não substitui comandos existentes nos arquivos: `^PW`, `^LL`, `^MT`, `^PR`, `~SD` e outros comandos posteriores podem prevalecer. Para ajustes uniformes, corrija esses comandos na origem do arquivo. Perfis são valores locais; não representam leitura de configuração do equipamento.

## Manutenção

- Calibrar mídia (`~JC`): pode avançar várias etiquetas; carregue papel/ribbon adequado e aplique o método de impressão antes.
- Imprimir configuração (`~WC`): relatório produzido pela impressora.
- Etiqueta de teste: moldura, texto e código de barras, usando os ajustes atuais; requer pelo menos 40 × 25 mm.
- Estado e trabalhos da fila CUPS.
- Cancelamento do último trabalho enviado nesta sessão. Dados já transmitidos à impressora não são recolhidos pelo cancelamento.

A aceitação pelo CUPS não prova que a etiqueta saiu. Consulte os indicadores da impressora e o relatório impresso para falhas físicas. Nenhuma ação de impressão é executada automaticamente ao iniciar.

## Validação

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile core.py zebra.py
```

Testes cobrem geração e limites, persistência opcional, preservação binária, transporte RAW, repetições e seleção de filas USB Zebra. A janela GTK e a descoberta de uma fila USB real foram verificadas no ambiente de desenvolvimento. A impressão física e calibração precisam ser verificadas com o material carregado; não foram disparadas durante o desenvolvimento.

## Referências

- [CUPS — envio sem filtros](https://openprinting.github.io/cups/)
