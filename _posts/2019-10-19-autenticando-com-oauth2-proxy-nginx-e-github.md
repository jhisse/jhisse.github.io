---
title: Autenticando com oauth2_proxy, nginx e Github
date: 2019-10-19
layout: post
---

O objetivo deste artigo é implementarmos um método de autenticação de um website estático por oauth2 utilizando o [nginx](https://www.nginx.com/) como proxy reverso, [oauth2_proxy](https://pusher.github.io/oauth2_proxy/) como backend para as validações das requisições e o [Github](https://github.com/) como provedor de autorização.

## Configurando o provedor de autorização

O Github funcionará como nosso provedor de autorização, ou seja, o usuário que deseja logar irá permitir que o nosso backend possa acessar os dados do solicitante. Em seguida o provedor enviará um código de autorização que indica que o backend está autorizado a receber os dados do usuário.

