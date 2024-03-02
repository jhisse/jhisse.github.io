---
title: Expondo um banco relacional como um endpoint SPARQL
date: 2020-09-11
layout: post
---

Introduziremos o artigo analisando uma estrutura parcial de um possível sistema de ERP que contêm um conjunto de tabelas e relacionamentos. Primeiro faremos algumas perguntas respondidas através de consultas SQL. Após gerarmos essas consultas, introduziremos alguns conceitos básicos sobre web semântica, RDF, ontologias (owl) e SPARQL. Criaremos uma ontologia simples e analisaremos algumas regras de inferência. Iremos explorar a linguagem R2RML, a linguagem de mapeamento de banco de dados relacionais para linked data. Por fim iremos utilizar a ferramenta Ontop para conectar a nossa base SQL utilizando nossa ontologia e nosso mapeamento para disponibilizarmos um endpoint SPARQL.

## Introdução

Imagine uma situação onde uma empresa disponibilizou alguns dados de seu ERP, mais especificamente tabelas e relacionamentos envolvendo dados de seus funcionários, à qual departamento eles trabalham e à, qual projeto estão envolvidos. A estrutura lógica disponibilizada é a seguinte:

![Modelo lógico parcial de um ERP](/images/expondo-um-banco-relacional-como-endpoint-sparql/logico.png)

A empresa deseja obter uma informação a partir desse conjunto:

- Quais são os projetos que cada departamento está inserido?

## Preparando o ambiente de testes

Vamos preparar nosso banco relacional com as tabelas indicadas no modelo lógico e com alguns dados de testes.

Como em outros artigos do site, vamos utilizar o Docker para facilitar a reprodução de nossas execuções. Então vamos criar uma estrutura de diretórios da seguinte maneira:

\- ./
\-\- sqlite3/
\-\-\- Dockerfile
\-\-\- create.sql

O conteúdo do arquivo "create.sql" será o seguinte:

```sql
CREATE TABLE Departament (
    id integer NOT NULL CONSTRAINT Departament_pk PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE Employee (
    id integer NOT NULL CONSTRAINT Employee_pk PRIMARY KEY,
    name varchar(255) NOT NULL,
    fk_departament_id integer NOT NULL,
    CONSTRAINT employee_departament FOREIGN KEY (fk_departament_id)
    REFERENCES Departament (id)
);

CREATE TABLE Project (
    id integer NOT NULL CONSTRAINT Project_pk PRIMARY KEY,
    name varchar(255) NOT NULL
);

CREATE TABLE WorksOn (
    Employee_id integer NOT NULL,
    Project_id integer NOT NULL,
    CONSTRAINT WorksOn_pk PRIMARY KEY (Employee_id,Project_id),
    CONSTRAINT WorksOn_Employee FOREIGN KEY (Employee_id)
    REFERENCES Employee (id),
    CONSTRAINT WorksOn_Project FOREIGN KEY (Project_id)
    REFERENCES Project (id)
);

INSERT INTO Departament VALUES (1, 'Sales');
INSERT INTO Departament VALUES (2, 'Technology');
INSERT INTO Departament VALUES (3, 'Marketing');

INSERT INTO Employee VALUES (1, 'John', 1);
INSERT INTO Employee VALUES (2, 'Ana', 2);
INSERT INTO Employee VALUES (3, 'Bruce', 3);
INSERT INTO Employee VALUES (4, 'Fred', 3);
INSERT INTO Employee VALUES (5, 'Ada', 2);
INSERT INTO Employee VALUES (6, 'Sara', 2);

INSERT INTO Project VALUES (1, 'Agile Transformation');
INSERT INTO Project VALUES (2, 'Sales up');

INSERT INTO WorksOn VALUES (2, 1);
INSERT INTO WorksOn VALUES (3, 1);
INSERT INTO WorksOn VALUES (4, 2);
INSERT INTO WorksOn VALUES (5, 1);
INSERT INTO WorksOn VALUES (6, 2);
INSERT INTO WorksOn VALUES (2, 2);
INSERT INTO WorksOn VALUES (3, 2);
```

Já o conteúdo do arquivo Dockerfile será:

```Dockerfile
FROM alpine:3.12

RUN apk add --update sqlite

COPY create.sql /

WORKDIR /database

RUN sqlite3 my_database.db < /create.sql && \
    rm /create.sql

ENTRYPOINT ["sqlite3"]
CMD ["my_database.db"]
```

Vamos testar nosso Dockerfile para checarmos se tudo esta correto:

