---
title: Sequência de Collatz
date: 2019-10-07
layout: default
---

## Problema proposto

A seguinte questão foi proposta no [problema 14 do Project Euler](https://www.projecteuler.net/problem=14 "Problema 14 do Project Euler").

A sequência de Collatz é gerada pela seguinte regra:

{% raw %}
\\[
n =s
\begin{cases}
  & n/2 \text{, se } x \text{ é par } \\
  & 3n+1 \text{, se } x \text{ é ímpar }
\end{cases}
\\]
{% endraw %}

De acordo com a regra acima e começando pelo número 13, temos a seguinte sequência:

13 -> 40 -> 20 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1

A sequência acima possui 10 termos até que se chegue ao número 1.

Não foi provado que começando de qualquer número a sequência acabará em 1.

Qual número abaixo de 1 milhão gera a maior sequência?

## Solução Naïve
