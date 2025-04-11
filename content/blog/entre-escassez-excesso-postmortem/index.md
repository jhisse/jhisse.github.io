---
title: Entre a escassez e o excesso de postmortems
date: 2025-04-11
layout: post
---

## Introdução

> Este dispositivo falhará. A questão não é se falhará, mas quando falhará. [...] Sempre tenha um plano para lidar com as falhas.
>
> — Trecho do manual do Shearwater Swift Air Transmitter

O trecho que acabamos de ler foi extraído do manual de um dispositivo de medição de ar em cilindros de mergulho. Quando o li pela primeira vez achei um tanto preocupante; um dispositivo que mede a quantidade de ar que resta em um mergulho não deveria ser à prova de falhas? No entanto, é óbvio que o dispositivo falhará em algum momento, isso é inevitável. Nenhum dispositivo ou sistema é imune a falhas. O que importa é o quanto você estará preparado para lidar com essa falha e o que você aprenderá caso o incidente aconteça. O princípio que ele transmite é universal: falhas e incidentes são inevitáveis, mas o que importa é como respondemos a elas e como nos preparamos para lidar com elas antes que aconteçam.

Em ambientes de tecnologia, falhas e incidentes são inevitáveis. À medida que sistemas crescem em escala e complexidade, a probabilidade de problemas também aumenta proporcionalmente. O desafio não está em evitar completamente as falhas – algo praticamente impossível – mas em aprender com elas e evitar recorrências do mesmo problema. É neste contexto que postmortems surgem como ferramentas essenciais.

Um postmortem é, em sua essência, um registro detalhado de um incidente, documentando seu impacto, as ações tomadas para mitigá-lo, as causas-raiz identificadas e, crucialmente, as lições aprendidas e ações preventivas planejadas. Entretanto, um dilema frequente nas organizações é determinar exatamente quando um postmortem é necessário. Fazer postmortems em excesso pode consumir recursos valiosos e potencialmente diluir sua importância; por outro lado, realizá-los com escassez significa perder oportunidades valiosas de aprendizado e melhoria.

Reuni alguns artigos de grandes empresas, que estão na vanguarda da cultura de DevOps: Google, Hosted Graphite, PagerDuty, Eficode, Datadog e Atlassian. Iremos analisar os critérios utilizados por elas para determinar quando fazer um postmortem, os benefícios desta prática quando aplicada corretamente e as estratégias para implementar um processo de postmortem eficiente que maximize o aprendizado por todos os colaboradores.

## Postmortems não são apenas documentos

Antes de discutir quando realizar um postmortem, devemos compreender que postmortems eficazes não são apenas documentos isolados. Eles representam o aprendizado contínuo e a melhoria constante. Uma cultura de postmortem saudável para uma empresa e seus colaboradores está fundamentada em princípios bem definidos.

> Blameless postmortems are a tenet of SRE culture.
>
> -- Google [1]

O primeiro deles é a ausência de culpa, isso significa que o foco deve estar nas causas que contribuíram para o incidente, não em apontar dedos e atribuir culpa para pessoas ou times específicos. Complementando esse ponto, a Eficode destaca a importância da segurança psicológica nesse processo, evitando que incidentes sejam ocultados por medo da culpa [4].

> A well-documented incident is invaluable because it includes not only a description of what happened but of what actions we took and the things we believed to be true at the time.
>
> -- Hosted Graphite [2]
>
> Your postmortems need to be living documents that enable readers to have conversations, get additional context, and refine their root-cause analysis
>
> -- Datadog [5]

O segundo princípio é o compromisso com a documentação detalhada. Esta documentação serve como referência vital para responder a incidentes futuros e para o aprendizado contínuo. Além disso, a Datadog pontua que os postmortems devem ser documentos vivos e dinâmicos, permitindo a troca de informações entre as partes envolvidas. Esses contextos nos levam ao terceiro princípio.

> The primary purpose of postmortems should be learning.
>
> -- PagerDuty [3]

O terceiro princípio é o foco na aprendizagem e melhoria contínua. Como observado pela PagerDuty (Quem já acordou com um alerta "PagerDuty Alert"?). Se uma equipe não está extraindo novos aprendizados de seus incidentes, então algo está errado e o processo de aprendizado está comprometido.

Quando estes princípios estão bem estabelecidos entre todas as equipes, a decisão sobre quando realizar um postmortem se torna mais clara e intuitiva.

## Critérios para realização de postmortems