```console
$ cd sqlite3

$ docker build -t sqlite3 .
Sending build context to Docker daemon  4.608kB
Step 1/7 : FROM alpine:3.12
...

$ docker run --rm -it sqlite3
sqlite> SELECT * FROM employee;
1|John|1
2|Ana|2
3|Bruce|3
4|Fred|3
5|Ada|2
6|Sara|2
```

Neste ponto já teremos nosso banco de dados pronto para realizarmos as consultas necessárias.

## Respostas com consultas SQL

Vamos recordar a pergunta:

  Quais são os projetos que cada departamento está inserido?

Analisando a pergunta chegamos a conclusão que o que desejamos como resultado é uma tabela com duas colunas, departamento e projeto. Sabemos de antemão que não existe um relacionamento direto entre a tabela departament e a tabela project, então necessariamente devemos passar pelas outras tabelas, employee e works_on.

Pelo modelo lógico sabemos que cada funcionário pode estar inserido em somente 1 departamento e 1 departamento pode ter N funcionários. Sabemos também que cada funcionário pode trabalhar em N projetos, assim como um projeto pode ter N funcionários.

Lembrando que todos os comandos SQL a seguir serão executados com o comando:

```console
$ docker run --rm -it sqlite3
sqlite3>
```

Sabendo desses fatos o caminho natural a se fazer nessa cadeia de relacionamentos é:

- Para cada departamento desejo saber quem são os funcionários.

```SQL
SELECT dp.name as Departament, em.name as Employee
FROM departament as dp
JOIN employee as em on dp.id = em.fk_departament_id;
```

- Para cada funcionário desejo saber em qual projeto ele está inserido.

```SQL
SELECT dp.name as Departament, pj.name as Project
FROM departament as dp
JOIN employee as em on dp.id = em.fk_departament_id
JOIN works_on as wo on em.id = wo.fk_employee_id
JOIN project as pj on wo.fk_project_id = pj.id;
```

Com essa última consulta, estamos com a resposta para nossa pergunta, porém com alguns valores duplicados.

```SQL
SELECT DISTINCT dp.name as Departament, pj.name as Project
FROM departament as dp
JOIN employee as em on dp.id = em.fk_departament_id
JOIN works_on as wo on em.id = wo.fk_employee_id
JOIN project as pj on wo.fk_project_id = pj.id
ORDER BY dp.name, pj.name;
```

Tudo certo agora, obtemos a resposta final:

| Departament | Project              |
|-------------|----------------------|
| Marketing   | Agile Transformation |
| Marketing   | Sales up             |
| Technology  | Agile Transformation |
| Technology  | Sales up             |

## Descrevendo a web semântica

O termo web semântica foi citado pela primeira vez em 2001 pelo então criador da World Wide Web, Tim Berners-Lee. A ideia por trás desta estrutura proposta é dar significado aos conteúdos publicados na web, isso permitiria que tanto humanos pudessem entender o sentido das construções textuais, como também as máquinas. Para isso foi proposto um framework composto de layers que juntos permitiriam chegar ao objetivo principal, fazer a máquina entender e processar um conjunto de palavras.

![Semantic Cake](/images/expondo-um-banco-relacional-como-endpoint-sparql/semantic-cake.jpg "Semantic Cake [Fonte: Wikipedia]")

