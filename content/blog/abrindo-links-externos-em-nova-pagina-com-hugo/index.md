---
title: Abrindo links externos em nova página com Hugo
date: 2025-02-11
layout: post
---

Neste post, vamos ver como identificar links externos em posts em Markdown e renderizar os links em HTML para que sejam abertos em uma nova página. Esse recurso melhora a experiência do usuário, mantendo seu blog aberto enquanto o leitor acessa links para outros domínios.

## Como o Hugo renderiza links

O Hugo utiliza o que ele chama de [render hooks](https://gohugo.io/render-hooks/) para customizar a forma como os links são renderizados. Para alterar o comportamento padrão de links, basta criar um render hook personalizado, nesse caso, `layouts/_default/_markup/render-link.html`.

## Render Hook default para links

Como estamos utilizando a versão 0.143.1 do Hugo, o render hook padrão pode ser encontrado no arquivo _[tpl/tplimpl/embedded/templates/_default/_markup/render-link.html](https://github.com/gohugoio/hugo/blob/v0.143.1/tpl/tplimpl/embedded/templates/_default/_markup/render-link.html)_ no repo oficial do Hugo no Github. Seu conteúdo é o seguinte:

```html
{{- $u := urls.Parse .Destination -}}
{{- $href := $u.String -}}
{{- if strings.HasPrefix $u.String "#" -}}
  {{- $href = printf "%s#%s" .PageInner.RelPermalink $u.Fragment -}}
{{- else if and $href (not $u.IsAbs) -}}
  {{- $path := strings.TrimPrefix "./" $u.Path -}}
  {{- with or
    ($.PageInner.GetPage $path)
    ($.PageInner.Resources.Get $path)
    (resources.Get $path)
  -}}
    {{- $href = .RelPermalink -}}
    {{- with $u.RawQuery -}}
      {{- $href = printf "%s?%s" $href . -}}
    {{- end -}}
    {{- with $u.Fragment -}}
      {{- $href = printf "%s#%s" $href . -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
<a href="{{ $href }}" {{- with .Title }} title="{{ . }}" {{- end }}>{{ .Text }}</a>
{{- /**/ -}}
```

Vamos explicar esse hook passo a passo, mas antes vamos entender quais componentes compões um link em Markdown.

```plain
[Post 1](/posts/post-1 "My first post")
 ------  -------------  -------------
  Text    Destination       Title
```

Este exemplo acima, que foi retirado da documentação oficial do Hugo, `Text` representa o texto do link, `Destination` representa o destino do link e `Title` representa o atributo `title` do link, sendo este opcional.

1. `{{- $u := urls.Parse .Destination -}}`
    Converte o valor de `.Destination` em um objeto URL através da função `urls.Parse`, permitindo manipulação estruturada da URL.

2. `{{- $href := $u.String -}}`
    Inicializa a variável `$href` com a representação em string da URL, que servirá de base para o atributo `href` do link.

3. `{{- if strings.HasPrefix $u.String "#" -}}`
    Verifica se a URL começa com o caractere `#`, indicando um link âncora. Um link âncora é um link que aponta para um fragmento dentro da mesma página.

4. `{{- $href = printf "%s#%s" .PageInner.RelPermalink $u.Fragment -}}`
    Se for uma âncora, modifica `$href` para concatenar o caminho relativo da página com o fragmento da âncora.

5. `{{- else if and $href (not $u.IsAbs) -}}`
    Caso o link não seja uma âncora, verifica se a URL é relativa (não absoluta). A função `isAbs` verifica se uma URL começa com `http` ou `https`, indicando que é uma URL absoluta, caso contrário, seria uma URL relativa.

6. `{{- $path := strings.TrimPrefix "./" $u.Path -}}`
    Remove o prefixo "./" do caminho relativo, caso possua, padronizando o valor do caminho relativo.

7. `{{- with or ($.PageInner.GetPage $path) ($.PageInner) (resources.Get $path)-}}`
    Tenta localizar uma página ou recurso que corresponda ao caminho fornecido.

8. `{{- $href = .RelPermalink -}}`
    Se um recurso for encontrado na instrução anterior, atualiza `$href` para o link relativo desse recurso.

9. `{{- with $u.RawQuery -}}`
    Se a URL original contiver uma query string, inicia um bloco para tratar esse parâmetro.

10. `{{- $href = printf "%s?%s" $href . -}}`
    Anexa a query string ao `href` através da função `printf`.

11. `{{- end -}}`
    Finaliza o bloco de tratamento da query string.

12. `{{- with $u.Fragment -}}`
    Se houver uma âncora (parte após "#") na URL, inicia um bloco para adicioná-lo.

13. `{{- $href = printf "%s#%s" $href . -}}`
    Inclui a âncora no `href`, preservando as referências.

14. `{{- end -}}`
    Finaliza o bloco do tratamento da âncora em links relativos.

15. `{{- end -}}`
    Conclui o bloco que busca e atualiza o recurso relativo.

16. `{{- end -}}`
    Finaliza a condição que trata links relativos.

17. `<a href="{{ $href }}" {{- with .Title }} title="{{ . }}" {{- end }}>{{ .Text }}</a>`
    Gera o elemento HTML `<a>`, definindo o atributo `href` com o valor processado e adiciona o atributo `title` se especificado.

18. `{{- /**/ -}}`
    Usado como um indicativo do fim do template.

### Exemplos com o hook default

Vamos mostrar três exemplos de como representamos um link em Markdown e como ele renderiza em HTML, um para cada tipo de link:

1. Âncora para mesma página

    `[Exemplos](#Exemplos)`: `<a href="/blog/abrindo-links-externos-em-nova-aba-com-hugo/#Exemplos">Exemplos</a>`

2. Link interno com caminho relativo e âncora

    `[Render Hook para Imagem](./gerando-imagens-webp-com-hugo/#render-hook-para-imagem)`: `<a href="/blog/gerando-imagens-webp-com-hugo/#render-hook-para-imagem">Render Hook para Imagem</a>`

3. Link externo

    `[Git deste site](https://github.com/jhisse/jhisse.github.io)`: `<a href="https://github.com/jhisse/jhisse.github.io">Git deste site</a>`

## Atributos `target` e `rel`

Podemos observar nos exemplos anteriores que todos os links renderizam de forma semelhante, apenas mudando o destino do link. Porém, vamos introduzir dois novos atributos ta tag `a`: `target` e `rel`.

O atributo `target="_blank"` abre o link em uma nova aba/página. Essa configuração permite que o usuário permaneça em seu site enquanto acessa o link externo. Isso melhora também a experiência do usuário, pois o visitante não precisa navegar para trás se quiser retornar ao seu site, ele fica aberto em uma aba/página. Outra vantagem é manter o usuário na página atual, evitando que ele saia do site.

O atributo `rel="noreferrer noopener"` é utilizado por questões de segurança. Esses atributos evitam que a página aberta acesse a página de origem via a propriedade `window.opener`, mitigando riscos de ataques como o "[reverse tabnabbing](https://securityintelligence.com/posts/what-is-reverse-tabnabbing-and-what-can-you-do-to-stop-it/)", além de impedir que o browser envie informações de referência para o site externo.

## Render Hook personalizado

O Render Hook do Hugo permite personalizar a forma como os links são renderizados. Para isso, basta criar um arquivo em `layouts/_default/_markup/render-link.html` e personalizar para que ele adicione os atributos `target="_blank"` e `rel="noopener noreferrer"` em links externos.

Basta substituir `<a href="{{ $href }}" {{- with .Title }} title="{{ . }}" {{- end }}>{{ .Text }}</a>` pelo seguinte conteúdo:

```html
<a href="{{ $href }}"
  {{- with .Title }} title="{{ . }}"{{- end }}
  {{- if $u.IsAbs }} target="_blank" rel="noreferrer noopener"{{- end -}}
>{{ .Text }}</a>
```

A única mudança feita no template default é adicionar `{{- if $u.IsAbs }} target="_blank" rel="noreferrer noopener"{{- end -}}` na tag `a`. Isso verifica se o link é absoluto ou relativo com `$u.IsAbs` e, se for absoluto, o atributo `target="_blank"` e `rel="noreferrer noopener"` são adicionados, caso contrário, o link permanece sem os novos atributos.

O conteúdo completo do render hook personalizado é o seguinte:

```html
{{- $u := urls.Parse .Destination -}}
{{- $href := $u.String -}}
{{- if strings.HasPrefix $u.String "#" -}}
  {{- $href = printf "%s#%s" .PageInner.RelPermalink $u.Fragment -}}
{{- else if and $href (not $u.IsAbs) -}}
  {{- $path := strings.TrimPrefix "./" $u.Path -}}
  {{- with or
    ($.PageInner.GetPage $path)
    ($.PageInner.Resources.Get $path)
    (resources.Get $path)
  -}}
    {{- $href = .RelPermalink -}}
    {{- with $u.RawQuery -}}
      {{- $href = printf "%s?%s" $href . -}}
    {{- end -}}
    {{- with $u.Fragment -}}
      {{- $href = printf "%s#%s" $href . -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
<a href="{{ $href }}"
  {{- with .Title }} title="{{ . }}"{{- end }}
  {{- if $u.IsAbs }} target="_blank" rel="noreferrer noopener"{{- end -}}
>{{ .Text }}</a>
{{- /**/ -}}
```

### Exemplos com hook personalizado

Vamos testar os mesmos links do exemplo anterior para ver o resultado:

1. Âncora para mesma página

    `[Exemplos](#Exemplos)` -> `<a href="/blog/abrindo-links-externos-em-nova-aba-com-hugo/#Exemplos">Exemplos</a>`

2. Link interno com caminho relativo e âncora

    `[Render Hook para Imagem](./gerando-imagens-webp-com-hugo/#render-hook-para-imagem)` -> `<a href="/blog/gerando-imagens-webp-com-hugo/#render-hook-para-imagem">Render Hook para Imagem</a>`

3. Link externo

    `[Git deste site](https://github.com/jhisse/jhisse.github.io)` -> `<a href="https://github.com/jhisse/jhisse.github.io" target="_blank" rel="noreferrer noopener">Git deste site</a>`

### Considerações Finais

Ao realizar mudanças no `render-link.html` do Hugo, você pode melhorar a usabilidade e segurança dos links. Ajuda a reter o leitor em seu blog garantindo que ele permanece na mesma página enquanto navega em links externos. Com o atributo `rel="noreferrer noopener"`, você evita brechas de segurança, como o "reverse tabnabbing".
