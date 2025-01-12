# Blog Pessoal

Este repositório contém o código fonte do meu blog pessoal, que é gerado utilizando o Hugo, um gerador de sites estáticos. O blog está disponível em [josehisse.dev](https://www.josehisse.dev).

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

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
