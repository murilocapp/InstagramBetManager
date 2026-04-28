# InstagramBetManager

O **InstagramBetManager** é um bot desenvolvido em Python que utiliza a biblioteca `Instaloader` para coletar comentários de postagens no Instagram, extrair e validar apostas de resultados da Copa do Mundo, e gerar uma tabela de classificação baseada nos acertos.

## Funcionalidades

- **Autenticação no Instagram**: Login via `getpass` — a senha nunca é exposta em argumentos de linha de comando.
- **Coleta de comentários**: Itera sobre dias e shortcodes definidos no CSV de entrada, com salvamento automático de progresso em caso de erro.
- **Extração de apostas**: Identifica o padrão `NxN Time` nos comentários (ex: `2x1 Brasil`). Quando não encontrado, usa o texto bruto como fallback.
- **Validação de apostas**: Normaliza ambos os lados da comparação — remove acentos, converte para lowercase e separa números de texto — tornando a validação tolerante a variações como `2 x 1 brasil`, `2X1 BRASIL` ou `2x1Brasil`.
- **Geração de relatórios**: Exporta comentários brutos, dados processados e leaderboard em CSV.

## Requisitos

- Python 3.10 ou superior
- Dependências externas:
  - `instaloader`
  - `pandas`
  - `unidecode`

> `argparse`, `getpass`, `logging`, `re` e `pathlib` fazem parte da stdlib — não requerem instalação.

Instale as dependências com:

```bash
pip install instaloader pandas unidecode
```

## Como usar

### Clone o repositório

```bash
git clone https://github.com/murilocapp/InstagramBetManager.git
cd InstagramBetManager
```

### Prepare o arquivo de entrada

Crie um arquivo CSV com as seguintes colunas:

| Coluna      | Descrição                                      | Exemplo        |
|-------------|------------------------------------------------|----------------|
| `shortcode` | Identificador do post no Instagram             | `CxYz123ABC`   |
| `Day`       | Dia da rodada                                  | `1`            |
| `result`    | Resultado esperado para comparação com apostas | `2x1 Brazil`   |

```csv
shortcode,Day,result
CxYz123ABC,1,2x1 Brazil
WXYZ567800,1,3x0 Germany
AbCd987654,2,1x1 Argentina
```

### Execute o script

```bash
python worldcup_bet_validator.py \
    --input input.csv \
    --output-dir ./output \
    --username seu_usuario_instagram
```

A senha será solicitada de forma segura via `getpass` após a execução do comando.

#### Parâmetros disponíveis

| Argumento      | Obrigatório | Descrição                               | Default |
|----------------|-------------|-----------------------------------------|---------|
| `--input`      | Sim         | Caminho para o CSV de entrada           | —       |
| `--output-dir` | Não         | Diretório de saída para os CSVs gerados | `.`     |
| `--username`   | Sim         | Usuário do Instagram para autenticação  | —       |

## Monitoramento e salvamento automático

O script processa todos os posts especificados e coleta os comentários. Em caso de erro durante a coleta, o progresso acumulado até aquele ponto é salvo automaticamente em `progress.csv` dentro do `--output-dir` antes de encerrar.

## Resultados

Após execução bem-sucedida, os seguintes arquivos são gerados no diretório de saída:

| Arquivo             | Descrição                                                  |
|---------------------|------------------------------------------------------------|
| `data_all_days.csv` | Comentários brutos coletados de todos os posts             |
| `data.csv`          | Dados processados com colunas `bet` e `bet_result`         |
| `leaderboard.csv`   | Ranking de usuários ordenado por número de acertos         |
| `progress.csv`      | Progresso parcial — gerado apenas em caso de erro          |

## Estrutura do projeto

```
InstagramBetManager/
│
├── worldcup_bet_validator.py   # Script principal (CLI)
├── input.csv                   # Arquivo de entrada com shortcodes e resultados esperados
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
├── LICENSE
│
└── output/                     # Gerado automaticamente na execução
    ├── data_all_days.csv
    ├── data.csv
    ├── leaderboard.csv
    └── progress.csv
```

## Considerações de segurança

- A senha do Instagram **nunca** é passada como argumento — sempre solicitada via `getpass` em tempo de execução.
- Não versione `input.csv` ou os arquivos de saída caso contenham dados de usuários — adicione-os ao `.gitignore`.

`.gitignore` recomendado:

```
output/
input.csv
__pycache__/
*.pyc
.env
```

## Contribuições

Contribuições são bem-vindas. Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).
