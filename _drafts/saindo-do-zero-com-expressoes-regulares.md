---
title: Saindo do zero com expressões regulares
date: 2020-02-29
layout: post
---

Você já precisou procurar em um texto sequências de caracteres que correspondiam a um padrão? Validar um número de telefone? Analizar logs de um servidor? São inúmeros os casos de uso das expressões regulares, porém seu uso pode parecer um pouco complicado à primeira vista. Ao longo deste texto vamos entender o contexto que ela surgiu e aprender suas principais funções.

## História

Tudo começou quando em 1943 com Warren McCulloch e Walter Pitts publicaram um artigo entitulado ["A logical calculus of the ideas immanent in nervous activity"](https://link.springer.com/article/10.1007/BF02478259) onde eles associaram a atividade neuronal com a lógica proposicional, ou seja, eles modelaram através da lógica a forma que os neurônios interagiam entre si.

Mais tarde em 1951, com o paper [“Representation of Events in Nerve Nets and Finite Automata”](https://www.rand.org/content/dam/rand/pubs/research_memoranda/2008/RM704.pdf) Stephen Kleene formalizou algebricamente os modelos neurológicos descritos por McCulloch e Pitts.

Ken Thompson, hoje colaborador da linguagem de programação Go, em 1968 enquanto trabalhava na Bell Labs publicou ["Regular Expression Search Algorithm"](https://www.fing.edu.uy/inco/cursos/intropln/material/p419-thompson.pdf). Ele descreveu um método de busca em texto que recebe como input uma determinada expressão regular, também mostrou uma implementação de um compilador para transformar uma expressão regular em um código compilado.

Henry Spencer lançou em um grupo de discussão a primeira biblioteca não comercial de expressões regulares para linguagem C chamada [regex](http://man7.org/linux/man-pages/man7/regex.7.html). Foram três versões desenvolvidas, 1986, 1993 e 1999. Hoje a biblioteca é usada em grandes sistemas como no [PostgreSQL](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-POSIX-REGEXP) e no [MySQL](https://dev.mysql.com/doc/refman/8.0/en/regexp.html) até a versão 5.6.

## Preparação do ambiente de testes

Nesse post vamos utilizar a ferramenta [grep](http://man7.org/linux/man-pages/man1/grep.1.html), ela nos permite buscar por padrões em uma cadeia de caracteres. Caso você esteja em sistema baseado no unix, provavelmente você já tem disponível para uso. Caso você esteja em outro sistema operacional ou não tenha a ferramenta disponível, pode usar um container docker.

```console
$ docker run -it alpine ash
Unable to find image 'alpine:latest' locally
latest: Pulling from library/alpine
c9b1b535fdd9: Pull complete
Digest: sha256:ab00606a42621fb68f2ed6ad3c88be54397f981a7b70a79db3d1172b11c4367d
Status: Downloaded newer image for alpine:latest
/ # grep
BusyBox v1.31.1 () multi-call binary.

Usage: grep [-HhnlLoqvsriwFE] [-m N] [-A/B/C N] PATTERN/-e PATTERN.../-f FILE [FILE]...

Search for PATTERN in FILEs (or stdin)

  -H    Add 'filename:' prefix
  -h    Do not add 'filename:' prefix
  -n    Add 'line_no:' prefix
  -l    Show only names of files that match
  -L    Show only names of files that don't match
  -c    Show only count of matching lines
  -o    Show only the matching part of line
  -q    Quiet. Return 0 if PATTERN is found, 1 otherwise
  -v    Select non-matching lines
  -s    Suppress open and read errors
  -r    Recurse
  -i    Ignore case
  -w    Match whole words only
  -x    Match whole lines only
  -F    PATTERN is a literal (not regexp)
  -E    PATTERN is an extended regexp
  -m N    Match up to N times per file
  -A N    Print N lines of trailing context
  -B N    Print N lines of leading context
  -C N    Same as '-A N -B N'
  -e PTRN    Pattern to match
  -f FILE    Read pattern from file
```

Nos exemplos que virão a seguir vamos usar a seguinte estrutura:

```console
echo "<texto>" | grep -oP "<pattern>"
```

Essa estrutura indica que o \<texto\> será enviado para o comando grep como input e por sua vez o grep irá buscar o \<pattern\>. A opção *o* faz o grep imprimir no terminal cada sequência encontrada em uma linha diferente e a opção *P* faz com que o grep interprete o pattern como a linguagem Perl que permite utilizar algumas funções a mais.

## Metacaracteres

Em regex alguns caracteres tem interpretações especias, ou seja, eles podem assumir certos tipos de funções. A seguir vamos conhecer alguns deles.

### O ponto - **.**

O metacaractere ponto casa qualquer caractere em determinada posição.

Vamos ver três exemplos para entendermos melhor:

```console
$ echo "pato galinha gato rato sapo galo" | grep -oP '.ato'
pato
gato
rato
```

Neste primeiro exemplo estávamos procurando pelo padrão, qualquer caractere seguido pela sequência literal "ato".

```console
$ echo "pato galinha gato rato sapo galo" | grep -oP 'gal.'
gali
galo
```

No segundo exemplo procurarmos pela sequência "gal" seguida de qualquer caractere.

```console
$ echo "pato galinha gato rato sapo galo" | grep -oP '.a.o'
pato
gato
rato
sapo
galo
```

Por último procuravámos por qualquer caractere seguida pela vogal "a", novamente qualquer caractere e por último a vogal "o".

### A alternância - **|**

O caractere de barra vertical ou pipe é usado como alternância, ou seja, é usado quando queremos usar a lógica de ou, ou uma coisa ou outra.

```console
$ echo "pato galinha gato rato sapo galo" | grep -oP 'pato|gato'
pato
gato
```

### O agrupador - **( )**


### A lista - **[ ]**

A lista pode ser entendida como uma sequência de caracteres separados por um \|. Isso quer dizer que o padrão irá casar um caractere que esteja dentro da lista.

```console
$ echo "pato galinha gato rato sapo galo" | grep -o '[pg]ato'
pato
gato
```

### A lista rejeitada - **[^ ]**


### A âncora de ínicio - **^**


### A âncora de fim - **$**
