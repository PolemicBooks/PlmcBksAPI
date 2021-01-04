### Instalação

_**Nota**: Você precisará de um sistema operacional Linux e pelo menos o Python 3.5 para isso._

Instale todas as dependências necessárias:

```bash
apt-get --assume-yes install \
    'python3' \
    'python3-pip' \
    'python3-setuptools'
    'python3-wheel' \
    'git'
```

Crie um novo usuário:

```bash
adduser --shell '/bin/bash' \
    --disabled-login \
    'pbapi'

sudo -i --user='pbapi'
```

Clone este repositório

```bash
git clone --ipv4 \
    --single-branch \
    --no-tags \
    --depth '1' \
    'https://github.com/SnwMds/PolemicBooksAPI' \
    'pbapi'
```

Instale todas as bibliotecas de código necessárias:

```bash
python3 -m pip install --force-reinstall \
    --disable-pip-version-check \
    --no-warn-script-location \
    --user \
    --upgrade \
    'setuptools' \
    'wheel' \
    'testresources' \
    'virtualenv' \
    'pip'
```

Crie um ambiente virtual:

```bash
python3 -m virtualenv --download \
    --no-periodic-update \
    "${HOME}/pbapi/venv"

source "${HOME}/pbapi/venv/bin/activate"
```

Instale as dependências no ambiente virtual:

```bash
pip install --force-reinstall \
    --disable-pip-version-check \
    --no-warn-script-location \
    --upgrade \
    'flask' \
    'gunicorn' \
    'pyrogram' \
    'tgcrypto' \
    'pandas' \
    'pytelegrambotapi' \
    'unidecode'
```

Inicie o servidor HTTP:

```bash
cd "${HOME}/pbapi"

"${PWD}/venv/bin/gunicorn" \
    --workers '1' \
    --bind '127.0.0.1:35678' \
    'wsgi:app'
```

Agora você possui uma instância executando em `http://127.0.0.1:35678/`.
