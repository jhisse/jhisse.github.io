---
title: Construindo uma API para consumo de modelos de machine learning
date: 2020-02-02
layout: post
---

O objetivo deste post é mostrar com detalhes um dos métodos que pode ser utilizado para disponibilizarmos uma interface de consumo de modelos de machine learning. A ideia geral deste método é a criação de um modelo que após o treinamento com uma parcela dos dados, poderemos utilizar uma API REST como uma interface padrão de comunicação entre outras aplicações.

## Introdução

### Etapas de construção

A primeira coisa que temos que ter como objetivo é o modelo treinado, gravado de tal modo que possamos utilizar à qualquer momento. Tendo isso em mente podemos enumerar alguns passos que terão que ser cumpridos:

1. Obter uma base de dados;
2. Análisar a base;
3. Treinar o modelo com uma parcela do dataset;
4. Testar o modelo treinado;
5. Salvar o modelo para consumo pela API.

![Diagrama da ideia geral](/images/2020-02-02-api_modelos_machine_learning/diagrama_geral.png)

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
docker run -d -p 8080:8888 -e JUPYTER_ENABLE_LAB=yes jupyter/scipy-notebook:414b5d749704 start-notebook.sh --NotebookApp.token=''
```

Vamos entender o comando acima:

1. **docker**: chamando a aplicação docker;
2. **run**: diz que iremos executar uma imagem instanciando um container;
3. **-d**: modo daemon, o terminal será liberado após o start do container;
4. **-p 8080:8888**: mapeamento de portas, o padrão é \<porta na sua máquina\>:\<porta do container\>, isso nos diz que acessaremos porta 8080 em localhost, porém dentro do container o jupyter está sendo executado na porta 8888;
5. **-e JUPYTER_ENABLE_LAB=yes**: está opção define a variável de ambiente *JUPYTER_ENABLE_LAB* com o valor *yes*, ativando assim o jupyter lab;
6. **jupyter/scipy-notebook:414b5d749704**: esta é a imagem do jupyter que iremos instanciar, o id que está após os dois pontos é a tag da imagem, isso garante que sempre iremos utilizar a mesma versão;
7. **start-notebook.sh --NotebookApp.token=''**: aqui indicamos que o script *start-notebook.sh* será usado para executar o notebook dentro do container, poderíamos ter omitido essa parte, porém não iriamos conseguir retirar a senha do notebook com o parâmetro *--NotebookApp.token=''*.

![Docker start notebook](/images/2020-02-02-api_modelos_machine_learning/docker_start_notebook.png)

Vamos abrir o navegador no endereço <http://localhost:8080> para acessarmos o notebook jupyter.

![Jupyter Home](/images/2020-02-02-api_modelos_machine_learning/jupyter_home.png)

Agora vamos entrar na pasta work [1] e criar um novo notebook [2].

![Work folder and create notebook](/images/2020-02-02-api_modelos_machine_learning/jupyter_create_notebook.png)

### Obter a base de dados Pima

Pima Indians Diabetes Database, é um dataset contendo informações de pacientes do sexo feminino acima de 21 anos.

O dataset pode ser encontrado no site do [Kaggle](https://www.kaggle.com/uciml/pima-indians-diabetes-database) ou baixado [aqui](https://gist.github.com/jhisse/ee5d2bfbd2567caece32aaad9e867e5b).

Esse conjunto de dados irá nos permitir construirmos um modelo de machine learning que tentará prever da maneira mais acurada se um paciente tem diabete ou não.

Em uma nova célula do notebook vamos executar o seguinte comando para fazer o download da base de dados do PIMA para nosso workspace:

```bash
!wget https://gist.githubusercontent.com/jhisse/ee5d2bfbd2567caece32aaad9e867e5b/raw/pima.csv
```

O sinal de exclamação no início da execução do wget indica que o comando que vem a seguir deve ser executado como se estivesse em um terminal e não como um código Python.

![Download Pima database](/images/2020-02-02-api_modelos_machine_learning/download_pima_database.png)

### Análise dos dados

Lendo o dataset e entendendo os dados:

```python
import pandas as pd

pima_dataset = pd.read_csv('pima.csv')

pima_dataset.shape

pima_dataset.describe()

pima_dataset.head()
```

![Basic analysis](/images/2020-02-02-api_modelos_machine_learning/basic_analysis.png)

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

independent_variables = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigreeFunction','Age','Outcome']

x = pima_dataset[independent_variables]
y = pima_dataset['Outcome']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=1)
```

### Serialização com Pickle

Pickle é um módulo para serialização de objetos Python em sequência de bytes. Isso significa que podemos salvar objetos Python em arquivos, ou seja, iremos salvar a função resultante do treinamento em um arquivo com extensão pkl.
