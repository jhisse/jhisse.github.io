---
title: Principais aprendizados utilizando o EKS
date: 2022-05-27
layout: post
---

Meu primeiro contato com o Kubernetes foi início de 2018, utilizamos a cloud do Google e seu serviço gerenciado do Kubernetes chamado Google Kubernetes Engine, GKE. Algum tempo depois, já em outra empresa, passamos a utilizar o Amazon Elastic Kubernetes Service, EKS, da AWS. Neste artigo irei focar no EKS, nas principais aplicações que julgo essenciais para gerenciar e manter em um cluster e nos principais acertos e erros cometidos nesse tempo.

## Provisionamento

Para instanciar o serviço do EKS temos muitas opções, podemos utilizar o console da AWS, o CLI [eksctl](https://eksctl.io), CloudFormation, [Terraform](https://www.terraform.io), entre outros. Como IaC neste caso, recomendo a utilização do Terraform, pois é uma aplicação amplamente utilizada pela comunidade, open-source, há muitas dúvidas e respostas no Stack Overflow, tem fácil curva de aprendizado, é multi cloud através dos inúmeros providers e, por fim, todos os recursos são definidos de forma declarativa.

Com o Terraform toda a infraestrutura necessária para o cluster pode ser automatizada e provisionada de forma que qualquer replicação do ambiente seja fácil. Isso traz muitas vantagens, como por exemplo, ter um ambiente de testes muito semelhante ao ambiente de produção. Ou em um cenário de disaster recovery o ambiente será provisionado de forma rápida e eficiente. Vou deixar fora deste artigo as diferentes maneiras de utilizar o Terraform para provisionar os recursos necessários, pois esse tema pode se estender o suficiente para justificar um novo artigo.

## IAM roles para service accounts

Talvez a primeira coisa que você deve se preocupar após provisionar seu cluster deve ser como seus pods poderão utilizar outros serviços da AWS. Por exemplo, se um pod precisar salvar um arquivo em um bucket no S3 ou escrever no DynamoDB, de alguma forma essas aplicações precisarão de uma permissão. De maneira a evitar utilizar credenciais da AWS, podemos associar uma role específica a um service account do Kubernetes e o pod utilizar essa service account. Isso permite um controle mais granular dos acessos que suas aplicações terão aos serviços da AWS, sem contar que evita o tráfego de credenciais de um lado para o outro. Podemos referenciar essa forma de associar uma IAM role a service account como IRSA.

Isso fará bastante sentido como iremos ver mais adiante. O controlador de volumes EBS precisará gerenciar os volumes EBS na AWS, ou seja, o controlador deve ter a permissão de criar, deletar ou anexar recursos de storage. O controlador dos load balancers precisará de acesso para criar, modificar e excluir load balancers gerenciados pela AWS. Em determinadas aplicações também precisaremos desse tipo de permissão. Um job Spark, por exemplo, precisará de permissão para ler e gravar dados em determinado bucket no S3. Uma aplicação backend poderá dar permissão para ler e gravar entradas no DynamoDB.

Não vou entrar em detalhes de como permitir que service accounts assumam roles da AWS, todos os por menores de como implementar essa feature pode ser encontrada na documentação [IAM roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html). Recomendo fortemente que o configure essa feature logo após o provisionamento do cluster para permitir que suas service accounts assumam roles das AWS.

## Aplicações

Vou falar um pouco das aplicações que julgo serem essenciais de serem instaladas em um cluster EKS. Algumas delas podem ser encontradas na [documentação oficial do EKS](https://docs.aws.amazon.com/eks/latest/userguide/index.html). Pode ser que alguma das citadas não faça sentido ao seu caso de uso. Muitas vezes o cluster após ser provisionado estará pronto para ser utilizado pela a maioria das aplicações. Cabe ao administrador do cluster utilizar seus próprios critérios para saber se precisa ou não das aplicações destacadas a seguir.

### Amazon EBS CSI driver

O EKS por padrão já disponibiliza um storage class para volumes persistentes. O tipo deste storage class padrão até a data de escrita deste artigo é o *gp2*. Para manipular novos tipos de EBS temos que instalar um driver CSI. Esta sigla quer dizer Container Storage Interface, é um padrão desenvolvido não só para o Kubernetes, mas para qualquer sistema de orquestração de containers. Ele dispõem de uma interface padrão que pode ser implementada por drivers para possibilitar que novos tipos de volumes, de diferentes fornecedores, possam ser utilizados no Kubernetes ou por qualquer outro serviço que utilize esta interface.

O *gp2* é um tipo de EBS disponibilizado pelo EKS que atende a maioria dos casos de uso, porém se quiser dar a possibilidade do desenvolvedor utilizar novas classes de armazenamento, então devemos instalar o [Amazon EBS CSI Driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver). Com ele, por exemplo, podemos provisionar o EBS do tipo *gp3* que oferece taxas de transferência melhores que o *gp2*, além de ser mais barato dependendo das configurações.

Como visto na seção de [IAM roles para service accounts](#iam-roles-for-service-accounts), o Amazon EBS CSI Driver precisa de permissão para provisionar volumes. Então a fim de evitar o uso de credenciais da AWS, podemos associar uma role específica a um service account do Kubernetes e o pod do driver utilizar essa service account.

### Amazon EFS CSI driver

Para o caso em que desejamos utilizar um volume cujo sistema de arquivos é do tipo *Amazon EFS*, é necessário instalar o [Amazon EFS CSI Driver](https://github.com/kubernetes-sigs/aws-efs-csi-driver). Com ele, podemos obter vantagens em relação ao EBS, como tamanho dinâmico de acordo com a demanda de recursos e a possibilidade de ser efetuado o mount em diferentes nós do EKS. Está última está relacionada aos modos de acesso ReadOnlyMany e ReadWriteMany do PersistentVolume.

### Calico

O [Calico](https://github.com/projectcalico/calico) é um network policy engine para o Kubernetes. Com ele é possível definir políticas para a rede do cluster, qual serviço pode se comunicar com outro, por exemplo. Outro tipo de caso de uso é o bloqueio de comunicação de serviços front-end com aplicações do *kube-system*, isso garantiria uma melhor segurança do cluster.

### AWS Load Balancer Controller

Para criar, gerenciar e deletar load balancers gerenciados pela AWS, precisamos deste controlador instalado ao cluster. O [AWS Load Balancer Controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller) irá permitir gerenciar Application Load Balancer para os recursos do tipo ingress e Network Load Balancer para os recursos do tipo service. 

Da mesma maneira que o Amazon EBS CSI Driver precisa de permissões especificas para gerenciar volumes, o AWS Load Balancer Controller também precisa de permissões para gerenciar recursos na AWs, justificando mais uma vez a configuração do IRSA no cluster.

Vamos a um exemplo.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  namespace: ns-1
  name: ingress-apps-1-2
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
        - path: /app1
          pathType: Prefix
          backend:
            service:
              name: service-app-1
              port:
                number: 80
        - path: /app2
          pathType: Prefix
          backend:
            service:
              name: service-app-2
              port:
                number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  namespace: ns-3
  name: ingress-app-3
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
        - path: /app3
          pathType: Prefix
          backend:
            service:
              name: service-app-3
              port:
                number: 80
```

O exemplo acima criará dois ALBs, o primeiro no namespace *ns-1* com duas regras e o segundo no namespace *ns-2* com uma regra. O primeiro ALB será utilizado para aplicação 1 e 2, enquanto o segundo será utilizado para aplicação 3. Lembrando que os serviços *services-app-1*, *service-app-2* e *service-app-3* devem ser do tipo NodePort.

![Ingress por namespace](/images/2022-05-27-principais-aprendizados-utilizando-o-eks/alb-separate.png)

O recurso do tipo *Ingress* da classe do ALB cria um novo load balancer de acordo com a quantidade de recursos ingress criados, como visto acima. Isso traz uma desvantagem, ter múltiplos ALBs pode tornar o custo alto. Para resolver este problema podemos utilizar uma [annotation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/ingress/annotations/#ingressgroup) que permite que o ALB seja reutilizado por vários namespaces, `alb.ingress.kubernetes.io/group.name`. Nosso exemplo ficaria assim:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  namespace: ns-1
  name: ingress-apps-1-2
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/group.name: group1
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
        - path: /app1
          pathType: Prefix
          backend:
            service:
              name: service-app-1
              port:
                number: 80
        - path: /app2
          pathType: Prefix
          backend:
            service:
              name: service-app-2
              port:
                number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  namespace: ns-3
  name: ingress-app-3
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/group.name: group1
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
        - path: /app3
          pathType: Prefix
          backend:
            service:
              name: service-app-3
              port:
                number: 80
```

![Compartilhando o mesmo ALB entre namespace](/images/2022-05-27-principais-aprendizados-utilizando-o-eks/alb-same-group.png)

### Nginx Ingress Controller

Caso você deseja utilizar o [Nginx](https://github.com/kubernetes/ingress-nginx) como um controlador do ingress, você ainda assim precisará do AWS Load Balancer Controller. Mais especificamente você utilizará o Network Load Balance e não o Application Load Balance. 

Aqui vale uma observação: não necessariamente você precisará utilizar o AWS Load Balancer Controller, pois por padrão o serviços do tipo load balancer são controlados pelo EKS, porém provisiona o Classic Load Balancer. A própria AWS recomenda que o [Network Load Balance seja utilizado em detrimento do Classic Load Balancer](https://docs.aws.amazon.com/eks/latest/userguide/network-load-balancing.html).

![Network Load Balancer com o Nginx Ingress Controller](/images/2022-05-27-principais-aprendizados-utilizando-o-eks/nlb-nginx.png)

Com o Nginx ingress basta que o serviço do nginx seja exposto como um serviço do tipo NodePort. No diagrama acima fica claro que somente o nginx tem interface com o load balancer, todos os demais serviços que tenham interface para fora do cluster podem ser do tipo ClusterIP, sendo o nginx a única porta de entrada para as aplicações.

### Cluster Autoscaler

Precisamos do [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler/cloudprovider/aws) para garantir a escalabilidade do cluster. Com ele podemos garantir que o número de nós irá aumentar ou diminuir de acordo com a demanda de recursos das aplicações.

Um dos principais erros cometidos quando usamos o autoscaler é em relação as zonas que os discos EBSs estão localizados quando usamos StatefulSets por exemplo. Os volumes EBSs provisionados estão localizados em determinadas zonas dentro de uma região. Se um nó não estiver localizado na mesma região que o volume EBS, o driver csi do EBS não conseguirá anexar o volume ao nó, já que eles estão em zonas diferentes. Para garantir que o nó sempre suba em uma região em específico, é necessário configurar o node group para escalar os nós somente em uma zona. Isso pode ser um problema se você estiver lidando com instâncias Spots, já que você acaba limitando o mercado de Spots quando utiliza somente uma zona. O Karpenter, a seguir, [resolve bem este problema](https://karpenter.sh/v0.10.1/tasks/scheduling/#persistent-volume-topology). Outra solução é utilizar classes de armazenamento que são replicadas em múltiplas zonas, como o [EFS](https://github.com/kubernetes-sigs/aws-efs-csi-driver), porém terá um custo maior devido as replicas em múltiplas regiões.

![EBS e EFS no EKS](/images/2022-05-27-principais-aprendizados-utilizando-o-eks/ebs-efs-eks.png)

### Karpenter

Essa aplicação é capaz de provisionar e gerenciar de maneira eficiente os workloads do seu cluster. De certa forma ele substitui o Cluster Autoscaler citado anteriormente, já que suas funções se sobrepõem. O [Karpenter](https://github.com/aws/karpenter) tem uma vantagem, ele provisiona máquinas de diferentes tamanhos de acordo com as requisições de recursos que foram solicitadas, ao contrário do Cluster Autoscaler que provisiona máquinas sempre do mesmo tamanho de acordo com os nodes groups. Dessa forma o Karpenter otimiza as solicitações de instâncias EC2 de acordo com a necessidade, aumentando assim a economia.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 10
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128M"
            cpu: "250m"
          limits:
            memory: "256M"
            cpu: "500m"
```

No exemplo acima, o deployment está instanciando 10 replicas, ou melhor, 10 pods com o container do nginx. Cada container está requisitando 128 megabytes de memória ram e 250 milicores de CPU, como temos 10 replicas, estamos solicitando um total de 1280 megabytes de memória e 2500 milicores de CPU. Se esse for o único workload do seu cluster, o Karpenter vai provisionar uma instância com valores de memória e CPU que mais se aproximará para igual ou superior ao que foi requisitado. Provável que seja uma instância com 4 cpu e 16Gb de ram, uma *m5.xlarge*, por exemplo.

![Representação da utilização de recursos](/images/2022-05-27-principais-aprendizados-utilizando-o-eks/requests.png)

Claro que o exemplo acima depende das configurações do Karpenter, porém acredito que as vantagens de usá-lo ficaram mais claras.

### External Secrets

Dificilmente você irá querer armazenar seus segredos no git, a não ser que você armazene de forma criptografada, por exemplo, utilizando o [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) ou o [SOPS](https://github.com/mozilla/sops). Outra forma de gerenciar os segredos é utilizando o [External Secrets](https://github.com/external-secrets/external-secrets).

Com o External Secrets podemos armazenar os segredos em um sistema externo ao Kubernetes e sincronizar de tempos em tempos, transformando-os em secrets do Kubernetes. Por exemplo, podemos armazenar os segredos no AWS Secrets Manager e criar um recurso no Kubernetes indicando que os segredos devem ser sincronizados a partir deste repositório.

### Prometheus

Para armazenar métricas do seu cluster, podemos utilizar o [Prometheus](https://prometheus.io/). O Prometheus irá armazenar essas métricas de memória, cpu e etc, para que possamos monitorar em tempo real ou para analises futuras o comportamento de nossos workloads.

### Prometheus Adapter



### Grafana Loki

Além das métricas do Prometheus, precisamos nos preocupar com os logs das aplicações também. Lembrando da natureza efêmera dos containers, precisamos capturar e armazenar os logs de forma eficiente. Para isso, utilizamos o [Loki](

### Grafana

Para visualizar as métricas do Prometheus e os logs do Loki, precisamos de uma aplicação que nos permita visualizar esses dados armazenados. Para isso, utilizamos o [Grafana](https://grafana.com/).

## Conclusão