Um dos principais desafios para as empresas é estabelecer critérios claros e objetivos para determinar quando um postmortem deve ser realizado ou não. Segundo a Eficode, empresa finlandesa fundada em 2005 com foco em implementar cultura DevOps, o processo de investigação e escrita de um postmortem tem um custo relativamente alto para a equipe. Portanto, os extremos, o excesso e a escassez, devem ser evitados.

> It's definitely worth acknowledging that a good postmortem process does present an inherent cost in terms of time and/or effort, so you need to be deliberate in choosing when to write one.
>
> -- Eficode [4]

O Google sugere que um dos principais gatilhos para postmortems é o impacto ao usuário - "User-visible downtime or degradation beyond a certain threshold" [1]. Este critério coloca o impacto na experiência do usuário como fator primordial. A Eficode expande este critério, sugerindo métricas bem definidas, como "x+ users impacted" [4]. Estes critérios quantificáveis ajudam a remover a subjetividade da decisão.

Além do impacto direto no negócio, a recorrência do incidente também pode justificar um postmortem. A Hosted Graphite pontua: "If you think an incident is "too common" to get its own postmortem that's a good indicator that there's a deeper issue that we need to address" [2], ou seja, incidentes frequentes indicam que algo merece mais atenção e um deep dive no problema deve ser feito.

Um critério frequentemente subestimado é o potencial de aprendizado. A Eficode sugere que mesmo incidentes menores podem justificar postmortems quando apresentam um alto valor a ser aprendido, "... where there's a high value in sharing what was learned." [4].

Este critério reconhece que o valor de um postmortem não está apenas na prevenção de novos incidentes do mesmo tipo, mas como PagerDuty destaca: "Delaying the postmortem delays key learning that will prevent the incident from recurring." [3], ou seja, o aprendizado é o fator mais importante, pois ele previne recorrências.

Outro fator prático a considerar é o nível de severidade definido pela empresa. Atlassian sugere que "We carry out postmortems for severity 1 and 2 incidents. Otherwise, they're optional." [6], da mesma forma, PagerDuty "Teams should conduct a postmortem after every major incident" [3]. Os critérios de severidade dos incidentes devem ser previamente definidos pela empresa para que não haja dúvida na decisão de realizar ou não um postmortem.

## Definir critérios antecipadamente

Um tema recorrente em todas as fontes consultadas é a importância de definir critérios para postmortems antes que os incidentes ocorram.

> It is important to define postmortem criteria before an incident occurs so that everyone knows when a postmortem is necessary.
>
> -- Google [1]

Quando os critérios são estabelecidos antecipadamente, as equipes podem focar na resolução do incidente, sabendo que o processo de reflexão e aprendizado ocorrerá em seguida.

A importância desses critérios serem revisados periodicamente não pode ser subestimada. Mudanças acontecem constantemente e times ágeis devem estar em melhoria contínua, o que implica em reavaliar regularmente os critérios de postmortem.

> What matters is that these criteria are defined in the first place and periodically revisited.
>
> -- Eficode [4]

À medida que softwares e plataformas evoluem, novos tipos de falhas podem surgir. Critérios que eram adequados para determinado contexto, tamanho da equipe e complexidade de sistemas, já podem não ser ideais para o novo contexto.

## Escassez de postmortems

A escassez de postmortems, ou seja, realizar menos análises do que o necessário, apresenta riscos significativos. Quando incidentes de grande impacto não são adequadamente analisados e documentados, padrões podem passar despercebidos e as mesmas falhas podem se repetir.

Um dos principais riscos é a perda, ou possível perda, de conhecimento. Como a Hosted Graphite enfatiza "It allows us to document the incident, ensuring that it won't be forgotten." [2]. Sem esta documentação, o conhecimento adquirido no processo de resolução permanece isolado na memória de quem o fez, tornando-o vulnerável ao esquecimento.

O objetivo fundamental de um postmortem é prevenir a recorrência do mesmo incidente. Ainda a Hosted Graphite cita "... we'll be fighting fires every day, and that's no fun" [2]. A escassez de postmortems pode gerar um ambiente de constante reação a incidentes e não permitir que o time atue na causa raiz de fato.

Postmortems detalhados frequentemente revelam oportunidades para melhorias. Por outro lado, é de conhecimento geral que o time gasta uma grande parte do tempo escrevendo postmortems. Como a Datadog observa, "... generate interactive postmortem documents automatically, you can let your team spend less time on writing and more time on finding clues - and preventing future incidents." [5]. Portanto, eles devem ser escritos sim, porém o tempo gasto em postmortems deve ser minimizado.

