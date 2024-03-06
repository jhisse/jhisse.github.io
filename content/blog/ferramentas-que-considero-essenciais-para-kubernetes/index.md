---
title: Ferramentas que considero essenciais para Kubernetes
date: 2024-03-04
layout: post
---

O Kubernetes tem se tornado uma plataforma de orquestração de contêineres cada vez mais essencial para equipes de desenvolvimento em todo o mundo. Apesar das facilidades que a plataforma proporciona para a execução de aplicações, gerenciar clusters Kubernetes pode se revelar uma tarefa complexa. Desafios como depurar aplicações, monitorar recursos e logs exigem ferramentas adequadas e um conhecimento aprofundado para serem superados com eficiência.

Este post tem o objetivo de compartilhar não as ferramentas mais populares, mas sim aquelas que, na minha experiência, se mostraram essenciais para o cotidiano de quem trabalha com Kubernetes. A seleção que apresentarei é fruto da experiência que adquiri no decorrer dos anos, durante os quais busquei otimizar meu tempo e aumentar a eficiência no gerenciamento de clusters Kubernetes.

Nas próximas linhas, descreverei cada uma dessas ferramentas essenciais e como elas podem ser úteis no dia a dia. Além disso, compartilharei um pouco sobre como utilizo cada uma delas na prática. Para ilustrar suas aplicações, utilizarei dois clusters locais gerenciados pelo Kind, denominados cluster1 e cluster2, servindo como exemplos práticos de suas funcionalidades e benefícios.

---

TL;DR: As ferramentas que considero essenciais para Kubernetes são:

