---
title: Construindo uma API para consumo de modelos de machine learning (Continuação)
date: 2020-02-28
layout: post
---

Este post é complementar ao anterior, disponível [aqui]({% post_url 2020-02-16-api_modelos_machine_learning %}). No primeiro vimos como construir modelos de machine learning e salvá-los como pickle, em seguida vimos como construir uma API serverless nativa na AWS. O objetivo deste é utilizamos o mesmo modelo salvo anteriormente e criamos uma API agnóstica com container, o que isso significa é que poderemos executar nossa API em qualquer ambiente em que o Docker esteja disponível.

## Falcon API

Vamos contar com a ajuda de um framework web chamado [Falcon](https://falcon.readthedocs.io).

## Preparação do ambiente

Vamos criar a seguinte estrutura de diretórios:

\- predict-api/  
\-\- app/

Dentro da pasta predict-api vamos inicializar nosso virtual environment e instalar a biblioteca do framework Falcon.

```bash
cd predict-api

pip install --user virtualenv

virtualenv venv

source venv/bin/activate

pip install falcon
```

## Ping Pong

Vamos criar oo arquivo que irá conter o método de inicialização da api.

app/app.py

```python
import falcon

from ping_handler import Ping


def create_api():
    api = falcon.API()

    # Routes
    api.add_route('/ping', Ping())

    return api


# Init app
app = create_api()

if __name__ == '__main__':
    from wsgiref import simple_server

    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()

```

Agora vamos criar a classe Ping. Essa classe terá o método **on_get** que irá receber a requisição http e irá responder um simples json.

app/ping_handler.py

```python
class Ping:
    def on_get(self, req, resp):
        resp.media = {"ping": "pong"}

```

O método **on_get** indica que quando a api receber uma ação de GET, esse método será executado. Para mais detalhes consulte a [documentação](https://falcon.readthedocs.io/en/stable/user/tutorial.html#creating-resources)

Agora vamos gerar nosso requirements.txt

```bash
pip freeze > app/requirements.txt
```

## Preparando o container

Vamos preparar nosso Dockerfile para instalar as bibliotecas necessárias para nosso projeto.

Dockerfile

```dockerfile
FROM python:3.8-slim

WORKDIR /api

ADD app/ .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "python", "app.py" ]
```

Nossa estrutura final de diretórios está da seguinte maneira:

\- predict-api/  
\-\- app/  
\-\-\- app.py  
\-\-\- ping_handler.py  
\-\-\- requirements.txt  
\-\- Dockerfile  

Para executarmos o container precisamos fazer o build da imagem e depois instanciá-la. Para isso, no diretório **predict-api** vamos executar os seguintes comandos no terminal:

```bash
docker build -t predict-api:latest .

docker run --rm -p 8000:8000 predict-api:latest
```

No comando de build não se esqueça do ponto ao final, esse ponto indica o contexto de onde o Dockerfile se encontra.

Vamos acessar o endereço <http://localhost:8000> e ver nosso endpoint ping funcionando. Como alternativa podemos executar o seguinte comando no terminal:

```bash
curl -w "\n" -X GET http://localhost:8000/ping
```

## Endpoint de previsão

Nessa etapa vamos criar o endpoint de previsão. Para isso precisamos do nosso modelo salvo em pickle, caso não tenha, basta seguir os primeiros passos do [post anterior]({% post_url 2020-02-16-api_modelos_machine_learning %}).

Vamos colocar o arquivo finalized_model.pkl no diretório **app** e criar um método para efetuar uma previsão com base em uma entrada de dados.

Antes de mais nada vamos adicionar as bibliotecas necessárias para executar a previsão.

```bash
pip install scikit-learn

pip freeze > app/requirements.txt
```

app/predict_handler.py

```python
import json
import falcon
import pickle
from sklearn.linear_model import LogisticRegression


class Predict(object):
    def on_post(self, req, resp):
        raw_body = req.bounded_stream.read()
        body_data = json.loads(raw_body, encoding='utf-8')

        pregnancies = body_data.get('pregnancies')
        glucose = body_data.get('glucose')
        blood_pressure = body_data.get('blood_pressure')
        skin_thickness = body_data.get('skin_thickness')
        insulin = body_data.get('insulin')
        bmi = body_data.get('bmi')
        diabetes_pedigree_function = body_data.get('diabetes_pedigree_function')
        age = body_data.get('age')

        loaded_model = pickle.load(open('finalized_model.pkl', 'rb'))

        result = int(loaded_model.predict([[
            pregnancies,
            glucose,
            blood_pressure,
            skin_thickness,
            insulin,
            bmi,
            diabetes_pedigree_function,
            age
        ]])[0])

        resp.media = {"outcome": result}
        resp.status = falcon.HTTP_200

```

A variável **body_data** irá carregar nosso payload, ou seja, nossos dados de entrada que serão necessários para a previsão.

Precisamos agora adicionar uma nova rota na api.

app/app.py

```python
import falcon

from ping_handler import Ping
from predict_handler import Predict


def create_api():
    api = falcon.API()

    # Routes
    api.add_route('/ping', Ping())
    api.add_route('/predict', Predict())

    return api


# Init app
app = create_api()

if __name__ == '__main__':
    from wsgiref import simple_server

    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()

```

A estrutura final de diretórios ficará da seguinte forma:

\- predict-api/  
\-\- app/  
\-\-\- app.py  
\-\-\- ping_handler.py  
\-\-\- predict_handler.py  
\-\-\- finalized_model.pkl  
\-\-\- requirements.txt  
\-\- Dockerfile  

Vamos agora fazer o build da imagem novcamente e testar o endpoint de previsão usando o curl na linha de comando:

```bash
docker build -t predict-api:latest .

docker run -d --rm -p 8000:8000 predict-api:latest

curl -w '\n' -X POST http://localhost:8000/predict -d '{ "pregnancies": 2, "glucose": 148, "blood_pressure": 72, "skin_thickness": 35, "insulin": 0, "bmi": 33.6, "diabetes_pedigree_function": 0.674, "age": 22 }'
```

O código completo pode ser encontrado [nesse repositório](https://github.com/jhisse/api-machine-learning-container)
