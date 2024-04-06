---
title: Sequência de Collatz
date: 2019-10-12
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

Conforme a regra acima e começando pelo número 13, temos a seguinte sequência:

\\[ 13 \rightarrow 40 \rightarrow 20 \rightarrow 10 \rightarrow 5 \rightarrow 16 \rightarrow 8 \rightarrow 4 \rightarrow 2 \rightarrow 1 \\]

A sequência acima possui 10 termos até que se chegue ao número 1.

Não foi provado que começando de qualquer número a sequência acabará em 1.

Qual número abaixo de 1 milhão gera a maior sequência?

## Solução Naïve

Primeiro devemos ter uma função que represente o cálculo da sequência de Collatz, depois precisamos calcular a quantidade total de termos que partindo de um determinado número chegaremos ao 1.

Como o problema propõe acharmos a maior sequência partindo de um número abaixo de n, criaremos a função calcular_maior_sequencia que receberá um número máximo onde iremos iterar de 1 até o limite máximo para acharmos o número que tem a maior quantidade de termos.

```python
import timeit

def collatz(x):
    if x % 2:   # Se ímpar
        return 3*x+1
    return x/2  # Se par


def calcular_qtd_em_sequencia(n):
    qtd_termos = 1  # Incluindo já o primeiro termo
    while n != 1:
        n = collatz(n)
        qtd_termos += 1
    return qtd_termos


def calcular_maior_sequencia(n_max):
    n_com_maior_sequencia = 0
    qtd_maior_sequencia = 0
    for termo_inicial in range(1, n_max+1):
        qtd_candidata = calcular_qtd_em_sequencia(termo_inicial)
        if qtd_candidata >= qtd_maior_sequencia:
            n_com_maior_sequencia = termo_inicial
            qtd_maior_sequencia = qtd_candidata
    return n_com_maior_sequencia, qtd_maior_sequencia


start = timeit.default_timer()

print("Número {} com {} termos".format(*calcular_maior_sequencia(1000000)))

stop = timeit.default_timer()
print('Tempo decorrido: ', stop - start)
```

Aqui podemos perceber que a saída para n_max = 1000000 foi:

```bash
Número 837799 com 525 termos
Tempo decorrido:  39.81831162200251
```

## Otimizando com cache

Vamos observar a seguinte situação.

Calculando a sequência do número 5:

\\[ 5 \rightarrow 16 \rightarrow 8 \rightarrow 4 \rightarrow 2 \rightarrow 1 \\]

Depois calculando a sequência do número 6:

\\[ 6 \rightarrow 3 \rightarrow 10 \rightarrow 5 \rightarrow 16 \rightarrow 8 \rightarrow 4 \rightarrow 2 \rightarrow 1 \\]

Como podemos observar a sequência do número 5 acaba sendo um subconjunto da sequência do número 6, ou seja, gastamos recursos computacionais com cálculos redundantes.

Podemos reescrever a função `calcular_qtd_em_sequencia` para utilizarmos a técnica de `memoização`. Como isso evitamos recálculos.

```python
memo = {}
def calcular_qtd_em_sequencia(n):
    qtd_termos = 1  # Incluindo já o primeiro termo
    n_original = n
    while n != 1:
        n = collatz(n)
        qtd_memo = memo.get(n)
        if qtd_memo:
            qtd_termos += qtd_memo
            break
        qtd_termos += 1
    memo[n_original] = qtd_termos
    return qtd_termos
```

Ganhamos muito em desempenho, como podemos oberservar abaixo.

```bash
Número 837799 com 525 termos
Tempo decorrido:  3.9822970859968336
```

O cache poderia ser otimizado de algumas outras formas, como, por exemplo, a utilização do cache LRU.

## Escovando bit

Podemos otimizar a função collatz realizando operações de bits.

Por exemplo, sabemos que o número 5 em binário é representado por 101 e o número 6, 110, ou seja, o último bit nos indica a paridade. Então, para não termos que calcular o resto de uma divisão basta compararmos o último bit do número.

Outra melhoria é na operação de divisão por 2. Como a operação de divisão neste caso só é realizada sobre números pares, então podemos fazer uma operação de shift a direita.

Então a função collatz poderia ser reescrita da seguinte forma:

```python
def collatz(x):
    if x & 1:   # Se ímpar
        return 3*x+1
    return x >> 1  # Se par
```

```bash
Número 837799 com 525 termos
Tempo decorrido:  2.9432366770051885
```

## Código final

```python
import timeit


def collatz(x):
    if x & 1:  # Se ímpar
        return 3 * x + 1
    return x >> 1  # Se par


memo = {}
def calcular_qtd_em_sequencia(n):
    qtd_termos = 1  # Incluindo já o primeiro termo
    n_original = n
    while n != 1:
        n = collatz(n)
        qtd_memo = memo.get(n)
        if qtd_memo:
            qtd_termos += qtd_memo
            break
        qtd_termos += 1
    memo[n_original] = qtd_termos
    return qtd_termos


def calcular_maior_sequencia(n_max):
    n_com_maior_sequencia = 0
    qtd_maior_sequencia = 0
    for termo_inicial in range(1, n_max+1):
        qtd_candidata = calcular_qtd_em_sequencia(termo_inicial)
        if qtd_candidata >= qtd_maior_sequencia:
            n_com_maior_sequencia = termo_inicial
            qtd_maior_sequencia = qtd_candidata
    return n_com_maior_sequencia, qtd_maior_sequencia


start = timeit.default_timer()

print("Número {} com {} termos".format(*calcular_maior_sequencia(1000000)))

stop = timeit.default_timer()
print('Tempo decorrido: ', stop - start)
```
