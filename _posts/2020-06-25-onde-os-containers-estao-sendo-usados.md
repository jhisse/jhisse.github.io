---
title: Onde os containers estão sendo usados?
date: 2020-06-25
layout: post
---

Estamos falando de container na maioria dos artigos deste blog. O fato é, com ele podemos reproduzir nossas experimentações sem que haja problemas de compatibilidade de sistemas e dependências. A natureza da tecnologia de containers nos proporciona essa capacidade de replicarmos de forma igualitária nossos ambientes de execução das aplicações e as transportamos de maneira fácil para outras máquinas.

## Container não é uma tecnologia nova

Já em 1979 a ideia de isolamento de aplicações estava sendo concretizada. O [chroot]() foi lançado na [versão 7 do unix](). O chroot permite o isolamento do sistema de arquivos, alterando a forma que os processos filhos processo que foi executado o chroot enxergasse o diretório raiz.

Para entendermos um pouco melhor vamos executar um exemplo:

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

Executamos o chroot com o seguinte padrão ```chroot <nova raiz> <comando>```. No nosso caso a nova raiz era */ambiente* e o comando *bash*.

Após o chroot podemos verificar com o *ls* que nosso diretório raiz foi alterado para o /ambiente e a raiz principal não é mais enxergada por nosso processo, nem nenhum processo filho.

