---
title: Autenticando com oauth2_proxy, nginx e Github
date: 2019-10-19
layout: post
---

O objetivo deste artigo é implementarmos um método de autenticação de um website estático por oauth2 utilizando o [nginx](https://www.nginx.com/) como proxy reverso, [oauth2_proxy](https://pusher.github.io/oauth2_proxy/) como backend para validação das requisições e o [Github](https://github.com/) como provedor de autorização.

## Nginx para arquivos estáticos

Aqui iremos configurar o nginx para servir uma página HTML estática, neste caso pode ser um build do Jekyll, Hugo ou um simples HTML.

Nossa página HTML de teste será simples (index.html):

```html
<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <title>Index</title>
</head>

<body>
  <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent in nibh mi. Vivamus convallis lacinia dolor in
    pulvinar. Nulla mollis ultricies justo, ut fermentum dolor auctor a. Nullam consectetur nulla eget eros scelerisque
    tincidunt. Etiam in metus nisi. Donec vehicula nec erat eu aliquet. Fusce fermentum arcu sit amet purus suscipit
    tristique.</p>

  <p>Duis quis libero quis sapien tempor auctor. Morbi ut eros eu eros finibus blandit a vel ante. Praesent porta rutrum
    lorem, interdum tincidunt sem porttitor in. Morbi nunc nibh, aliquet hendrerit auctor sed, ultricies non ipsum. Nam
    a ante in dolor pharetra euismod. Donec aliquam turpis nec tortor ultricies molestie. Nunc dignissim, orci vitae
    tristique porta, magna erat dignissim dui, sit amet commodo tortor justo interdum nulla. Mauris dictum ex libero, at
    aliquet mauris sagittis sit amet. Etiam hendrerit elementum arcu at pulvinar. Nunc pellentesque tincidunt tortor,
    sit amet consequat felis blandit hendrerit. Nulla nibh sapien, sagittis quis cursus ac, luctus in neque. Nullam
    pellentesque maximus mollis. Fusce quam nisi, accumsan tincidunt nibh cursus, feugiat cursus urna. Pellentesque
    imperdiet aliquet quam, in gravida dolor vehicula eleifend.</p>

  <p>Proin sed sapien sit amet nisl faucibus dapibus. Cras sed cursus tellus. Nullam nunc metus, hendrerit et maximus
    in, tincidunt non sem. Etiam vehicula arcu nec erat posuere, nec tincidunt lorem rhoncus. Phasellus tincidunt
    fringilla enim. Vivamus porta ultricies enim vitae facilisis. Duis sit amet pulvinar dolor, maximus aliquam odio.
  </p>

  <p>Quisque eget volutpat nulla. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.
    Vivamus sagittis, magna non ullamcorper blandit, turpis nisi lacinia risus, eget tempus libero lorem vitae risus.
    Curabitur quis ligula eu dolor volutpat placerat. Integer iaculis, arcu non luctus ultricies, dolor est fermentum
    enim, quis ullamcorper magna sapien a est. Nulla facilisi. Nulla lectus leo, pellentesque quis iaculis non, mollis
    in neque. Cras porttitor lacinia dolor quis hendrerit.</p>

  <p>Etiam dictum rutrum ligula, sed eleifend nibh consectetur ut. Etiam pellentesque urna eget tempus hendrerit. Nullam
    faucibus convallis mauris, id hendrerit diam eleifend a. Curabitur ultrices ex diam, vitae accumsan lectus vulputate
    eu. Aliquam ultricies eu arcu quis dignissim. Sed pharetra leo non erat dapibus, vitae porta augue aliquet. Morbi
    porttitor pellentesque dui, sed vulputate nulla pulvinar sit amet. Aenean consequat luctus nisi. Maecenas imperdiet
    diam sit amet iaculis porttitor. Donec fermentum est sapien, maximus tempus nunc posuere sit amet. Nulla vestibulum
    elementum lacus quis placerat.</p>

</body>

</html>
```

Agora vamos configurar o Dockerfile para colocar esta página HTML dentro de uma imagem Docker.

```dockerfile
FROM nginx:alpine

ADD index.html /usr/share/nginx/html
```

A estrutura do diretório irá ficar da seguinte forma:

\- nginx  
\-- Dockerfile  
\-- index.html  

Temos que buildar nossa imagem do nginx e executa-lá em seguida:

```bash
cd nginx
docker build -t nginx_static .
docker run --rm -p 80:80 nginx_static
```

Podemos acessar o endereço `http://localhost` para verificarmos que nossa aplicação funcionou e a nossa página está sendo exibida corretamente.

Tendo nosso ponto de partida configurado, vamos seguir para a configuração da autenticação.

## Configurando o provedor de autorização

O Github funcionará como nosso provedor de autorização, ou seja, o usuário que deseja logar irá permitir que o nosso backend possa acessar os dados do solicitante. Em seguida o provedor enviará um código de autorização que indica que o backend está autorizado a receber os dados do usuário.

Então o primeiro passo é criarmos um OAuth App em nosso provedor de autenticação. Entre no Github e vá para **Settings** -> **Developers Settings** -> **OAuth Apps** ([link direto](https://github.com/settings/developers)), clique em **Register a new application**.

![Register a new Application](/images/register_oauth_app_github.png)

Escolha um nome para sua aplicação, como estamos testando localmente, em **Homepage URL** coloque `http://localhost` e em **Callback URL** coloque `http://localhost/oauth2/callback`.

Os endpoints disponíveis do oauth2_proxy pode ser consultado neste [link](https://pusher.github.io/oauth2_proxy/endpoints).

![FCampos OAuth App Github](/images/fields_oauth_app_github.png)

Agora temos um *client_id* e um *client_secret* que serão utilizados pelo oauth2_proxy.

## Configurando 