1. [kind](https://kind.sigs.k8s.io)
2. [kubectx e kubens](https://github.com/ahmetb/kubectx)
3. [stern](https://github.com/stern/stern)
4. [kube-score](https://github.com/zegl/kube-score)
5. [kube-capacity]()
6. [kubescape]()
7. [kubeshark]()

---

## kind

Por diversas vezes tenho a necessidade de testar alguma aplicação nova ou preciso simular os impactos que determina atualização pode causar em um cluster Kubernetes. O Kind permite que eu possa criar cluster locais em questão de minutos, o que me permite testar e validar cenários de forma rápida e eficiente.

Veja o exemplo abaixo onde crio um cluster chamado cluster1 e outro chamado cluster2:

```bash
kind create cluster --name cluster1
kind create cluster --name cluster2
kind get clusters
```

![kind](images/kind.png)

O Kind cria clusters locais usando contêineres Docker como nós, o que torna a criação e destruição de clusters extremamente rápidas. Além disso, podemos carregar imagens locais para os clusters, basta executar o comando `kind load docker-image <image-name> --name cluster1` para carregar a imagem no cluster1.

## kubectx e kubens

Mudar de contexto muitas vezes pode ser uma tarefa tediosa, principalmente quando estamos lidando com múltiplos clusters como é o caso acima. Imagine toda vez que quiser mudar de contexto você precisar executar o comando `kubectl config use-context kind-cluster1` para começar a trabalhar no cluster1 ou `kubectl config use-context kind-cluster2` para alterarmos o contexto para o cluster2. E se não lembrarmos os nomes dos clusters? Devemos executar o comando `kubectl config get-contexts` para listar todos os contextos disponíveis e depois escolher o contexto desejado.

![kubectx](images/use-context.png)

Neste ponto que entra o kubectx, com ele podemos listar todos os contextos disponíveis e mudar de contexto de forma rápida e eficiente. Veja, com o comando `kubectx` podemos listar todos os contextos disponíveis e com o comando `kubectx kind-cluster1` podemos mudar para o contexto do cluster1, assim como `kubectx kind-cluster2` para mudar para o contexto do cluster2. Muito mais fácil de lembrar e executar, não?

![kubectx](images/kubectx.png)

E que tal listar os namespaces do cluster1? Para isso usaremos o comando `kubectl get namespaces`. Verificamos com o comando `kubectl config view --minify --output 'jsonpath={..namespace}'` que estamos no namespace default, ou seja, a saída será em branco. Vamos alterar nosso namespace de trabalho para o namespace kube-system com o comando `kubectl config set-context --current --namespace=kube-system`. Verificando com o comando `kubectl config view --minify --output 'jsonpath={..namespace}'` que agora estamos no namespace kube-system e em segguida listamos os pods do namespace kube-system com o comando `kubectl get pods`, para confirmar que estamos no namespace correto.

![Change context with kubectx](images/change-namespace.png)

O kubens funciona da mesma maneira que o kubectx, mas ao invés de mudar de contexto, ele muda de namespace. Com o comando `kubens` podemos listar todos os namespaces disponíveis e com o comando `kubens kube-system` podemos mudar para o namespace kube-system, assim como `kubens default` para mudar para o namespace default.

![Change namespace with kubens](images/kubens.png)

## stern

Podemos facilmente obter os logs de um pod especifico com o comando `kubectl logs <pod-name>`, mas se precisarmos obter os logs de vários pods em simultâneo? Ou mesmo de múltiplos containers no mesmo pod? Este comando não nos atenderá nesse caso. O Stern é uma ferramenta que nos permite obter os logs de vários pods ou containers em simultâneo, o que é extremamente útil quando precisamos depurar múltiplas aplicações.

Vamos fazer um pequeno experimento com um pod que contêm dois containers. Ambos os containers irão gerar logs diferentes. Desta forma poderemos visualizar a limitação que temos ao usar o comando `kubectl logs <pod-name>`. Antes de mais nada, não esqueça de criar um namespace para nossas aplicações com o comando `kubectl create namespace applications`. Em seguida, vamos criar um pod com dois containers, um chamado ubuntu-logger-one e outro chamado ubuntu-logger-two.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
  - name: ubuntu-logger-two
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
```

Podemos ver os logs de cada container com os comandos `kubectl logs ubuntu-dual-logging-pod` e `kubectl logs ubuntu-dual-logging-pod -c ubuntu-logger-two`, ou seja, não é possível ver ambos os logs ao mesmo tempo, a não ser que um novo terminal seja aberto.

![Visualizando logs com kubectl](images/logs-standard.png)

Com o Stern, podemos obter os logs de ambos os containers em simultâneo com o comando `stern ubuntu-dual-logging-pod`. Além disso, podemos filtrar os logs por container com o comando `stern ubuntu-dual-logging-pod --container ubuntu-logger-one` e `stern ubuntu-dual-logging-pod --container ubuntu-logger-two`, da mesma maneira que faríamos com o comando `kubectl logs ubuntu-dual-logging-pod -c ubuntu-logger-one` e `kubectl logs ubuntu-dual-logging-pod -c ubuntu-logger-two`.

![Visualizando logs com stern](images/stern.png)

## kube-score

Podemos perceber que a definição do pod que demos como exemplo acima não é a mais segura e não segue as melhores práticas. O kube-score é uma ferramenta que nos ajuda a avaliar as melhores práticas das definições de nossos recursos Kubernetes. Ele verifica se nossos recursos seguem as melhores práticas de segurança e resiliência e nos fornece sugestões de como podemos melhorar a segurança de nossos recursos.

Vamos verificar a definição do pod que criamos anteriormente com o kube-score. Primeiro, vamos salvar a definição do pod em um arquivo chamado _pod.yaml_ e em seguida executamos o comando `kube-score score pod.yaml`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
  - name: ubuntu-logger-two
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
```

Executamos o comando `kube-score score pod.yaml` e obtemos a seguinte saída:

![kube-score](images/kube-score.png)

O primeiro aviso que vemos é que o pod em questão não tem um Security Context Group ID definido. Vamos corriger isso adicionando um Security Context Group ID ao pod. A definição do pod ficará da seguinte maneira:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
  - name: ubuntu-logger-two
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
```

O segundo aviso se refere ao network policy, que não foi definido. Vamos corrigir isso adicionando um network policy para pod, mas para isso precisamos adicionar uma label ao pod para poder dar match com a network policy. Como nosso pod não precisa se comunicar com nenhum outro pod em nosso cluster, vamos bloquear tanto o trafego de entrada quanto o de saída. A definição do pod e da network policy ficará da seguinte maneira:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
  labels:
    app: ubuntu-logging-app
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
  - name: ubuntu-logger-two
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-all-traffic
  namespace: applications
spec:
  podSelector:
    matchLabels:
      app: ubuntu-logging-app
  policyTypes:
    - Ingress
    - Egress
```

Agora vamos ajustar o terceiro ponto que o kube-score nos alertou, que é o uso da tag latest, já que não definimos tag na imagem, o padrão é a latest. Vamos fixar a imagem do ubuntu para a versão 22.04. Portanto, agora teremos:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
  labels:
    app: ubuntu-logging-app
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu:22.04
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
  - name: ubuntu-logger-two
    image: ubuntu:22.04
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-all-traffic
  namespace: applications
spec:
  podSelector:
    matchLabels:
      app: ubuntu-logging-app
  policyTypes:
    - Ingress
    - Egress
```

No terceiro ponto precisamos definir apenas no SecurityContext o readOnlyRootFilesystem como true. O readOnlyRootFilesystem é uma medida de segurança que impede que um container modifique o sistema de arquivos raiz. A definição do pod ficará da seguinte maneira:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
  labels:
    app: ubuntu-logging-app
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu:22.04
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
      readOnlyRootFilesystem: true
  - name: ubuntu-logger-two
    image: ubuntu:22.04
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
      readOnlyRootFilesystem: true
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-all-traffic
  namespace: applications
spec:
  podSelector:
    matchLabels:
      app: ubuntu-logging-app
  policyTypes:
    - Ingress
    - Egress
```

Quase terminamos nossos ajustes, falta definir agora os recursos reservados para os containers. Os dois últimos alertas tratam sobre recursos, tanto memória e cpu quanto de ephemeral storage. Vamos definir que cada container terá 100m de CPU, 128Mi de memória e 50Mi de ephemeral storage como recursos reservados, 200m de CPU, 256Mi de memória e 100Mi de ephemeral storage como recursos limitados. Teremos então:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu-dual-logging-pod
  namespace: applications
  labels:
    app: ubuntu-logging-app
spec:
  containers:
  - name: ubuntu-logger-one
    image: ubuntu:22.04
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger One: Gerando logs para teste...\"; sleep 10; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
      readOnlyRootFilesystem: true
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
        ephemeral-storage: "50Mi"
      limits:
        memory: "256Mi"
        cpu: "200m"
        ephemeral-storage: "100Mi"
  - name: ubuntu-logger-two
    image: ubuntu:22.04
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo \"$(date) - Logger Two: Gerando logs para teste de outro contêiner...\"; sleep 15; done"]
    securityContext:
      runAsGroup: 10001
      runAsUser: 10001
      readOnlyRootFilesystem: true
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
        ephemeral-storage: "50Mi"
      limits:
        memory: "256Mi"
        cpu: "200m"
        ephemeral-storage: "100Mi"
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-all-traffic
  namespace: applications
spec:
  podSelector:
    matchLabels:
      app: ubuntu-logging-app
  policyTypes:
    - Ingress
    - Egress
```

## kube-capacity

## kubescape

## kubeshark

## Conclusão


