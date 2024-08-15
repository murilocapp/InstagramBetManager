# InstagramBetManager

O **InstagramBetManager** é um bot desenvolvido em Python que utiliza a biblioteca `Instaloader` para coletar comentários de postagens no Instagram, extrair e validar apostas feitas nos comentários, e gerar uma tabela de classificação baseada nas apostas corretas.

## Funcionalidades

- **Login no Instagram**: Solicita o nome de usuário e a senha para fazer login no Instagram.
- **Coleta de Comentários**: Coleta os comentários das postagens especificadas em um arquivo CSV de entrada.
- **Extração de Apostas**: Identifica e extrai as apostas feitas nos comentários com base em um padrão específico.
- **Validação de Apostas**: Compara as apostas extraídas com os resultados esperados.
- **Geração de Relatórios**: Gera arquivos CSV contendo todos os dados coletados, além de uma tabela de classificação com as pontuações dos usuários.

## Requisitos

- Python 3.7 ou superior
- As seguintes bibliotecas Python:
  - `instaloader`
  - `pandas`
  - `unidecode`
  - `getpass`

Você pode instalar essas dependências executando o seguinte comando:

```bash
pip install instaloader pandas unidecode getpass
```
## Como Usar
### Clone o repositório:

```bash
git clone https://github.com/murilocapp/InstagramBetManager.git
cd InstagramBetManager
```
### Prepare o arquivo de entrada:

Crie um arquivo CSV chamado input.csv com as seguintes colunas:

- *shortcode*: O shortcode da postagem no Instagram.
- *Day*: O dia correspondente àquela postagem.
- *result*: O resultado esperado para a aposta (exemplo: "2x1 Brazil").

Exemplo de input.csv:

```csv
shortcode,Day,result
ABCD1234,1,2x1 Brazil
WXYZ5678,1,3x0 Germany
```
### Execute o script:

Você pode executar o bot de duas maneiras:

- Via Script Python: Execute o script principal main.py para iniciar o bot.

  ```bash
  python main.py
  ```
- Via Jupyter Notebook: Abra e execute o notebook InstagramBetManager.ipynb em um ambiente Jupyter. O notebook contém o mesmo código, mas é mais interativo e permite execução passo a passo.

O script e o notebook solicitarão seu nome de usuário e senha do Instagram para fazer o login.

## Monitoramento e Salvamento Automático:

O script processa todas as postagens especificadas e coleta os comentários. Em caso de erro, o progresso até o ponto do erro será salvo automaticamente em data_all_days_progress.csv.

## Resultados:

Após a execução bem-sucedida, os seguintes arquivos serão gerados:

- data_all_days.csv: Contém todos os comentários coletados e processados.
- data.csv: Contém os dados finais, incluindo as apostas extraídas e os resultados validados.
- leaderboard.csv: Contém a tabela de classificação dos usuários com base nas apostas corretas.

## Estrutura do projeto
```graphql
InstagramBetManager/
│
├── main.py                        # Script principal
├── InstagramBetManager.ipynb       # Notebook Jupyter com o código principal
├── input.csv                      # Arquivo de entrada com shortcodes e resultados esperados
├── data_all_days.csv              # Dados coletados de todas as postagens
├── data.csv                       # Dados finais após validação
├── leaderboard.csv                # Tabela de classificação
└── README.md                      # Este arquivo
```

## Considerações de Segurança
Credenciais do Instagram: O script/notebook solicita suas credenciais do Instagram para fazer o login. Certifique-se de que suas credenciais estejam seguras e evite compartilhá-las com outras pessoas.

## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença
Este projeto é licenciado sob a [MIT License](https://github.com/murilocapp/InstagramBetManager/blob/main/LICENSE).
