---
title: Construindo uma API para consumo de modelos de machine learning
date: 2020-02-15
layout: post
---

O objetivo deste post é mostrar com detalhes um dos métodos que pode ser utilizado para disponibilizarmos uma interface de consumo de modelos de machine learning. A ideia geral deste método é a criação de um modelo que após o treinamento com uma parcela dos dados, poderemos utilizar uma API REST como uma interface padrão de comunicação entre outras aplicações.

## Introdução

![Diagrama da ideia geral de criação da solução](/images/2020-02-16-api_modelos_machine_learning/diagrama_geral.png)

## Construção do modelo

A primeira coisa que temos que ter como objetivo nesta etapa é ter o modelo treinado de tal modo que possamos utilizar à qualquer momento. Tendo isso em mente podemos enumerar alguns passos que terão que ser cumpridos:

1. Obter uma base de dados;
2. Análisar a base;
3. Treinar o modelo com uma parcela do dataset;
4. Testar o modelo treinado;
5. Salvar o modelo para consumo pela API.

![Diagrama da ideia geral de criação do modelo](/images/2020-02-16-api_modelos_machine_learning/diagrama_geral_modelo.png)

### Preparando nosso ambiente de desenvolvimento

#### Bibliotecas necessárias

Serão necessárias as seguintes bibliotecas para a construção do modelo:

- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [pickle](https://docs.python.org/3/library/pickle.html)

#### Executando o notebook jupyter

Para que nosso ambiente de desenvolvimento seja comum em diversas arquiteturas de sistemas operacionais, iremos utilizar uma imagem Docker já contendo as bibliotecas necessárias, inclusive com o jupyter. A imagem docker a ser utilizada é a [jupyter/scipy-notebook](https://hub.docker.com/r/jupyter/scipy-notebook). Mais detalhes sobre esta imagem pode ser obtidos no seguinte [link](https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html).

Para ter certeza que o docker está instalado, execute o seguinte comando no terminal:

```bash
docker --version
```

Caso não tenha o Docker instalado pode acessar esse [link](https://docs.docker.com/install/) e seguir as instruções de instalação.

Agora precisamos executar a imagem para acessarmos o notebook jupyter já com todas as bibliotecas instaladas.

```bash
docker run -d -p 8080:8888 --user root -e JUPYTER_ENABLE_LAB=yes -e GRANT_SUDO=yes jupyter/scipy-notebook:414b5d749704 start-notebook.sh --NotebookApp.token=''
```

Vamos entender o comando acima:

1. **docker**: chamando a aplicação docker;
2. **run**: diz que iremos executar uma imagem instanciando um container;
3. **-d**: modo daemon, o terminal será liberado após o start do container;
4. **-p 8080:8888**: mapeamento de portas, o padrão é \<porta na sua máquina\>:\<porta do container\>, isso nos diz que acessaremos porta 8080 em localhost, porém dentro do container o jupyter está sendo executado na porta 8888;
5. **--user root**: O container será executado com o usuário root;
6. **-e JUPYTER_ENABLE_LAB=yes**: está opção define a variável de ambiente *JUPYTER_ENABLE_LAB* com o valor *yes*, ativando assim o jupyter lab;
7. **-e GRANT_SUDO=yes**: vamos permitir que comandos executados com sudo não necessitem de senha;
8. **jupyter/scipy-notebook:414b5d749704**: esta é a imagem do jupyter que iremos instanciar, o id que está após os dois pontos é a tag da imagem, isso garante que sempre iremos utilizar a mesma versão;
9. **start-notebook.sh --NotebookApp.token=''**: aqui indicamos que o script *start-notebook.sh* será usado para executar o notebook dentro do container, poderíamos ter omitido essa parte, porém não iriamos conseguir retirar a senha do notebook com o parâmetro *--NotebookApp.token=''*.

Vamos abrir o navegador no endereço <http://localhost:8080> para acessarmos o notebook jupyter.

![Jupyter Home](/images/2020-02-16-api_modelos_machine_learning/jupyter_home.png)

Agora vamos entrar na pasta work [1] e criar um novo notebook [2].

![Work folder and create notebook](/images/2020-02-16-api_modelos_machine_learning/jupyter_create_notebook.png)

### Obter a base de dados Pima

Pima Indians Diabetes Database, é um dataset contendo informações de pacientes do sexo feminino acima de 21 anos.

O dataset pode ser encontrado no site do [Kaggle](https://www.kaggle.com/uciml/pima-indians-diabetes-database) ou baixado [aqui](https://gist.github.com/jhisse/ee5d2bfbd2567caece32aaad9e867e5b).

Esse conjunto de dados irá nos permitir construirmos um modelo de machine learning que tentará prever da maneira mais acurada se um paciente tem diabete ou não.

Em uma nova célula do notebook vamos executar o seguinte comando para fazer o download da base de dados do PIMA para nosso workspace:

```bash
!wget https://gist.githubusercontent.com/jhisse/ee5d2bfbd2567caece32aaad9e867e5b/raw/pima.csv
```

O sinal de exclamação no início da execução do wget indica que o comando que vem a seguir deve ser executado como se estivesse em um terminal e não como um código Python.

![Download Pima database](/images/2020-02-16-api_modelos_machine_learning/download_pima_database.png)

### Análise dos dados

Lendo o dataset e entendendo os dados:

```python
import pandas as pd

pima_dataset = pd.read_csv('pima.csv')

pima_dataset.shape

pima_dataset.describe()

pima_dataset.head()
```

![Basic analysis](/images/2020-02-16-api_modelos_machine_learning/basic_analysis.png)

Vamos entender o que cada variável significa:

- **Pregnancies**: quantidade de vezes que esteve grávida;
- **Glucose**: nível de glicose após 2 horas do teste de intolerância à glicose;
- **BloodPressure**: Pressão arterial diastólica (mmHg);
- **SkinThickness**: Espessura da dobra de pele do tríceps (mm);
- **Insulin**: Quantidade de insulina após 2 horas do teste de intolerância à glicose;
- **BMI**: Índice de massa corporal (IMC = peso(kg)/(altura(m)*altura(m)));
- **DiabetesPedigreeFunction**: Função que retorna um score com base no histórico familiar;
- **Age**: Idade (anos);
- **Outcome**: Indicativo se a pessoa é diabética (1/0).

Vamos separar o dataset em dois conjuntos de dados, o primeiro conjunto deverá ter 70% da base, ele será usado para o treinamento de nosso modelo, os outros 30% do dataset será usado para testes.

```python
from sklearn.model_selection import train_test_split

independent_variables = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigreeFunction','Age']

x = pima_dataset[independent_variables]
y = pima_dataset['Outcome']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=1)
```

### Treinando o modelo

Nesta fase usaremos a parcela maior do nosso dataset para ajustar da melhor forma o modelo ao nossos dados. Para isso iremos utilizar o modelo linear de regressão logística da biblioteca sklearn.

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(solver='lbfgs', max_iter=1000)

result = model.fit(x_train, y_train)
```

### Testando a acurácia do modelo treinado

```python
result.score(x_test, y_test)
```

### Serialização com Pickle

Pickle é um módulo para serialização de objetos Python para sequência de bytes. Isso significa que podemos salvar objetos Python em disco em forma de arquivo, ou seja, iremos salvar a função resultante do treinamento em um arquivo com extensão pkl.

```python
import pickle

model_filename = 'finalized_model.pkl'
pickle.dump(model, open(model_filename, 'wb'))
```

Vamos carregar o modelo para efetuarmos alguns testes.

```python
loaded_model = pickle.load(open(model_filename, 'rb'))

loaded_model.predict([[6,148,72,35,0,33.6,0.627,50]])
```

## API de previsão

### Arquitetura

![Arquitetura API](/images/2020-02-16-api_modelos_machine_learning/arquitetura_api_aws.png)

### Conceitos

#### AWS API Gateway

API Gateway é um serviço gerenciado da AWS que, nesse contexto, terá como função receber os fluxos de requisições HTTP e encaminhar para as funções lambda explicadas a seguir.

Para mais informações: <https://aws.amazon.com/pt/api-gateway/>

#### AWS Lambda

Serviço gerenciado que permite executar códigos em diversas linguagens sem se preocupar com servidores.

Para mais informações: <https://aws.amazon.com/pt/lambda/>

#### AWS Simple Storage Service, S3

Serviço de armazenamento gerenciado pela AWS. Altamente escalável.

Para mais informações: <https://aws.amazon.com/pt/s3/>

#### Framework Serverless

Este ponto é de extrema importancia. Para empacotarmos nossa API de forma organizada iremos utilizar o framework Serverless. Ele irá nos ajudar a fazer o deploy para a nuvem AWS sem grande esforço.

### Configuração do AWS CLI

A primeira coisa que temos que ter em mãos é o aws cli instalado e configurado. Para isso vamos fazer o download este [link](https://aws.amazon.com/pt/cli/). Após a instalação ele deve ser configurado com suas credenciais da AWS.

```bash
aws configure
```

As credencias necessárias (Access Key e Secret Key) podem ser obtidas em sua conta AWS conforme imagem a seguir.

![Credenciais AWS](/images/2020-02-16-api_modelos_machine_learning/aws_credentials.png)

### Upload do modelo

Vamos fazer o upload do nosso modelo para um bucket S3, então antes de mais nada precisamos criar o bucket.

```bash
aws s3 mb models-$(uuidgen)
```

Utilizamos o utilitário **uuidgen** para concaternamos um identificador único ao nome, pois o nome do bucket deve ser único em toda a AWS, independente da conta.

Seguindo com a cópia do modelo para a nuvem.

```bash
aws s3 cp finalized_model.pkl s3://models-56304424-ff6e-4422-ad9c-2a1731683e44/

aws s3 ls s3://models-56304424-ff6e-4422-ad9c-2a1731683e44/
```

### Instalação

Precisamos instalar o CLI do framework Serverless.

### Ping pong

Vamos construir um endpoint para entendermos um pouco mais como toda essa estrutura funciona, para isso iremos utilizar uma chamada de api chamada ping.

Para isso teremos a seguinte estrutura de diretórios:

\- pedict-api/  
\-\- ping_handler.py  
\-\- serverless.yml

ping_handler.py

```python
import json


def ping_handler(event, context):
    body = {
        "ping": "pong"
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
```

serverless.yml

```yml
service: predict-model-api

provider:
  name: aws
  runtime: python3.8

stage: dev
region: us-east-1

functions:
  ping:
    handler: ping_handler.ping
    events:
      - http:
          path: /ping
          method: get
```

Agora vamos fazer o deploy de nossa api.

```bash
sls deploy
```

A saída será parecida com esta:

```
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service predict-model-api.zip file to S3 (2.37 KB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
.............................
Serverless: Stack update finished...
Service Information
service: predict-model-api
stage: dev
region: us-east-1
stack: predict-model-api-dev
resources: 11
api keys:
  None
endpoints:
  GET - https://sdtbeeif6d.execute-api.us-east-1.amazonaws.com/dev/ping
functions:
  ping: predict-model-api-dev-ping
layers:
  None
Serverless: Run the "serverless" command to setup monitoring, troubleshooting and testing.
```

Podemos testar nossa função de diferentes formas, a primeira é através do navegador inserindo o link que está no endpoint:

![Endpoint no browser](/images/2020-02-16-api_modelos_machine_learning/endpoint_browser.png)

Outra forma de testar é usando o próprio sls para invocar a função. Para isso vamos executar no terminal o seguinte comando:

```bash
sls invoke --function ping
```

### Endpoint de previsão

Vamos a construção do endpoint de previsão, mas antes vamos instalar um plugin no nosso sls.

Ao longo deste tutorial usamos algumas bibliotecas que fazem uso de outras libs baixo nível, ou seja, que são dependentes do sistema operacional que estamos executando nosso código. O lambda utiliza uma máquina linux de 64 bits para executar nossas funções, isso pode causar alguns tipos de erros, por exemplo, caso estejamos desenvolvendo em uma máquina Windows algumas bibliotecas terão problema de compatibilidade.

Para isso iremos utilizar o plugin [serverless-python-requirements](https://github.com/UnitedIncome/serverless-python-requirements).

```bash
sls plugin install -n serverless-python-requirements
```

