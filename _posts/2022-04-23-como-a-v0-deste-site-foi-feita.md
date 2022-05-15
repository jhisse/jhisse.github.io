---
title: Como a v0 deste site foi feita
date: 2022-04-23
layout: post
---

A seguir irei apresentar as decisões tomadas na construção deste blog e apresentar as principais tecnologias que foram utilizadas. Buscarei ao máximo descrever o por que de cada decisão tomada e explicar qual o pensamento por trás. Um aviso aqui é importante, se você estiver lendo este artigo em uma data futura a da publicação, ele pode não descrever mais a realidade do atual blog. 

## Objetivo do blog

O objetivo do blog é compartilhar com os leitores um pouco da minha maneira de pensar e meus principais aprendizados, aos quais envolvem assuntos diversos, quase sempre presentes no meu dia-a-dia. Assuntos simples ou complexos, sempre é um desafio explicar de forma clara cada etapa que compõem um pensamento que leva a determinada decisão. 

Por mais detalhado que seja o texto, ele nem sempre vai contemplar todos os detalhes. Por isso antes de publicar um artigo eu peço para que alguns amigos o leiam e me enviem feedbacks. Muitos deles reproduzem cada etapa descrita e indicam pontos que podem ser melhores explicados ou até suprimidos do texto original.

## Visual

O tema do blog foi pensado de forma que o conteúdo de cada artigo fique evidenciado. Por isso o estilo simples, sem muita variação de cores e formas.

![Rascunho do visual do blog](/images/como-a-v0-deste-site-foi-feita/visual.png)

Todas as páginas do blog possuem uma profundidade de no máximo 2 cliques. Isso quer dizer que para se chegar em qualquer página basta no máximo essa quantidade de cliques.

Abaixo podemos ver um diagrama simplificado da relação entre as páginas através dos links presentes nelas. Nela podemos observar a dinâmica de alguns cliques que podem ocorrer durante a navegação do site.

![Diagrama representando os links entre as páginas](/images/como-a-v0-deste-site-foi-feita/link-pages.png)

Na sequência apresentada abaixo podemos observar que podemos chegar em qualquer artigo através de no máximo 2 cliques. Seja partindo da home e escolhendo um artigo, que resulta em 1 clique. Indo de um artigo ao próximo ou ao anterior, resultando também em 1 clique. Ou de um artigo qualquer para outro qualquer, que neste caso passa pela home do blog, resultando em 2 cliques.

![Cenários possíveis de navegação entre as páginas](/images/como-a-v0-deste-site-foi-feita/link-pages-scenarios.png)

Outro destaque que vale a pena falar é a presença de diagramas visuais na maioria dos artigos. Sempre tento manter os diagramas os mais simples e lúdicos possíveis. Após ler o livro "The Back of the Napkin: Solving Problems and Selling Ideas with Pictures" de Dan Roam, me convenci ainda mais da importância de desenhar o problema ou a solução com formas elementares. Desta forma fica mais evidente a relação entre as peças que os compõem.

![Capa do livro "The Back of the Napkin"](/images/como-a-v0-deste-site-foi-feita/the_back_of_the_napkin.jpeg)

## Escrita

Seria ruim se cada artigo fosse escrito em HTML puro. Apesar de simples, não é uma forma muito elegante de escrever os textos. Nesse ponto fica claro que precisamos de uma outra linguagem de marcação para nos auxiliar.

Agora o Markdown entra na história. Ele foi pensado para ser mais enxuto e com uma melhor legibilidade do que o HTML. Com poucas regras de marcação, ele se tornou um padrão como forma de escrever texto em fóruns ou nos famosos *README.md* presentes nos repositórios git.

Ele possui algumas poucas regras, como utilizar `#`, `##`, `###` para representar cabeçalhos, neste caso ele será convertido para `<h1>`, `<h2>` e `<h3>` no HTML. Ou `![descrição da imagem](local da imagem)` para imagens, neste caso a conversão ficaria `<img alt="descrição da imagem" src="/local/da/imagem.jpg">`. Podemos perceber como a escrita vai ficando mais simples com o Markdown. 

Já que estamos escrevendo utilizando uma linguagem de marcação que o nosso navegador não entende, precisamos converter em HTML para que tudo seja renderizado corretamente para os visitantes do blog. Agora, precisamos introduzir um novo conceito, os geradores de sites estáticos, SSG.

![Markdown para HTML](/images/como-a-v0-deste-site-foi-feita/markdown2html.png)


## Geradores de sites estáticos

Neste ponto vale uma explicação do que é um site estático. Sabemos que tecnologias web não param de surgir e serem aperfeiçoadas, porém ainda podemos recorrer ao básico em algumas situações. Neste caso vamos recorrer ao trio HTML, CSS e Javascript. O site estático é composto basicamente por esses três componentes, servindo para entregar ao visitante uma página web simples e sem muita iteração.

Por outro lado o site dinâmico possui algum sistema gerenciador de conteúdo, mais conhecido como CMS. Alguns exemplos são o Wordpress ou o Joomla. Diferente do CMS, não irá existir um banco de dados em nossa stack, nem uma linguagem de backend que irá servir conteúdos mais dinâmicos e complexos para os usuários. Teremos apenas texto puro e imagens pré-processados.

Os geradores de sites estáticos funcionam como uma espécie de pré-processador. Convertendo arquivos em algum formato especifico, como o Markdown e templates com lógicas embutidas em arquivos HTML estáticos.

