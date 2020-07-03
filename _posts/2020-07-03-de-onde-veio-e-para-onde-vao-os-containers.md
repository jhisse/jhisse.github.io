---
title: De onde veio e para onde vão os containers
date: 2020-07-03
layout: post
---

Estamos falando de container na maioria dos artigos deste blog. O fato é, com ele podemos reproduzir nossas experimentações sem que haja problemas de compatibilidade de sistemas e dependências. A natureza da tecnologia de containers nos proporciona essa capacidade de replicarmos de forma igualitária nossos ambientes de execução das aplicações e as transportamos de maneira fácil para outras máquinas.

## Container não é uma tecnologia nova

Já em 1979 a ideia de isolamento de aplicações estava sendo concretizada. O [chroot](https://man7.org/linux/man-pages/man1/chroot.1.html) foi lançado na [versão 7 do unix](https://en.wikipedia.org/wiki/Version_7_Unix), onde permite o isolamento do sistema de arquivos, alterando a forma que o processo principal e seus processos filhos enxergassem o diretório raiz.

Os anos foram passando e vinte anos mais tarde o sistema FreeBSD anunciou o novo comando [jail](https://www.freebsd.org/doc/handbook/jails.html) no [release 4.0](https://www.freebsd.org/releases/4.0R/notes.html). O jails seguia a ideia do chroot, porém estendia seu isolamento para além do filesystem, passando pela gerência de usuários, redes e processos.

Melhorias foram sendo implementadas e o isolamento de processos e recursos foram se aprimorando. Outras empresas foram desenvolvendo suas próprias aplicações voltadas para esse foco.

Em 2008 o LXC, Linux Containers, construído com base no [cgroups](https://man7.org/linux/man-pages/man7/cgroups.7.html) e nos [namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html), foi uma implementação completa de gerenciamento de container. O LXC permitia executar suas aplicações com isolamento suficiente para que o kernel do host fosse compartilhado.

O Docker foi criado em 2013 e preenchia um gap emergente no mercado. As aplicações precisavam de uma forma de seu ambiente de execução ser reproduzido de forma rápida. As metodologias ágeis buscavam rapidez na entrega de valor e melhoria contínua. As empresas precisavam de eficiencia com o uso de recursos na nuvem. Nesse contexto o Docker surgiu provendo um conjunto de soluções de alto nível que abstraiam as funcionalidades de baixo nível como o cgroups e os namespaces já existentes, resolvendo assim uma parte dessas demandas.

Hoje temos diversas implementações que permitem a execução de containers, os containers runtimes ([para saber mais](https://www.ianlewis.org/en/container-runtimes-part-1-introduction-container-r)). Alguns exemplos são: [RKT](https://coreos.com/rkt/], [Podman](https://podman.io/), [Buildah](https://buildah.io/)...

## Entendendo algumas tecnologias de isolamento

### Chroot

Para entendermos um pouco melhor como o chroot atua vamos executar um exemplo:

```console
$ docker container run --rm -it ubuntu:18.04 bash

root:teste/# mkdir -p ambiente/{bin,lib,lib64} # Criando diretórios necessários

root:teste/# cp /bin/bash /bin/ls ambiente/bin/ # Copiando binários para testes

root:teste/# touch ambiente/arquivo{1,2}.txt # Criando dois arquivos quaisquer

root:teste/# ldd /bin/bash # Verificando dependências do binário bash
  linux-vdso.so.1 (0x00007ffcb4100000)
  libtinfo.so.6 => /lib/x86_64-linux-gnu/libtinfo.so.6 (0x00007f63adb61000)
  libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f63adb5b000)
  libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f63ad969000)
  /lib64/ld-linux-x86-64.so.2 (0x00007f63adcc1000)

root:teste/# cp /lib/x86_64-linux-gnu/libtinfo.so.5 /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libc.so.6 /ambiente/lib/

root:teste/# cp /lib64/ld-linux-x86-64.so.2 /ambiente/lib64/

root@teste:/# ldd /bin/ls # Verificando dependências do binário ls
  linux-vdso.so.1 (0x00007ffecb50d000)
  libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007f99f34a2000)
  libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f99f30b1000)
  libpcre.so.3 => /lib/x86_64-linux-gnu/libpcre.so.3 (0x00007f99f2e3f000)
  libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f99f2c3b000)
  /lib64/ld-linux-x86-64.so.2 (0x00007f99f38ec000)
  libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f99f2a1c000)

root:teste/# cp /lib/x86_64-linux-gnu/libselinux.so.1 /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libpcre.so.3 /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libpthread.so.0 /ambiente/lib/

root:teste/# cp /lib64/ld-linux-x86-64.so.2 /ambiente/lib64/

root:teste/# chroot /ambiente/ bin/bash # Fazendo chroot para o diretório /ambiente

root@teste:/# chroot /ambiente/ bin/bash

bash-4.4# ls / # Listando a nova raiz do sistema de arquivos
arquivo1.txt  arquivo2.txt  bin  lib  lib64

bash-4.4# exit
exit

root@teste:/# chroot /ambiente/ bin/bash & # e comercial no final para executar em background
[2] 51

root@teste:/# ls -la /proc/51/root # Verificando se o chroot alterou a raiz
lrwxrwxrwx 1 root root 0 Jul  2 04:04 /proc/51/root -> /ambiente

root@teste:/# exit
```

No exemplo acima começamos criando uma estrutura básica para executarmos dois binários, o *bash* e o *ls*. Após a preparação dessa hieraquia de diretórios copiamos os binários e as dependencias que eles necessitam.

Executamos o chroot com o seguinte padrão ```chroot <nova raiz> <comando>```. No nosso caso a nova raiz era */ambiente* e o comando *bash*. Após o chroot podemos verificar com o *ls* que nosso diretório raiz foi alterado para o /ambiente e a raiz principal do sistema operacional não é mais enxergada por nosso processo, nem nenhum processo filho.

## Domínios que os containers estão inseridos

### DevOps

As ferramentas de contínuos 

### Analytics

ELK

A stack do Elastic pode ser reproduida por completo através de containers

### 


## Conclusão