---
title: Verificando vulnerabilidades em containers com Trivy e Gitlab CI/CD
date: 2020-05-22
layout: post
---

Neste artigo vamos criar uma API na linguagem golang, armazenar o código fonte em um repositório do Gitlab e construir um pipeline de continuous integration para build, teste de vulnerabilidade e push para o docker registry. Ao final teremos o fluxo de continuous integration de uma aplicação, desde o código fonte até a disponibilização da imagem docker em um container registry.

## Entendendo o plano

![Diagrama](/images/2020-05-22-verificando-vulnerabilidades-em-containers-com-trivy-e-gitlab-ci-cd/visao_geral.png)

O primeiro passo é construir uma simples API REST que na rota ```/ping``` irá responder com uma simples mensagem. Escolhemos a linguagem [Go](https://golang.org/), pois é compilada, com isso podemos explorar dois estágios, o de compilação e o estágio de execução. Essa característica irá permitir que possamos utilizar diferentes técnicas na criação de nossas imagens docker e analisar os ganhos que temos ao adotar determinada abordagem em relação a tamanho e segurança.

No processo de desenvolvimento da API é de boa prática realizarmos commits no repositório git conforme avançamos em nosso código, ou seja, um local onde é possível versionar de forma eficiente nosso código, para isso vamos utilizar o Gitlab.

O [GitLab](https://gitlab.com/) se denomina uma "plataforma completa de DevOps". Suas features são realmente diferenciadas, gerenciamento, planejamento, segurança,release, entre outras.

Vamos manter em mente que o objetivo do artigo é utilizarmos a ferramenta [Trivy](https://github.com/aquasecurity/trivy) para identificarmos vulnerabilidades em nossas imagens docker, como falhas de segurança em pacotes do sistema operacional e dependências de aplicações. Então, o foco está no processo de continuous integration, onde irá acontecer o scanner automático. Porém, para termos esse processo de automatização, vamos utilizar a feature de [CI/CD do Gitlab](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/) que abrange tanto continuous integration, quanto continuous delivery e continuous deployment. No nosso caso vamos explorar somente o primeiro.

## Construindo nossa API

Neste artigo vamos criar uma API que será executada dentro de nosso container. Para isso, vamos utilizar o framework [Gin](https://github.com/gin-gonic/gin) para nos auxiliar a construção de uma simples API Rest.

Não iremos descrever com detalhes o código, mas precisamos saber alguns detalhes. O arquivo ```go.mod``` corresponde ao gerenciador de dependências do go, ou seja, os módulos necessários para buildar nossa aplicação estão descritos nele e que o arquivo ```main.go``` corresponde à nossa aplicação principal.

No ```main.go``` temos:

```golang
package main

import "github.com/gin-gonic/gin"
import "net/http"

var (
    r  *gin.Engine
)

func main() {
    r = gin.Default()
    r.GET("/ping", ping)
    r.Run()
}

func ping(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
        "status": http.StatusOK,
        "message": "pong",
    })
}
```

As dependências necessárias em ```go.mod```:

```golang
module SimpleApi

go 1.12

require github.com/gin-gonic/gin v1.6.3
```

## Preparando a primeira versão do Dockerfile

O Dockerfile é o arquivo que irá conter nossas instruções para a criação da imagem docker final. Algumas boas práticas de construção deste arquivo são:

- Sempre utilizar uma tag especifíca quando fizer referência a outra imagem (linha 1)
- Usar o label maintainer para identificar os responsáveis por aquela imagem (linha 3)
- Instalar somente o necessário para que a aplicação seja executada
- Nunca executar seu processo com o usuário root do container (linha 17)

```Dockerfile
FROM golang:1.12

LABEL maintainer="José Hisse"

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY main.go .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

ENV GIN_MODE release

USER 1000:1000

EXPOSE 8080

CMD ["./main"]
```

Podemos observar acima que o processo de build e execução da nossa API estão em um mesmo container. Isso é prejudicial a segurança de nossa aplicação, pois temos um excesso de pacotes e depencias necessários somente até gerarmos nosso executável, após o build podemos executar a aplicação em qualquer sistema com a mesma arquitetura.

Até o momento temos a seguinte estrutura de diretórios:

\- SimpleApi/  
\-\- Dockerfile
\-\- go.mod
\-\- main.go

## Gitlab CI/CD

```yaml
image: docker:stable

# Jobs para build e scan com o trivy
stages:
  - build
  - scan
  - push

# Serviços acessíveis pelos jobs
# Precisamos do dind, docker in docker para buildar nossa imagem
services:
  - docker:dind

variables:
  # Nome da imagem e a tag
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  # Variáveis para acessar o serviço do dind
  DOCKER_HOST: tcp://docker:2375/
  DOCKER_TLS_CERTDIR: ""

# Permite que possamos usar um arquivo ou diretório em múltiplos jobs
cache:
  key: "$CI_COMMIT_REF_NAME"
  paths:
    - image.tar

build:
  stage: build
  script:
    - docker build -t $IMAGE .
  # Salva a imagem docker em um pacote tar
  after_script:
    - docker save $IMAGE -o image.tar

scan:
  stage: scan
  image:
    name: aquasec/trivy:latest
    # Sobresceve entrypoint da imagem
    entrypoint: [""]
  variables:
    GIT_STRATEGY: none
    TRIVY_NO_PROGRESS: "true"
    # Variáveis de ambiente para que o trivy possa acessar o registry do gitlab
    TRIVY_USERNAME: "$CI_REGISTRY_USER"
    TRIVY_PASSWORD: "$CI_REGISTRY_PASSWORD"
    TRIVY_AUTH_URL: "$CI_REGISTRY"
  # Vamos scannear o container por vulnerabilidades de vários graus de severidade,
  # porém se for encontrada alguma critica o pipeline irá falhar
  script:
    - trivy image --severity UNKNOWN,LOW,MEDIUM,HIGH -i image.tar
    - trivy image --severity CRITICAL --exit-code 1 -i image.tar

push:
  stage: push
  # Carrega a imagem a partir do pacote tar e em seguida faz login no registry do GitLab
  before_script:
    - docker load -i image.tar
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
  # Se tudo ocorreu bem por aqui, será feito o push da imagem docker
  script:
    - docker push $IMAGE

```

Após o commit do ```.gitlab-ci.yml``` o processo de continuous integration iniciará no GitLab, onde pode ser verificado no link lateral, em "CI/CD".

![menu Lateral](/images/2020-05-22-verificando-vulnerabilidades-em-containers-com-trivy-e-gitlab-ci-cd/menu_lateral.png)

O pipeline consiste na execução de três jobs. O primeiro é responsável pelo build da imagem. Vale um ponto de atenção aqui, para que possamos utilizar um diretório ou um arquivo entre um job e outro, é necessário termos um local para cache pré-definido (linha 22). 

No segundo estágio é onde o Trivy executará o scanner em busca de vulnerabilidades conhecidas. Caso o scanner não identifique vulnerabilidade critica então será executado o terceiro estágio, que consiste no push da imagem para o registry. O GitLab possui um registry em seu leque de ferramentas.

![Pipeline no gitlab](/images/2020-05-22-verificando-vulnerabilidades-em-containers-com-trivy-e-gitlab-ci-cd/pipeline.png)

Agora vamos aos resultados da nossa primeira verificação de vulnerabilidades, para isso clique em "CI/CD" e em seguida em "Tarefas".

![Menu de tasks](/images/2020-05-22-verificando-vulnerabilidades-em-containers-com-trivy-e-gitlab-ci-cd/scan_task.png)

Ao identificar a task referente ao scan, vamos acessar os logs. Lembrando que o pipeline só irá falhar se encontrar uma vulnerabilidade critíca, no log as demais vulnerabilidade serão listadas, mas a task não falhará. Adiantando que nossa aplicação de exemplo não terá vulnerabilidades critícas, então ele não deve falhar em situações normais. Vamos focar em analizar a quantidade de vulnerabilidades de graus severidade abaixo de critico.

![Resultado da primeira abordagem](/images/2020-05-22-verificando-vulnerabilidades-em-containers-com-trivy-e-gitlab-ci-cd/resultado1_geral.png)

Observamos um número elevado em falhas de segurança. 

Vamos à outra observação, o tamanho da imagem final.

![Size da primeira abordagem](/images/2020-05-22-verificando-vulnerabilidades-em-containers-com-trivy-e-gitlab-ci-cd/resultado1_size.png)

Será que podemos melhorar nossos números? Atingir um nível de zero ou próximo de 0 no número de vulnerabilidades é nosso objetivo e se, além disso, pudermos abaixar o o tamanho da imagem final?

## Melhorando a segurança com multi-stage build

Uma técnica muito interessante é separarmos nosso Dockerfile em duas parte. A primeira será usada para build e a segunda será onde nossa aplicação será executada. Isso diminui as dependências que o container carrega consigo, já que a imagem final conterá apenas o básico, sem todas as ferramentas necessárias para a compilação.

No Dockerfile abaixo podemos ver essa divisão claramente pela tag FROM. A primeira imagem temos todas as ferramentas necessárias para compilar a nossa aplicação em Go, ou seja, aqui vamos executar o build e gerar um único arquivo executável. Usamos como alias o nome ```builder``` que fazemos referência no segundo estágio, o estágio de execução.

No estágio da execução usamos como imagem base uma imagem mínima do alpine linux. Em seguida copiamos o executável já compilado, para dentro do container contendo o alpine, ou seja, nossa imagem final já não terá todas as bibliotecas necessárias para a compilação, apenas as necessárias para a execução.

```Dockerfile
FROM golang:1.12 as builder

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY main.go .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:3.12.0

LABEL maintainer="José Hisse"

ENV GIN_MODE release

USER 1000:1000

WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

Vamos observar em seguida a quantidade de vunerabilidades detectadas nessa abordagem e o tamanho final da imagem.

![]()

## Explorando as imagens distroless

Em primeiro lugar, é bom explicarmos o que são imagens [distroless](https://github.com/GoogleContainerTools/distroless). São imagens que possuem apenas o mínimo para rodar determinada aplicação, ou seja, pacotes de sistema operacional, shell ou gerenciador de dependências são descartados.

Esses tipos de imagens se propõem a minimizar as possíveis vulnerabilidades e não gerar ruído de sua aplicação com outras. Esse tipo de imagem base é interessante em nosso caso, pois além de serem mais leves, são também mais seguras.

Vamos a um teste. Iremos agora modificar nosso Dockerfile adicionando uma imagem distroless base no lugar do alpine.

```Dockerfile
FROM golang:1.12 as builder

LABEL maintainer="José Hisse"

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY main.go .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM gcr.io/distroless/base@sha256:2b0a8e9a13dcc168b126778d9e947a7081b4d2ee1ee122830d835f176d0e2a70

ENV GIN_MODE release

USER 1000:1000

WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

## Conclusão

Chegamos ao final e podemos observar uma grande variedade de conteúdo que tivemos contato. 