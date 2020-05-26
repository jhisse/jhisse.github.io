---
title: Verificando vulnerabilidades em containers com Trivy e Gitlab CI/CD
date: 2020-05-22
layout: post
---

Neste artigo vamos criar uma API na linguagem golang, armazenar o código fonte em um repositório git, Gitlab e construir um pipeline de continuous integration para build, teste de vulnerabilidade e report de possíveis falhas de segurança em uma imagem docker contendo nossa aplicação. Ao final teremos o fluxo de continuous integration de uma aplicação, desde o código fonte até a disponibilização da imagem docker em um container registry.

## Entendendo o plano

[Diagrama]

O primeiro passo é construir uma simples API REST que na rota ```/ping``` irá responder uma simples mensagem. No processo de desenvolvimento da API é de boa prática irmos commitando nossos avanços em um repositório git, ou seja, um local onde é possível versionar de forma eficiente nosso código.

Vamos manter em mente que o objetivo do artigo é utilizarmos a ferramenta Trivy para identificarmos vulnerabilidades em nossas imagens docker. Então, o foco está no processo de continuous integration de nossa aplicação, porém para termos esse processo de automatização vamos utilizar o Gitlab. Ele possui uma ótima feature para CI/CD, ou seja , tanto continuous integration, quanto continuous delivery e continuous deployment. No nosso caso vamos explorar somente o primeiro.

Nosso processo de continuous integration

## Construindo nossa API

Vamos utilizar o framework [Gin](https://github.com/gin-gonic/gin) neste exemplo.

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

## Preparando no Dockerfile

```Dockerfile
FROM golang:latest as builder

LABEL maintainer="José Hisse"

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY main.go .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:latest

USER 1000:1000

WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

## Gitlab CI/CD

