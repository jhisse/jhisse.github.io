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

Henry Spencer lançou em um grupo de discussão a primeira biblioteca não comercial para linguagem C chamada [regex](http://man7.org/linux/man-pages/man7/regex.7.html). Foram três versões desenvolvidas, 1986, 1993 e 1999. Hoje a biblioteca é usada em grandes sistemas como no [PostgreSQL](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-POSIX-REGEXP) e no [MySQL](https://dev.mysql.com/doc/refman/8.0/en/regexp.html) até a versão 5.6.
