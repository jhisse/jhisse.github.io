---
title: Diferença entre explode e explode_outer no pyspark
# date: 2019-10-06
layout: post
---

É comum em transformações de dados nos depararmos com estruturas como arrays, seja arrays de strings, inteiros ou algum outro tipo de objeto.

## Preparação do ambiente

Vamos utilizar uma imagem docker do jupyter contendo o pyspark já instalado.

```console
docker run -d -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes jupyter/pyspark-notebook:e255f1aa00b2 start-notebook.sh --NotebookApp.token=''
```

No navegador acesse o endereço <localhost:8888> e crie um novo notebook.

![Jupyter com pyspark](/images/diferenca-entre-explode-e-explode-outer-no-pyspark/2020-03-21_19-39.png)

