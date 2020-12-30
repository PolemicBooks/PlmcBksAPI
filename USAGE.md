## Uso

A API atualmente pode ser usada de 3 formas:

1. Obtenção de informações sobre livros.
2. Buscas com base no título, categoria e entre outros.
3. Download de documentos e imagens.

### Obtenção de informações sobre livros

Você baixar os arquivos contendo informações sobre todos os livros já publicados no canal em:

- https://api.polemicnews.com/dumps

Nós disponibilizamos essas informações nos formatos `json`, `csv` e `xlsx`. Eles também serão atualizados sempre que houver algum novo conteúdo no canal.

### Buscas com base no título, categoria e entre outros

Você pode utilizar os seguintes métodos para buscar informações sobre livros:

- `/s/title`
- `/s/author`
- `/s/publisher`
- `/s/narrator`
- `/s/type`
- `/s/category`

Os métodos são alto descritíveis.

- O método `/s/title` retornará livros em que o termo enviado corresponda ao título da obra.
- O método `/s/author` retornará livros em que o termo enviado corresponda ao autor da obra.
- O método `/s/publisher` retornará livros em que o termo enviado corresponda a editora que realizou a publicação da obra.

#### Exemplos

**_Pesquisando por livros que possuam em seus títulos o termo `Python`:_**

Requisição:

```bash
curl --url "https://api.polemicnews.com/s/title" \
    --data-urlencode "query=Python" \
    --data-urlencode "max_results=1" \
    --get
```

Resposta:

```json
{
  "pagination": {
    "total_pages": 20,
    "remaining_pages": 19,
    "previous_page": null,
    "current_page": 0,
    "next_page": 1
  },
  "results": {
    "total_results": 20,
    "max_results": 1,
    "results": [
      {
        "id": 17622,
        "title": "A História (quase) Definitiva De Monty Python: Cinco Britânicos E Um Americano Que Reinventaram O Nonsense E Viraram O Mundo De Ponta-cabeça",
        "type": "Ebook",
        "category": "Biografias",
        "duration": {
          "seconds": null,
          "human": null
        },
        "size": {
          "bytes": 2374401,
          "human": "2.26 MB"
        },
        "author": "Thiago Meister Carneiro",
        "narrator": null,
        "publisher": "Viseu",
        "views": 23,
        "location": "/l/17622",
        "photo": {
          "id": 17622,
          "kind": "cover",
          "date": {
            "epoch": 1606345931,
            "human": "Wed, 25 Nov 2020 20:12:11 GMT"
          },
          "file_extension": "jpeg",
          "file_id": "AgACAgQAAx0CVZ8qrQACRNZf61a_04SdJXUT24LTgc18iUsXAAPhqzEbnvr8UR6th3-qTNo0-dSpJ10AAwEAAwIAA3gAA_ewAgABHgQ",
          "file_name": "A História (quase) Definitiva De Monty Python: Cinco Britânicos E Um Americano Que Reinventaram O Nonsense E Viraram O Mundo De Ponta-cabeça.jpeg",
          "file_size": {
            "bytes": 62796,
            "human": "61.32 KB"
          },
          "file_unique_id": "AQAD-dSpJ10AA_ewAgAB",
          "mime_type": "image/jpeg",
          "resolution": {
            "height": 600,
            "width": 400
          },
          "downloadable": true,
          "location": "/l/17622",
          "download": "/d/17622"
        },
        "documents": [
          {
            "id": 17623,
            "kind": "ebook",
            "date": {
              "epoch": 1606345936,
              "human": "Wed, 25 Nov 2020 20:12:16 GMT"
            },
            "file_extension": "epub",
            "file_id": "BQACAgEAAx0CVZ8qrQACRNdf61bAENufp2xovRI5kiW_tcYO1QACMwgAAt2E-UVcdnYjcZP71B4E",
            "file_name": "A História quase Definitiva De Monty Python: Cinco Britânicos E.epub",
            "file_size": {
              "bytes": 2374401,
              "human": "2.26 MB"
            },
            "file_unique_id": "AgADMwgAAt2E-UU",
            "mime_type": "application/epub+zip",
            "views": 25,
            "downloadable": true,
            "location": "/l/17623",
            "download": "/d/17623"
          }
        ]
      }
    ]
  }
}
```

**_Pesquisando por livros que foram escritos pelo autor `Charles Darwin`:_**

Requisição:

```bash
curl --url "https://api.polemicnews.com/s/author" \
    --data-urlencode "query=Charles Darwin" \
    --data-urlencode "max_results=1" \
    --get
```

Resposta:

