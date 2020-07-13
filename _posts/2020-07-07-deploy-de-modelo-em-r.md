---
title: Transformando modelo em R em produto
date: 2020-07-07
layout: post
---

O objetivo deste artigo é transformar um modelo desenvolvido em R em produto, no caso, um API Rest preditiva. Para isso vamos utilizar uma base contendo dados de pessoas diabéticas, cuja as variáveis de entradas serão pré determinadas e teremos como output uma probabilidade daquela pessoa ter ou não diabete. Vamos utilizar também a plataforma Docker para treinarmos nosso modelo com o RStudio e transformamos em container nossa API.

![Fluxo geral de deploy de modelos em R]()

## Base de dados PIMA

Vamos utilizar a Pima Indians Diabetes Database, assim como usamos neste [artigo abordando o deploy de modelos em Python]({% post_url 2020-02-16-api-modelos-machine-learning %}). A base de dados do PIMA contêm dados de pessoas do sexo feminino acima de 21 anos diabéticas ou não.

- **pregnant**: quantidade de vezes que esteve grávida;
- **glucose**: nível de glicose após 2 horas do teste de intolerância à glicose;
- **pressure**: Pressão arterial diastólica (mmHg);
- **triceps**: Espessura da dobra de pele do tríceps (mm);
- **insulin**: Quantidade de insulina após 2 horas do teste de intolerância à glicose;
- **mass**: Índice de massa corporal (IMC = peso(kg)/(altura(m)*altura(m)));
- **pedigree**: Função que retorna um score com base no histórico familiar;
- **age**: Idade (anos);
- **diabetes**: Indicativo se a pessoa é diabética (pos/neg).

As 8 primeiras variáveis serão usadas como entrada do nosso modelo preditivo e a última será nossa saída.

## Iniciando com RStudio

Para desenvolvermos nosso modelo iremos utilizar a famosa IDE para a linguagem de programação R chamada RStudio. O RStudio é uma interface de desenvolvimento baseada na web, ou seja, podemos acessá-la através do nosso navegador.

Como o foco do artigo é utilizarmos o Docker para facilitar a padronização do nosso ambiente de desenvolvimento, vamos começar por iniciar uma imagem básica já contendo nossa IDE.

```bash
docker run --rm -d -p 8787:8787 --name rstudio-pima -e DISABLE_AUTH=true rocker/rstudio:4.0.0
```

Ao acessar o navegador no endereço ```localhost:8787``` teremos acesso à interface do RStudio.

![Interface padrão do RStudio](/images/deploy-de-modelo-em-r/rstudio-interface-padrao.png)

A imagem padrão do rstudio contêm os pacotes básicos para executar nossos scripts em R, porêm como iremos trabalhar com modelos de machine learning será necessário instalar algumas bibliotecas.

É de boa prática criarmos uma imagem personalizada quando estamos utilizando o Docker para a padronização de ambientes. Por isso não iremos instalar direto na interface do RStudio que vimos anteriormente, vamos criar uma definição de imagem onde iremos executar um comando de instalação dos pacotes R que serão necessários.

Vamos parar o RStudio que iniciamos para evitarmos conflito de portas em nosso host:

```bash
docker stop rstudio-pima
```

## Personalizando uma imagem R

