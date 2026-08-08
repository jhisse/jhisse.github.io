---
title: "[TIL] O link-checker do blog pegou a doc da MinIO CE saindo do ar"
date: 2026-08-08
layout: post
---

Ao rodar o [lychee](https://github.com/lycheeverse/lychee) como verificador de links do blog, um alerta chamou atenção: uma URL da documentação da MinIO Community Edition, citada num post antigo sobre object storage self-hosted, não retorna mais o conteúdo original. Não é um `404`: o link ainda responde `200`. Ele redireciona para a documentação do AIStor, o produto enterprise pago, mas a página, embora carregue normalmente, não é mais a que o post pretendia citar.

O que mudou não foi um endereço. Em 10 de outubro de 2025, toda a documentação pública da Community Edition foi retirada do ar; o [README do repositório `minio/docs`](https://github.com/minio/docs) registra, em texto literal, que a "documentation was pulled from web hosting" e que não há "further development planned". Hoje `docs.min.io` é dedicado ao AIStor. Não houve comunicado formal: a mudança foi sinalizada por commit e README, e o repositório [`minio/minio`](https://github.com/minio/minio) acabou arquivado em abril de 2026. Existe um [fork da comunidade](https://github.com/pgsty/minio-docs) restaurando a doc removida.

O ponto que fica: a documentação de um projeto open-source citada num post é uma dependência externa como qualquer outra. Está fora do seu controle e pode mudar não só de endereço, mas de modelo de negócio. E um redirect que responde `200` é o caso mais traiçoeiro, porque não dispara alarme algum enquanto a referência deixa de apontar para o que se pretendia dizer (um `404` honesto teria dado menos trabalho).

Daí duas providências: uma nota editorial no post original, avisando que a doc referenciada saiu do ar e apontando para o fork da comunidade; e o próprio [link-checker automatizado](/blog/evitando-links-quebrados-com-lychee/) (que foi como isso apareceu) rodando como parte da manutenção contínua do blog. Manter um post tecnicamente correto ao longo do tempo é trabalho contínuo, não um "publicou e esqueceu".