```json
{
  "pagination": {
    "total_pages": 11,
    "remaining_pages": 10,
    "previous_page": null,
    "current_page": 0,
    "next_page": 1
  },
  "results": {
    "total_results": 11,
    "max_results": 1,
    "results": [
      {
        "id": 1593,
        "title": "A Origem Das Espécies",
        "type": "Ebook",
        "category": "Ciência",
        "duration": {
          "seconds": null,
          "human": null
        },
        "size": {
          "bytes": 571645,
          "human": "558.25 KB"
        },
        "author": "Charles Darwin",
        "narrator": null,
        "publisher": "FV Éditions",
        "views": 8,
        "location": "/l/1593",
        "photo": {
          "id": 1593,
          "kind": "cover",
          "date": {
            "epoch": 1603935059,
            "human": "Wed, 28 Oct 2020 22:30:59 GMT"
          },
          "file_extension": "jpeg",
          "file_id": "AgACAgQAAx0CVZ8qrQACBjlf60_TrBWAf_BqjG3KEYtYjZJ2MAACxKsxG9WF1VCMde1_zsEmdqQj2SddAAMBAAMCAAN4AAMYuQEAAR4E",
          "file_name": "A Origem Das Espécies.jpeg",
          "file_size": {
            "bytes": 32878,
            "human": "32.11 KB"
          },
          "file_unique_id": "AQADpCPZJ10AAxi5AQAB",
          "mime_type": "image/jpeg",
          "resolution": {
            "height": 600,
            "width": 400
          },
          "downloadable": true,
          "location": "/l/1593",
          "download": "/d/1593"
        },
        "documents": [
          {
            "id": 1594,
            "kind": "ebook",
            "date": {
              "epoch": 1603935076,
              "human": "Wed, 28 Oct 2020 22:31:16 GMT"
            },
            "file_extension": "epub",
            "file_id": "BQACAgEAAx0CVZ8qrQACBjpf60_TGoDiVoEAAeYqGEIcYZbgwxIAAqYCAAKzd9BE65yCINWKUEceBA",
            "file_name": "A Origem Das Espécies.epub",
            "file_size": {
              "bytes": 571645,
              "human": "558.25 KB"
            },
            "file_unique_id": "AgADpgIAArN30EQ",
            "mime_type": "application/epub+zip",
            "views": 7,
            "downloadable": true,
            "location": "/l/1594",
            "download": "/d/1594"
          }
        ]
      }
    ]
  }
}
```

**_Pesquisando por livros que foram publicados pela editora `Ubook`:_**

Requisição:

```bash
curl --url "https://api.polemicnews.com/s/publisher" \
    --data-urlencode "query=Ubook" \
    --data-urlencode "max_results=1" \
    --get
```

Resposta:

```json
{
  "pagination": {
    "total_pages": 507,
    "remaining_pages": 506,
    "previous_page": null,
    "current_page": 0,
    "next_page": 1
  },
  "results": {
    "total_results": 507,
    "max_results": 1,
    "results": [
      {
        "id": 827,
        "title": "Maradona - O Garoto de Ouro",
        "type": "Audiobook",
        "category": "Biografias",
        "duration": {
          "seconds": 3349,
          "human": "0 hora(s), 55 minuto(s) e 49 segundo(s)"
        },
        "size": {
          "bytes": 21779592,
          "human": "20.77 MB"
        },
        "author": "Independente",
        "narrator": "Bernardo Vieira",
        "publisher": "Ubook",
        "views": 7,
        "location": "/l/827",
        "photo": {
          "id": 827,
          "kind": "cover",
          "date": {
            "epoch": 1603921189,
            "human": "Wed, 28 Oct 2020 18:39:49 GMT"
          },
          "file_extension": "jpeg",
          "file_id": "AgACAgQAAx0CVZ8qrQACAztf609_SsS11LZp_OyH76ZJ2oe21wACt6sxG0G11FA_WfmG6-jI0yKIySZdAAMBAAMCAAN4AAPE6AEAAR4E",
          "file_name": "Maradona - O Garoto de Ouro.jpeg",
          "file_size": {
            "bytes": 41485,
            "human": "40.51 KB"
          },
          "file_unique_id": "AQADIojJJl0AA8ToAQAB",
          "mime_type": "image/jpeg",
          "resolution": {
            "height": 600,
            "width": 400
          },
          "downloadable": true,
          "location": "/l/827",
          "download": "/d/827"
        },
        "documents": [
          {
            "id": 828,
            "kind": "audiobook",
            "date": {
              "epoch": 1603921200,
              "human": "Wed, 28 Oct 2020 18:40:00 GMT"
            },
            "file_extension": "zip",
            "file_id": "BQACAgEAAx0CVZ8qrQACAzxf60-Azb8QIoZ_eaBmMxgDDfhVhAACIgEAArN30ERU7fIoPfS5eR4E",
            "file_name": "Maradona - O Garoto de Ouro.zip",
            "file_size": {
              "bytes": 21779592,
              "human": "20.77 MB"
            },
            "file_unique_id": "AgADIgEAArN30EQ",
            "mime_type": "application/zip",
            "views": 8,
            "downloadable": false,
            "location": "/l/828",
            "download": null
          }
        ]
      }
    ]
  }
}
```

#### Parâmetros

Cada um dos métodos citados anteriormente suportam os 3 seguintes parâmetros: `query`, `page` e `max_results`.

- O `query` deve receber um termo que será usado como base pra realizar a busca.
- O `page` é usado para controlar a paginação. O valor dele deve ser sempre um número igual ou superior a zero e igual ou inferior ao valor da chave `total_pages`. Quando não presente na requisição, seu valor padrão é `0`.
- O `max_results` é usado para controlar a quantidade máxima de resultados retornados. O valor dele deve sempre ser superior a zero. Quando não presente na requisição, seu valor padrão é `15`.

Você pode obter uma lista contendo todos os autores, editoras, tipos e categorias disponíveis usando os seguintes métodos:

- `/g/authors`
- `/g/publishers`
- `/g/narrators`
- `/g/types`
- `/g/categories`

### Download de documentos e imagens

_**Nota**: Devido as limitações impostas pela propia API de bots, só é realizar o download de arquivos de no máximo 20 MB._

O método utilizado para o download de imagens ou documentos é o `/d/`.

#### Exemplos

Requisição:

```bash
curl --url "https://api.polemicnews.com/d/116308" \
    --verbose
```

A identificação numérica após o `/d/` é o ID da mensagem enviada no canal do Telegram. 

> Se a mensagem for uma foto ou foto com legenda, um imagem será retornada. Se a mensagem for um documento, um arquivo será retornado.