![Gerador de site estático](/images/como-a-v0-deste-site-foi-feita/diagrama-ssg.png)

No site [Jamstack](https://jamstack.org/generators/) podemos encontrar uma lista extensa de geradores de sites estáticos. Neste blog utilizamos o [Jekyll](https://jekyllrb.com), pelo menos até o momento que este artigo está sendo escrito.

O que o Jekyll faz é transformar arquivos Markdown e de templates em HTML já processado, como se fosse um processo de compilação. Ele é escrito em Ruby e precisa ser instalado. Nessa altura você deve estar se perguntando por que a escolha dele e não de outros já que há muitas opções. A resposta é simples, o Github Pages já tem suporte para ele. 

## Hospedagem

Desde o começo do blog tivemos a hospedagem gratuita. Isso aconteceu de uma maneira fácil já que somente arquivos estáticos seriam servidos aos usuários.

Existem muitas opções disponíveis quando falamos de hospedagem de sites estáticos como o Github pages, Gitlab Pages, S3, Netlify ou Cloudflare. Todos eles cumprem o que se propõem, porém no inicio do blog eu optei pelo mais lógico. O blog já estava sendo versionado no Github então o que fez mais sentido a época era usar o Github Pages.

O Github Pages entrega um domínio `.github.io` para seu site estático. Desta forma não há a necessidade de ter um domínio próprio.

No começo, o blog não havia o domínio <josehisse.dev>, somente o padrão. Depois houve a compra do domínio e como o Pages permite configurar um customizado ao qual você seja o dono, bastou configurar um CNAME no registro de nome de domínios.

Vale um destaque sobre os domínios `.dev`. Comprado pelo Google em 2015 e disponibilizado para compra pelo público somente em março de 2019, ele só permite conexões seguras, https, pelos navegadores. Essa funcionalidade se chama pré-carregamento de HSTS, [preloaded HSTS](https://hstspreload.org/?domain=josehisse.dev). O link que apresentamos anteriormente corresponde a uma lista dinâmica contendo os domínios que devem responder as requisições de forma segura pelos navegadores. Toda vez que consultamos um site `.dev` em um navegador moderno como o Chrome, Firefox, EDGE ou Safari, ele consulta essa lista e verifica se o site que estamos tentando acessar está na lista, caso esteja presente, o usuário que fez a solicitação da página web sempre será redirecionado pelo navegador para utilizar a versão segura https. No artigo [HSTS - a no-nonsense guide](https://www.steveworkman.com/2016/hsts-a-no-nonsense-guide/) de Steve Workman há muitos mais detalhes sobre preloaded HSTS e uma explicação muito mais aprofundada de como os redirecionamentos para a versão segura funcionam.

## Adicionais

### MathJax

Em "[Sequência de Collatz]({% post_url 2019-10-08-sequencia-de-collatz %})" tive a necessidade de usar fórmulas matemáticas durante a escrita. Para uma melhor representação gosto de utilizar o LaTeX para escreve-las. Nesse ponto há algumas opções para renderizar a fórmula na tela do leitor.

Uma das opções era transformar a fórmula escrita em LaTeX para imagem e colocá-la no artigo. Não considerei essa opção por ter que gerar a imagem para cada fórmula e gerar um possível aumento de tamanho das páginas, consequentemente aumentando o tempo de carregamento delas. A outra opção é carregar uma pequena biblioteca javascript que irá renderizar as fórmulas em LaTeX no momento que o leitor carregar a página.

Para evitarmos sobrecarregar o site adicionando uma biblioteca javascript, vamos adicioná-la somente as páginas que precisam renderizar as fórmulas. Para indicarmos ao Jekyll quais as páginas que necessitam dessa biblioteca vamos utilizar um atributo no topo de cada artigo e um pequeno trecho do template Liquid.

No topo de cada arquivo markdown que representa os textos há um cabeçalho. Nesse cabeçalho existe informações de título do artigo, data da publicação, o layout que ele irá utilizar e por fim acrescentamos uma nova informação, se haverá o carregamento ou não da biblioteca MathJax.

```markdown
---
title: Sequência de Collatz
date: 2019-10-12
layout: post
mathjax: true
---
```

Não vou entrar em maiores detalhes sobre o template Liquid que o Jekyll utiliza, porém no trecho a seguir da para perceber um pouco a sua sintaxe. No trecho há uma pequena instrução condicional, que caso na página tenha o atributo mathjax como true, então ele irá adicionar a biblioteca ou não no HTML final.

```html
  {% if page.mathjax %}
  <script>
    MathJax = {
      tex: {
        inlineMath: [
          ['\\(', '\\)']
        ],
        displayMath: [
          ['$$', '$$'],
          ['\\[', '\\]']
        ],
        processEscapes: true
      }
    };
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3.0.0/es5/tex-mml-chtml.js"></script>
  </script>
  {% endif %}
```

### Syntax highlighting

Na maioria dos artigos desse blog há trechos de códigos nas mais diversas linguagens. Há trechos de dockerfile, yaml, python, r entre outros que precisam ter um destaque para a sintaxe. Isso vai dar ao leitor uma melhor experiência na leitura. 

Para o syntax highlight, utilizo o [highlightjs](https://highlightjs.org). No site é possível escolher 

## Otimização do site estático



## Considerações finais

As decisões que foram tomadas e a arquitetura apresentada podem não refletir o estado atual do site. Muitas dessas decisões podem, foram ou serão revistas conforme o meu pensamento for mudando.