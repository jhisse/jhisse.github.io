---
title: Saindo do zero com expressões regulares
date: 2020-03-14
layout: post
---

Você já precisou procurar em um texto sequências de caracteres que correspondiam a um padrão? Validar um número de telefone? Analisar logs de um servidor? São inúmeros os casos de uso das expressões regulares, porém seu uso pode parecer um pouco complicado à primeira vista. Ao longo deste texto, vamos entender o contexto em que elas surgiram e aprender suas principais funções.

## História

Tudo começou em 1943, quando Warren McCulloch e Walter Pitts publicaram um artigo intitulado ["A logical calculus of the ideas immanent in nervous activity"](https://link.springer.com/article/10.1007/BF02478259) onde eles associaram a atividade neuronal com a lógica proposicional: eles modelaram através da lógica a forma que os neurônios interagiam entre si.

Mais tarde, em 1951, com o paper ["Representation of Events in Nerve Nets and Finite Automata"](https://www.rand.org/content/dam/rand/pubs/research_memoranda/2008/RM704.pdf), Stephen Kleene formalizou algebricamente os modelos neurológicos descritos por McCulloch e Pitts.

Ken Thompson, hoje colaborador da linguagem de programação Go, em 1968, enquanto trabalhava na Bell Labs, publicou ["Programming techniques: Regular expression search algorithm."](https://dl.acm.org/doi/abs/10.1145/363347.363387). Ele descreveu um método de busca em texto que recebe como input uma determinada expressão regular, também mostrou uma implementação de um compilador para transformar uma expressão regular em um código compilado.

Henry Spencer lançou em um grupo de discussão a primeira biblioteca não comercial de expressões regulares para linguagem C chamada [regex](https://man7.org/linux/man-pages/man7/regex.7.html). Foram três versões desenvolvidas: 1986, 1993 e 1999. Hoje a biblioteca é usada em grandes sistemas como no [PostgreSQL](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-POSIX-REGEXP) e no [MySQL](https://dev.mysql.com/doc/refman/8.0/en/regexp.html) até a versão 5.6.

## Preparação do ambiente de testes

Nesse post vamos utilizar a ferramenta [grep](https://man7.org/linux/man-pages/man1/grep.1.html), ela nos permite buscar por padrões em uma cadeia de caracteres. Caso você esteja em sistema baseado no unix, provavelmente você já tem disponível para uso. Caso você esteja em outro sistema operacional ou não tenha a ferramenta disponível, pode usar um container docker.

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

Nos exemplos que virão a seguir usaremos a seguinte estrutura:

```console
echo "<texto>" | grep -oE "<pattern>"
```

Essa estrutura indica que o \<texto\> será enviado para o comando grep como input e, o grep irá buscar o \<pattern\>. A opção _o_ faz o grep imprimir no terminal cada sequência encontrada em uma linha diferente e a opção _P_ faz com que o grep interprete o pattern como a linguagem Perl que permite utilizar algumas funções a mais.

## Metacaracteres

Em regex alguns caracteres têm interpretações especias, ou seja, eles podem assumir certos tipos de funções. A seguir, vamos conhecer alguns deles.

### O ponto - **.**

O metacaractere ponto casa qualquer caractere em determinada posição.

Vamos ver três exemplos para entendermos melhor:

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '.ato'
pato
gato
rato
```

Neste primeiro exemplo estávamos procurando pelo padrão, qualquer caractere seguido pela sequência literal "ato".

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE 'gal.'
gali
galo
```

No segundo exemplo procurarmos pela sequência "gal" seguida de qualquer caractere.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '.a.o'
pato
gato
rato
sapo
galo
```

Por último procurávamos por qualquer caractere seguida pela vogal "a", novamente qualquer caractere e por último a vogal "o".

### A alternância - **|**

O caractere de barra vertical ou pipe é usado como alternância, ou seja, é usado quando queremos usar a lógica de ou, ou uma coisa, ou outra.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE 'pato|gato'
pato
gato
```

### O agrupador - **( )**

Também conhecido como grupo de captura, tem por objetivo agrupar metacaracteres. Muito útil em busca e substituição, pois nos permite referenciar o grupo para um possível reuso.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '(p|g)ato'
pato
gato
```

### A lista - **[ ]**

A lista pode ser entendida como uma sequência de caracteres separados por um \|. Isso quer dizer que o padrão irá casar um caractere que esteja na lista.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '[pg]ato'
pato
gato
```

### A lista rejeitada - **[^ ]**

A lista rejeitada indica que os caracteres contidos nela não vão casar com os padrões buscados.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '[^pg]ato'
rato
```

### A âncora de ínicio - **^**

O metacaractere de acento circunflexo indica o começo de uma linha, ou seja, é uma forma da expressão regular interpretar o início de uma linha.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '^.ato'
pato
```

### A âncora de fim - **$**

O metacaractere dollar é semelhante ao anterior, porém indica o fim de uma linha.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE 'ga.o$'
galo
```

### Metacaracteres de repetição - **\* + ? {}**

O asterisco tentará casar o máximo possível de seu antecedente, vamos ver alguns exemplos.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '.*'
pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo
```

No exemplo acima usamos o metacaractere que representa qualquer caractere e o repetimos o máximo número de ves que conseguímos.

A seguir veremos que podemos usar um range de valores dentro de uma lista e combinar com o caractere de repetição. Nota-se que os caracteres diferentes de letras minúsculas não deram match.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '[a-z]*'
pato
galinha
gato
rato
sapo
galo
```

Vale destacar que o asterisco casa tudo ou nada.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE 'p*ato'
pato
ato
ato
```

Já o sinal de mais pode casar um ou mais.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE 'p+ato'
pato
```

O sinal de interrogação indica que a expressão que o antecede é opcional, pode ocorrer ou não.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE 'g?ato'
pato
```

No exemplo acima, o match foi na sequência "ato" da primeira palavra pato, a palavra gato por inteiro, já que a letra g era opcional, e a sequência "ato" da palavra rato.

Por fim, as chaves representam o número mínimo e máximo de ocorrências. Uso é feito da seguindo o formato {n,m}, sendo n o número mínimo e m o número máximo, pode-se ocultar o número m, {n} ou {n,}, significa que temos um número exato de elemento a dar match no primeiro e no segundo indica que temos um número mínimo de caracteres a dar match.

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '[0-9]{2,3}'
234
763
52
342
34
```

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '[0-9]{2,}'
2342
7634
52
3423
34
```

```console
$ echo "pato 2342 galinha 7634 gato 52 rato 3423 sapo 34 galo" | grep -oE '[0-9]{3}'
234
763
342
```

## Alguns exemplos do mundo real

### Validando CPF

```console
$ echo "123.456.789.11" | grep -qE '^(\d{3}\.){3}\d{2}$' && echo "Validate" || echo "Not Match"
Validate
```

```console
$ echo "123.456.789.111" | grep -qE '^(\d{3}\.){3}\d{2}$' && echo "Validate" || echo "Not Match"
Not Match
```

```console
$ echo "12e.45o.789.a1" | grep -qE '^(\d{3}\.){3}\d{2}$' && echo "Validate" || echo "Not Match"
Not Match
```

### Validando datas no formato dd/MM/yyyy

```console
$ echo "15/02/2020" | grep -qE '^(0[1-9]|[12]\d|3[01])\/(0[1-9]|1[0-2])\/\d{4}$' && echo "Validate" || echo "Not Match"
Validate
```

```console
$ echo "00/06/2009" | grep -qE '^(0[1-9]|[12]\d|3[01])\/(0[1-9]|1[0-2])\/\d{4}$' && echo "Validate" || echo "Not Match"
Not Match
```

### Busca de números hexadecimais

```console
$ echo "h1 {color: #00ff00; border-style: solid; border-color: #92a8d1;}" | grep -oE '#([0-9a-fA-F]{2}){3}'
#00ff00
#92a8d1
```

## Conclusão

Agora que exploramos diversos exemplos, podemos ver claramente como as expressões regulares são uma ferramenta poderosa para manipulação de texto e validações. Compreender e dominar seu uso pode facilitar muito a realização de tarefas complexas em diversas áreas, desde a programação até a análise de dados. Espero que este guia tenha ajudado você a sair do zero com expressões regulares.
