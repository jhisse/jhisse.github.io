---
title: Expondo um banco relacional como um endpoint SPARQL
date: 2020-09-11
layout: post
---

Introduziremos o artigo analisando uma estrutura parcial de um sistema de ERP que contêm um conjunto de tabelas e relacionamentos. Primeiro faremos algumas perguntas que serão respondidas através de consultas SQL. Após gerarmos essas consultas, introduziremos alguns conceitos básicos sobre web semântica, RDF, ontologias (owl) e SPARQL.

## Introdução

Imagine uma situação onde uma empresa disponibilizou alguns dados de seu ERP, mais especificamente tabelas e relacionamentos envolvendo dados de seus funcionários, à qual departamento eles trabalham e à qual projeto estão envolvidos. A estrutura lógica disponibilizada é a seguinte:

![Modelo lógico parcial de um ERP](/images/expondo-um-banco-relacional-como-endpoint-sparql/logico.png)

A empresa deseja obter algumas informações a partir desse conjunto, como, quais são os projetos que cada departamento está inserido?

## Preparando o ambiente de testes

Vamos preparar nosso banco PostgreSQL com as tabelas indicadas no modelo lógico anteriormente. Para isso temos o script SQL abaixo:

```sql
CREATE TABLE departament (
    id integer NOT NULL CONSTRAINT departament_pk PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE employer (
    cpf bigint NOT NULL CONSTRAINT employer_pk PRIMARY KEY,
    name varchar(255) NOT NULL,
    fk_departament_id integer NOT NULL,
    CONSTRAINT employer_departament FOREIGN KEY (fk_departament_id)
    REFERENCES departament (id)
);

CREATE TABLE project (
    id integer NOT NULL CONSTRAINT project_pk PRIMARY KEY,
    name varchar(255) NOT NULL
);

CREATE TABLE works_on (
    fk_employer_cpf bigint NOT NULL,
    fk_project_id integer NOT NULL,
    CONSTRAINT works_on_pk PRIMARY KEY (fk_employer_cpf,fk_project_id),
    CONSTRAINT works_on_employer FOREIGN KEY (fk_employer_cpf)
    REFERENCES employer (cpf),
    CONSTRAINT works_on_project FOREIGN KEY (fk_project_id)
    REFERENCES project (id)
);
```

Como em outros artigos do site, vamos utilizar o docker para facilitar que nossos scripts sejam facilmente reproduzíveis.

## Respostas com consultas SQL

Vamos