Inúmeros recursos na internet podem ser consultados de modo a descrever com mais detalhes o mundo da web semântica, entre eles [a página da W3C sobre a web semântica](https://www.w3.org/standards/semanticweb/) ou o [artigo que deu origem ao termo](http://ww.wi-consortium.org/wicweb/pdf/wi-hendler.pdf).

A imagem acima representa o "semantic cake". Cada camada recorre à camada inferior, então para o entendimento completo do topo, é necessário o entendimento de toda sua base. Vamos explicar de maneira resumida alguns termos que usaremos no restante deste artigo.

Começando pela base, no primeiro nível, temos o URI, ele é a representação única de um recurso na web semântica. Em sua maioria das vezes ela é representada por uma URL, por exemplo, este artigo possui uma URI, que neste caso é a URL usada para acessá-lo. Lembrando que nem toda URI é uma URL, mas uma URL sempre é uma URI.

Namespace são nomes que representam um conjunto de recursos, provendo um nome único. Por exemplo, eu poderia ter um recurso descrito por "CadeiraDePalha" em um namespace chamado namespace_da_marca_A, e ao mesmo tempo, ter outro recurso chamado "CadeiraDePalha", porém com o namespace namespace_da_marca_B.

O XML é um formato estruturado de texto. Hoje você pode representar seus recursos estruturados em diversos formatos, entre eles estão o json-ld, turtle, n3, n-quads.

RDF é o acrônimo para Resource Description Framework, ele define um conjunto de regras para descrevermos as relações, que chamaremos de predicado, entre um sujeito e um objeto. A sequência sujeito predicado objeto chamaremos tripla. Observe que um conjunto de triplas representa um grafo. Por exemplo, o fragmento abaixo representa um grafo RDF em linguagem turtle.

Ontologia é um modelo formal para descrever um determinado domínio de informação. Nela podemos descrever classes, objetos e instâncias.

Abaixo um exemplo de uma representação em RDF, em formato turtle, de um grafo que representa uma pessoa chamada John que conhece uma pessoa chamada Fred.

```turtle
@base <http://www.example.org/> .

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<#john> rdf:type foaf:Person .
<#john> foaf:name "John" .
<#john> foaf:knows <#fred> .

<#fred> rdf:type foaf:Person .
<#fred> foaf:name "Fred" .
```

Em uma representação visual teríamos o seguinte grafo.

![Representação RDF em grafo](/images/expondo-um-banco-relacional-como-endpoint-sparql/rdf-graph.png)

## Criando nossa primeira ontologia

Precisamos criar um modelo formal para descrevermos nosso domínio de informação. Neste momento não nos preocuparemos com o reuso de ontologias existentes devido ao fato de não ser o foco do artigo. Esse modelo formal se chama ontologia e para a criação dela vamos usar a ferramenta [Protégé da Universidade de Stanford](https://protege.stanford.edu/).

Para entendermos melhor como iremos construir nossa ontologia, vamos voltar alguns passos atrás. Vamos converter o modelo lógico apresentado no começo deste artigo em um modelo conceitual.

![Modelo conceitual](/images/expondo-um-banco-relacional-como-endpoint-sparql/modelo_conceitual.png)

Observando o modelo conceitual identificamos 3 classes principais, employee, departament e project. O predicado entre a classe employee e departament será descrita por works_for e o predicado entre a employee e project será descrito por works_on.

Vamos entender um pouco a interface do Protégé. Já iremos definir nossa URI base como ```http://www.example.org/```.

![Interface principal do Protégé](/images/expondo-um-banco-relacional-como-endpoint-sparql/protege_interface_principal.png)

A próxima interface que iremos ver será a que criaremos as classes employee, departament e project.

![Interface de classes do Protégé](/images/expondo-um-banco-relacional-como-endpoint-sparql/protege_interface_classes.png)

Agora temos que criar nossos predicados, eles serão criados na aba objects properties.

![Objects Properties do Protégé](/images/expondo-um-banco-relacional-como-endpoint-sparql/protege_interface_object_propertiesl.png)

Vamos definir o domain e o range de cada predicado. O domain representa os recursos que podem ser sujeitos desse predicado e o range define quais objetos podem ser destino.

![Detalhes de domínios](/images/expondo-um-banco-relacional-como-endpoint-sparql/protege_interface_object_properties_details.png)

Para o predicado name o domain será todos as classes criadas anteriormente, porém o range será um datatype do tipo literal, ou seja, será uma string.

![Predicado name](/images/expondo-um-banco-relacional-como-endpoint-sparql/protege_interface_object_properties_details_name.png)

Por enquanto a ontologia que iremos usar será essa que acabamos de criar. A ontologia em formato turtle está representada abaixo.

```turtle
@prefix : <http://www.example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://www.example.org/> .

<http://www.example.org/> rdf:type owl:Ontology .

:name rdf:type owl:ObjectProperty ;
      rdfs:domain :departament ,
                  :employee ,
                  :project ;
      rdfs:range [ rdf:type owl:Restriction ;
                   owl:onProperty owl:topDataProperty ;
                   owl:someValuesFrom rdfs:Literal
                 ] .

:works_for rdf:type owl:ObjectProperty ;
           rdfs:domain :employee ;
           rdfs:range :departament .

:works_on rdf:type owl:ObjectProperty ;
          rdfs:domain :employee ;
          rdfs:range :project .

:departament rdf:type owl:Class .

:employee rdf:type owl:Class .

:project rdf:type owl:Class .
```

A ontologia acima pode ser salva em um arquivo .owl e ser carregada no Protégé. Voltaremos a ela mais tarde para criarmos uma regra de inferência e percebemos a vantagem de se usar ontologias.

# Mapeando o banco SQL para RDF com o R2RML

