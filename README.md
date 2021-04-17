## PlmcBksAPI

PlmcBksAPI é uma API HTTP, feed RSS e catálogo OPDS escrito usando Python3 e o framework FastAPI.

## Instâncias

Veja a lista de instâncias disponíveis ou adicione a sua própria na [wiki](https://github.com/PolemicBooks/PlmcBksAPI/wiki/Instâncias).

### Características

* Possibilita a pesquisa e obtenção de informações sobre livros.
* Possibilita o download de documentos e a visualização de imagens.

### API

A API se baseia na estrutura de dados JSON e processa dados a partir de parâmetros em requisições GET e valores associados a URI.

### OPDS

O catálogo OPDS se baseia na estrutura de dados XML e processa dados a partir de parâmetros em requisições GET e valores associados a URI. A especificação atualmente seguida é o [OPDS 1.2](https://specs.opds.io/opds-1.2).

### RSS

O feed RSS se baseia na estrutura de dados XML e processa dados a partir de parâmetros em requisições GET. A especificação atualmente seguida é o [RSS 2.0](https://validator.w3.org/feed/docs/rss2.html).

### Instalação

As instruções a seguir assumem que você possui experiência com ambientes Linux e que também tem conhecimento básico sobre as APIs do Telegram.

#### Requisitos

- Sistema operacional Linux
- 200 MB de espaço em disco
- 600 MB de memória
- Python 3.6 ou superior

#### Instruções
 
 1. Comece realizando um clone deste repositório:
 
 ```bash
$ git clone --ipv4 \
    --single-branch \
    --no-tags \
    --depth '1' \
    'https://github.com/PolemicBooks/PlmcBksAPI' \
    ~/PlmcBksAPI
```

2. Instale todas as dependências necessárias:

```bash
$ cd ~/PlmcBksAPI
$ python3 scripts/setup_dependencies.py
```

3. Faça login usando sua conta no Telegram:

Isso será necessário para tornar o download de documentos e imagens através da API possível.

Para acessar a API do Telegram, você precisará de um `api_id` e um `api_hash`. Siga [estas instruções](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id) para saber como obtê-las.

```bash
$ source virtualenv/bin/activate
$ python scripts/setup_account.py -h
usage: setup_account.py [-h] --api-id API_ID --api-hash API_HASH

optional arguments:
  -h, --help           show this help message and exit
  --api-id API_ID      telegram api id
  --api-hash API_HASH  telegram api hash
```

_Apenas realize o login usando contas descartáveis. Embora as chances sejam baixas, sua conta ainda pode ser banida por abuso._

4. Inicie a aplicação

```bash
$ python application.py
```

_Leva em média 5 minutos para que a aplicação inicie._