Embora a escassez de postmortems possa levar à perda de conhecimento e recorrência de incidentes, também precisamos estar atentos ao extremo oposto. Não podemos nos exceder com uma quantidade excessiva de documentos, o que nos leva à outra mão de uma mesma via.

## Excesso de postmortems

Embora a escassez de postmortems apresente riscos claros, o excesso também pode ser prejudicial. Postmortems bem documentados exigem tempo e esforço significativo. A afirmação ".. a good postmortem process does present an inherent cost in terms of time and/or effort ..." [4] deixa isso muito evidente. Quando postmortems são realizados para incidentes triviais e sem impacto significativo ou potencial aprendizado, o tempo gasto em tais processos pode ser considerado desperdiçado.

Um outro risco do excesso é a fadiga dos colaboradores, similar ao conceito de "alert fatigue" documentado pela Atlassian. Como eles explicam, "Alert fatigue is when an overwhelming number of alerts desensitizes the people tasked with responding to them" [8]. Da mesma forma, quando o colaborador é constantemente interrompido por incidentes e para escrita de postmortems, as pessoas podem se tornar indiferentes. O time pode se sentir sobrecarregado com suas tarefas diárias, a resposta aos incidentes e ainda o processo de investigação e escrita de postmortems. Quando postmortems se tornam uma formalidade burocrática em vez de uma oportunidade de aprendizado, seu valor é reduzido.

Uma solução prática para o excesso de postmortems, conforme sugerido pela Eficode, é o agrupamento de incidentes similares: "Another idea could be to group multiple small incidents that have a similar nature, into one postmortem for resolution, rather than writing one for each smaller incident" [4]. Esta abordagem permite que as equipes identifiquem padrões entre incidentes menores e extraiam aprendizados valiosos sem o custo de realizar processos completos para cada ocorrência. Ao consolidar incidentes semelhantes, as organizações podem manter o valor do processo de postmortem enquanto reduzem significativamente o esforço necessário para a escrita.

## Conclusão

A questão sobre quando realizar postmortems não tem resposta única, definitiva ou certa. O espaço entre escassez e excesso é um vale que, ora estamos tendenciosos para um lado e ora estamos tendenciosos para outro. Influenciada pelo contexto, maturidade, complexidade e objetivos, os critérios devem ser ajustados de forma contínua a fim de buscarmos um equilíbrio, como a Eficode [4] observou e bem pontuou.

O valor dos postmortems está, principalmente, em seu potencial como ferramentas de aprendizado, onde incidentes são transformados em oportunidades de crescimento. Empresas podem e vão navegar no vale entre escassez e excesso, mas isso não impede que ajustes nos critérios sejam feitos. Por fim, o sucesso não está na balança totalmente equilibrada, mas na capacidade de aprender consistentemente com falhas inevitáveis e efetuar ajustes quando necessário.

## Referências

[1] Google SRE. "Postmortem Culture: Learning from Failure". Site Reliability Engineering, 2016. Disponível em: <https://sre.google/sre-book/postmortem-culture/>. Acesso em: 11 abr. 2025.

[2] Hosted Graphite. "It's dead, Jim: How we write an incident postmortem", 2019. Disponível em: <https://www.hostedgraphite.com/blog/its-dead-jim-how-we-write-an-incident-postmortem>. Acesso em: 11 abr. 2025.

[3] PagerDuty. "Postmortems", 2021. Disponível em: <https://postmortems.pagerduty.com/>. Acesso em: 11 abr. 2025.

[4] Eficode. "Blameless Postmortem Culture", 2021. Disponível em: <https://www.eficode.com/blog/blameless-postmortem-culture>. Acesso em: 11 abr. 2025.

[5] Datadog. "Best Practices for Writing Incident Postmortems", 2021. Disponível em: <https://www.datadoghq.com/blog/incident-postmortem-process-best-practices/>. Acesso em: 11 abr. 2025.

[6] Atlassian. "Who completes the postmortem?". Disponível em: <https://www.atlassian.com/incident-management/handbook/postmortems#who-completes-the-postmortem>. Acesso em: 11 abr. 2025.

[7] Atlassian. "Incident Management Handbook". Disponível em: <https://www.atlassian.com/incident-management/handbook>. Acesso em: 11 abr. 2025.

[8] Atlassian. "Understanding and fighting alert fatigue". Disponível em: <https://www.atlassian.com/incident-management/on-call/alert-fatigue>. Acesso em: 11 abr. 2025.
