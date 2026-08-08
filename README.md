# Blog Pessoal

Este repositório contém o código fonte do meu blog pessoal, que é gerado utilizando o Hugo, um gerador de sites estáticos. O blog está disponível em [josehisse.dev](https://www.josehisse.dev).

> Contribuindo com ajuda de um agente de código (Claude Code ou similar)? Veja [AGENTS.md](AGENTS.md) para convenções de conteúdo, comandos de build/verificação e o fluxo de PR.

## Tecnologias Utilizadas

- **Gerador de Site Estático:** [Hugo](https://gohugo.io/)
- **Hospedagem:** [Cloudflare Pages](https://pages.cloudflare.com/)
- **CI/CD:** [GitHub Actions](https://github.com/features/actions)
- **Qualidade de Código:**
  - [Pre-commit](https://pre-commit.com/)
  - [Markdownlint](https://github.com/DavidAnson/markdownlint)
  - [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) (executado via `markdownlint-cli2 --config .markdownlint.json "**/*.md" "#public" "#resources"`)
  - [Prettier](https://prettier.io/)
  - [lychee](https://github.com/lycheeverse/lychee) para checagem de links quebrados em `content/blog/**/*.md` (workflow semanal, abre issue automaticamente quando encontra um link quebrado)

## Estrutura do Repositório

- **.github/workflows**: Contém os workflows do GitHub Actions.
- **.markdownlint.json**: Configuração do markdownlint para garantir que os arquivos markdown sigam as regras de formatação desejadas.
- **.nojekyll**: Indica ao GitHub Pages para não usar o Jekyll ao construir o site.
- **.pre-commit-config.yaml**: Configuração para hooks de pre-commit, garantindo que certas verificações ou formatações sejam aplicadas antes dos commits.
- **.prettierrc.json**: Configuração para o Prettier, uma ferramenta de formatação de código.
- **hugo.yaml**: Arquivo de configuração do Hugo. Deve conter todas as configurações necessárias para o funcionamento do site.
- **archetypes**: Contém modelos para novos conteúdos. Útil para padronizar a criação de novos posts ou páginas.
- **assets**: Diretório para armazenar arquivos como CSS, JavaScript ou imagens que são processados pelo Hugo.
- **content**: Contém os posts do blog, cada um em sua própria pasta.
- **layouts**: Contém os templates do site.
- **static**: Diretório para arquivos estáticos que não precisam ser processados pelo Hugo, como imagens ou documentos.

## Configuração e Execução

Para executar o blog localmente, você precisa ter o Hugo instalado. Use o seguinte comando para iniciar o servidor local:

```bash
hugo server --buildDrafts --noHTTPCache --disableFastRender --buildFuture
```

## Convenções

- Todos os posts devem residir dentro do diretório `content/blog`.
- Cada post deve estar em sua própria pasta nomeada de forma descritiva (slug). Isso irá refletir o URL do post.
- O conteúdo do post deve estar em um arquivo `index.md` dentro da pasta do post.
- Todo post deve incluir o seguinte frontmatter no início do arquivo `index.md`:

  ```yaml
  ---
  title: "Título do Post"
  date: AAAA-MM-DD
  layout: post
  ---
  ```

- Título principal deve está no frontmatter. Demais títulos, h2, h3, devem ser colocados no conteúdo do post.
- As imagens devem ser colocadas em uma subpasta `images` dentro da pasta de cada post.
- Links para imagens dentro do Markdown devem usar o caminho relativo começando com `images/`. Exemplo: `![Descrição da Imagem](images/nome-da-imagem.png)`.
- Não é necessário converter imagens para WebP manualmente: o render hook `layouts/_default/_markup/render-image.html` gera WebP + fallback JPEG automaticamente no build (veja o post [Gerando imagens WebP com Hugo](content/blog/gerando-imagens-webp-com-hugo/index.md)).

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