Como vimos mais acima, a imagem do RStudio que vamos utiliar é a [rocker/rstudio:4.0.0](https://hub.docker.com/r/rocker/rstudio/), então vamos  começar criando um diretório modelo-r para ser a nossa pasta de trabalho e dentro desta pasta vamos criar o arquivo de definição de imagem chamado ```Dockerfile```:

```Dockerfile
FROM rocker/rstudio:4.0.0
```

O arquivo de definição acima apenas cria um novo layer a partir da imagem base *rocker/rstudio:4.0.0*, porém precisamos instalar as bibliotecas mlbench, caret e suas dependências. A imagem base que estamos utilizando disponibiliza um script R que nos ajuda nessa tarefa, o nome dele é [install2.r](https://github.com/eddelbuettel/littler/blob/master/inst/examples/install2.r). Então vamos ao nosso Dockerfile:

```Dockerfile
FROM rocker/rstudio:4.0.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
                    libxml2-dev \
                    libz-dev \
    && rm -rf /var/lib/apt/lists/*

RUN install2.r -s -d TRUE --error \
               mlbench \
               caret \
               plumber

```

Vamos construir nossa imagem definindo o nome dela como *minhaimagemr*:

```bash
docker build -t minhaimagemr .
```

E após isso vamos executar nosso container novamente, só que agora com as bibliotecas e suas dependências já instaladas:

```bash
docker run --rm -d -p 8787:8787 --name rstudio-pima -e DISABLE_AUTH=true minhaimagemr
```

Observação: caso a senha seja requisitada, basta colocar "rstudio" no campo username e password.

## Desenvolvendo nosso modelo

Verificando o funcionamento de nossa imagem em *localhost:8787*, vamos criar um novo arquivo no rstuido e carregar nosso script contendo o treinamento do modelo.

![Criando um novo arquivo no RStudio](/images/deploy-de-modelo-em-r/create-new-file-in-rstudio.png)

A descrição dos comandos antecede os mesmos no código abaixo.

```r
# Biblioteca contendo o algoritimo de 
library(mlbench)

# Base de dados que iremos utilizar para treinar o modelo
data('PimaIndiansDiabetes')

# Verificando os dados que temos no dataset
head(PimaIndiansDiabetes,10)

# Dimensão de nosso dataset, número de linhas e colunas
dim(PimaIndiansDiabetes)

# Biblioteca necessária para particionar o modelo em conjunto de
# treinameto e conjunto de teste
library(caret)

# Ajusta o randomizador para reproduzirmos os mesmos resultados
set.seed(12345)

# Particiona o dataset em dois conjuntos, 80% para treinamento e 20% para teste
trainIndex <- createDataPartition(PimaIndiansDiabetes$diabetes,p=0.8,list=FALSE)

# Separa o dataset de treinamento do dataset de teste em objetos distintos
trainset <- PimaIndiansDiabetes[trainIndex,] # 80% dos dados para treinamento
testset <- PimaIndiansDiabetes[-trainIndex,] # 20% dos dados para teste

# Verifica as dimensões dos datasets
dim(trainset)
dim(testset)

# 
typeColNum <- grep('diabetes',names(PimaIndiansDiabetes))
typeColNum

# Treinar o modelo com o conjunto de treinamento
glm_model <- glm(diabetes~.,data=trainset, family=binomial)

# Verificar os coeficientes que o modelo gerou
summary(glm_model)

# Testar o modelo com o conjunto de teste
glm_prob <- predict.glm(glm_model,testset[,-typeColNum],type='response')

head(glm_prob, 10)

# 
contrasts(PimaIndiansDiabetes$diabetes)

# Efetua previsões
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

Vale destacar que ao final do nosso script iremos salvar o modelo treinando em um objeto do R. Sendo assim, poderemos efetuar o download do mesmo e utilizarmos posteriormente em outro script.

## Criando nossa api em R

Para disponibilizarmos uma interface para nosso modelo preditivo vamos criar uma API. Essa será construída com a ajuda de uma [biblioteca R chamada Plumber](https://www.rplumber.io/). A Plumber irá permitir a construção de nossa API sem que tenhamos que alterar o código R existente, precisamos apenas adicionar decorators a nossa função de predição. ([Para entender mais sobre decorators.](https://refactoring.guru/pt-br/design-patterns/decorator))

Primeiro devemos criar um novo arquivo no RStudio e carregar nosso modelo salvo anteriormente. Após o o modelo treinado estar carregado em um objeto do R, vamos definir nossa API, usando os decorators na função de previsão. Os decorators irão expandir nossa função à transformando em uma espécie de núcleo do nosso endpoint da API.

Além dos elementos descritivos do endpoint preditivo, vamos dizer que aquela função será invocada pelo [método post do protocolo http](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST) pelo decorator ```#* @post /predict``` e que o [serializador unboxedJSON]([unboxedJSON](https://www.rplumber.io/articles/rendering-output.html#boxed-vs-unboxed-json), descrito com ```#* @serializer unboxedJSON``` será o método que converte o retorno da função para um formato de saída desejado, em nosso caso, em json.

```r
# Importando a biblioteca plumber
library(plumber)

# Carregamento do modelo para um objeto
glm_model <- readRDS("./glm_model.rds")

#* @param pregnant:numeric quantidade de vezes que esteve grávida
#* @param glucose:numeric nível de glicose após 2 horas do teste de intolerância à glicose
#* @param pressure:numeric pressão arterial diastólica (mmHg)
#* @param triceps:numeric espessura da dobra de pele do tríceps (mm)
#* @param insulin:numeric quantidade de insulina após 2 horas do teste de intolerância à glicose
#* @param mass:numeric índice de massa corporal (IMC = peso(kg)/(altura(m)*altura(m)))
#* @param pedigree:numeric função que retorna um score com base no histórico familiar
#* @param age:numeric idade (anos)
#* @post /predict
#* @serializer unboxedJSON
function(pregnant, glucose, pressure, triceps, insulin, mass, pedigree, age)
{
  df <- data.frame(
    pregnant = as.numeric(pregnant),
    glucose = as.numeric(glucose),
    pressure = as.numeric(pressure),
    triceps = as.numeric(triceps),
    insulin = as.numeric(insulin),
    mass = as.numeric(mass),
    pedigree = as.numeric(pedigree),
    age = as.numeric(age)
  )
  output <- list(prob = predict.glm(glm_model, df, type='response'))
  return(output)
}
```

Podemos executar nossa API no próprio RStudio, assim teremos um ambiente de testes antes de empacotarmos em uma imagem Docker. Para isso vamos clicar no símbolo de play verde no canto superior direito do RStudio e uma nova janela irá se abrir.

![Iniciar API](/images/deploy-de-modelo-em-r/rstudio_run_plumber.png)

Na janela que foi aberta quando demos início a nossa API irá aparecer uma interface do Swagger. [O Swagger é um utilitário que permite documentar nossa aplicação de forma amigável para o usuário](https://swagger.io/). Graças ao pacote plumber, teremos essa interface já implementada.

![Interface do swagger](/images/deploy-de-modelo-em-r/interface-do-swagger.png)

Na interface principal do Swagger podemos inserir valores de testes e verificarmos o resultado, como no exemplo a seguir.

![Exemplo de chamada no Swagger](/images/deploy-de-modelo-em-r/exemplo-swagger.png)

## Empacotando a API preditiva


