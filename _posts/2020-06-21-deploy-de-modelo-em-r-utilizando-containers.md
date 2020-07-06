---
title: Deploy de modelo em R utilizando containers
date: 2020-06-21
layout: post
---

O objetivo deste artigo é transformar um modelo desenvolvido em R em produto, no caso, um API Rest preditiva. Para isso vamos utilizar uma base contendo dados de pessoas diabéticas, cuja as variáveis de entradas serão pré determinadas e nossa saída é um indicativo de verdadeiro ou falso. Vamos utilizar também a plataforma Docker para treinarmos nosso modelo com o RStudio.

[Imagem]

## Base de dados PIMA

A base de dados do PIMA contêm dados de pessoas diabéticas ou não.

- **Pregnancies**: quantidade de vezes que esteve grávida;
- **Glucose**: nível de glicose após 2 horas do teste de intolerância à glicose;
- **BloodPressure**: Pressão arterial diastólica (mmHg);
- **SkinThickness**: Espessura da dobra de pele do tríceps (mm);
- **Insulin**: Quantidade de insulina após 2 horas do teste de intolerância à glicose;
- **BMI**: Índice de massa corporal (IMC = peso(kg)/(altura(m)*altura(m)));
- **DiabetesPedigreeFunction**: Função que retorna um score com base no histórico familiar;
- **Age**: Idade (anos);
- **Outcome**: Indicativo se a pessoa é diabética (1/0).

As 8 primeiras variáveis serão usadas como entrada do nosso modelo preditivo e a última será nossa saída.

## Iniciando com RStudio

Para desenvolvermos nosso modelo iremos utilizar a famosa IDE para a linguagem de programação R chamada RStudio. O RStudio é uma interface de desenvolvimento baseada na web, ou seja, podemos acessá-la através do nosso navegador.

Como o foco do artigo é utilizarmos o Docker para facilitar a padronização do nosso ambiente de desenvolvimento, vamos começar por iniciar uma imagem básica já contendo nossa IDE.

```bash
docker run -d -p 8787:8787 -e DISABLE_AUTH=true rocker/rstudio:4.0.0
```

Ao acessar o navegador no endereço ```localhost:8787``` teremos acesso à interface do RStudio.

[IMAGEM RSTUDIO]

## Personalizando uma imagem R

Como iremos treinar um modelo de previsão precisamos de algumas bibliotecas para machine learning. Poderíamos instalar direto via o console do RStudio, porém uma boa prática é criarmos nossa imagem Docker personalizada que contêm as bibliotecas necessárias para o treinamento do modelo.

Como vimos mais acima, a imagem do RStudio que vamos utiliar é a ```rocker/rstudio:4.0.0```, então vamos iniciar nosso arquivo de definição de imagem:

```Dockerfile
FROM rocker/rstudio:4.0.0
```

Precisamos instalar as bibliotecas mlbench, caret e suas dependências. A nossa imagem base disponibiliza um script R que nos ajuda nessa tarefa, o nome dele é install2.r. Então vamos ao nosso Dockerfile:

```Dockerfile
FROM rocker/rstudio:4.0.0

RUN apt-get install -y libxml2-dev libz-dev

RUN install2.r -s -d TRUE --error \
               mlbench \
               caret \
               plumber
```

Vamos construir nossa imagem:

```bash
docker build -t minhaimagemr:v1 .
```

E após isso vamos executar nosso container novamente, só que agora com as bibliotecas e suas dependências já instaladas:

```bash
docker run -d -p 8787:8787 -e DISABLE_AUTH=true minhaimagemr:v1
```

## Desenvolvendo nosso modelo

```r
# Biblioteca contendo o algoritimo de 
library(mlbench)

# Base de dados que iremos utilizar para treinar o modelo
data('PimaIndiansDiabetes')


head(PimaIndiansDiabetes,10)

dim(PimaIndiansDiabetes)

library(caret) #this package has the createDataPartition function

# Randomiza a base de dados
set.seed(123)

# Particiona o dataset em dois conjuntos, para treinamento e para teste
trainIndex <- createDataPartition(PimaIndiansDiabetes$diabetes,p=0.8,list=FALSE)

# Separa o dataset de treinamento do dataset de teste em objetos distintos
trainset <- PimaIndiansDiabetes[trainIndex,] # 80% dos dados
testset <- PimaIndiansDiabetes[-trainIndex,] # 20% dos dados

# Verifica as dimensões dos datasets
dim(trainset)
dim(testset)

#get column index of predicted variable in dataset
typeColNum <- grep('diabetes',names(PimaIndiansDiabetes))

typeColNum

#build model
glm_model <- glm(diabetes~.,data = trainset, family = binomial)

summary(glm_model)

#predict probabilities on testset
#type=”response” gives probabilities, type=”class” gives class
glm_prob <- predict.glm(glm_model,testset[,-typeColNum],type='response')

head(glm_prob, 10)

#which classes do these probabilities refer to? What are 1 and 0?
contrasts(PimaIndiansDiabetes$diabetes)

#make predictions
##…first create vector to hold predictions (we know 0 refers to neg now)
glm_predict <- rep('neg',nrow(testset))
glm_predict[glm_prob>.5] <- 'pos'

head(glm_predict, 10)

# Matrix de colizão
table(pred=glm_predict,true=testset$diabetes)

# Acurácia do modelo
mean(glm_predict==testset$diabetes)

# Salvar o modelo para uso da API
saveRDS(glm_model, "./glm_model.rds")
```

## Criando nossa api em R

Para disponibilizarmos uma interface para nosso modelo preditivo vamos criar uma API. Essa API será construída com a ajuda de uma biblioteca chamada Plumber.

Primeiro devemos criar um novo arquivo e carregar nosso modelo salvo anteriormente.

````r
library(mlbench)
library(caret)
library(plumber)

glm_predict <- readRDS("./glm_model.rds")


```