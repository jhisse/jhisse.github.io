---
title: Sequência de Collatz
date: 2019-10-07
layout: post
mathjax: true
---

## Problema

A seguinte questão foi proposta no [problema 14 do Project Euler](https://www.projecteuler.net/problem=14 "Problema 14 do Project Euler").

A sequência de Collatz é gerada pela seguinte regra:

\\[
n =
\begin{cases}
  & n/2 \text{, se } n \text{ é par } \\\\  
  & 3n+1 \text{, se } n \text{ é ímpar }
\end{cases}
\\]

De acordo com a regra acima e começando pelo número 13, temos a seguinte sequência:

\\[ 13 \rightarrow 40 \rightarrow 20 \rightarrow 10 \rightarrow 5 \rightarrow 16 \rightarrow 8 \rightarrow 4 \rightarrow 2 \rightarrow 1 \\]

A sequência acima possui 10 termos até que se chegue ao número 1.

Não foi provado que começando de qualquer número a sequência acabará em 1.

Qual número abaixo de 1 milhão gera a maior sequência?

## Solução Naïve

Primeiro devemos ter uma função que represente o calculo da sequência de Collatz:

```python
def collatz(x):
  if x % 2: # Se ímpar
    return 3*x+1
  else: # Se par
    return x/2
```
