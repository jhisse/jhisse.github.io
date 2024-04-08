---
title: Aplicações fundamentais para o Amazon EKS
date: 2024-04-07
layout: post
---

Meu primeiro contato com o Kubernetes ocorreu no início de 2018, quando utilizamos a cloud do Google e seu serviço gerenciado do Kubernetes, chamado Google Kubernetes Engine (GKE). Algum tempo depois, já em outra empresa, passamos a utilizar o Amazon Elastic Kubernetes Service (EKS) da AWS. Este artigo se concentrará no EKS, destacando as principais ferramentas e práticas que considero fundamentais para gerenciar e manter um cluster de forma eficaz, baseando-se nos acertos e desafios enfrentados durante minha experiência.

## Provisionamento

Para instanciar o serviço do EKS, temos diversas opções: podemos utilizar o console da AWS, o CLI [eksctl](https://eksctl.io), CloudFormation, [Terraform](https://www.terraform.io), entre outros. Recomendo o uso do Terraform por ser uma ferramenta open-source amplamente adotada pela comunidade, com uma vasta quantidade de documentação e discussões disponíveis no Stack Overflow. Além disso, o Terraform permite definir a infraestrutura de maneira declarativa e é compatível com múltiplas clouds por meio de providers. Essas características facilitam a replicação de ambientes e agilizam o provisionamento em cenários de disaster recovery.

Até o momento deste artigo, o [módulo do Terraform para provisionar o EKS](https://github.com/terraform-aws-modules/terraform-aws-eks) é amplamente utilizado e bem mantido pela comunidade, sendo uma excelente escolha para essa finalidade.

## IAM roles para service accounts

Após provisionar seu cluster, é crucial configurar como seus pods irão interagir com outros serviços da AWS. Evitando o uso de credenciais AWS explícitas, podemos associar IAM roles a service accounts do Kubernetes, permitindo um controle mais granular dos acessos. Este método é conhecido como IRSA ("IAM roles for service accounts").

Configurar o IRSA é fundamental para diversas operações, como permitir que um job do Spark acesse um bucket no S3, que um controlador do EBS possa provisionar volumes, que um job Flink possa salvar checkpoints no S3 ou que o controlador dos load balancers da AWS gerencie esses recursos. A documentação oficial [IAM roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html) oferece um guia detalhado para implementação.

Recomendo que esta configuração seja feita logo após a criação do cluster, pois ela é essencial para o funcionamento de diversas aplicações e serviços. Além disso, o IRSA é uma prática recomendada de segurança, pelos diversos benefícios que oferece.

## Aplicações

Segue uma lista de aplicações que considero essenciais em um cluster EKS. Essas escolhas podem variar conforme as necessidades específicas de cada caso de uso. Muitas vezes o cluster, após ser provisionado, estará pronto para ser utilizado pela maioria das aplicações. Cabe ao administrador do cluster utilizar seus próprios critérios para saber se precisa ou não das aplicações destacadas a seguir.

### Amazon EBS CSI driver

Por padrão, o EKS disponibiliza uma classe de armazenamento, chamada *gp2*, para volumes persistentes. Essa classe atende à maioria dos casos de uso, porém, para explorar novas classes de armazenamento EBS, é necessário instalar o Amazon EBS CSI Driver. O CSI, ou Container Storage Interface, é um padrão crucial não apenas para o Kubernetes mas também para qualquer sistema de orquestração de contêineres. Ele oferece uma interface unificada que permite a implementação de drivers específicos, habilitando o uso de diferentes tipos de volumes para diversos providers.

O *gp2* é uma solução de armazenamento versátil oferecida pelo EKS, mas ao instalar o [Amazon EBS CSI Driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver), abrem-se novas possibilidades. Com ele, é viável provisionar volumes *gp3*, que, dependendo da configuração, podem ser mais econômicos e oferecer taxas de transferência superiores, ou *io1*, destinados a cargas de trabalho com intensa leitura e escrita.

Conforme discutido na seção [IAM roles para service accounts](#iam-roles-for-service-accounts), o Amazon EBS CSI Driver necessita de permissões específicas para gerir volumes. Portanto, ao invés de recorrer ao uso de credenciais AWS, o recomendado é vincular uma role IAM específica a um service account do Kubernetes, possibilitando que o pod do driver opere com essa configuração. Isso enfatiza a importância de adotar práticas seguras, minimizando o risco associado ao gerenciamento de credenciais.

### Amazon EFS CSI Driver

Para situações em que se faz necessário o uso de volumes com sistema de arquivos *Amazon EFS*, a instalação do [Amazon EFS CSI Driver](https://github.com/kubernetes-sigs/aws-efs-csi-driver) se torna indispensável. Este driver traz consigo benefícios significativos quando comparado ao uso tradicional de EBS, destacando-se principalmente pelo seu tamanho adaptável que escala conforme a demanda de recursos e pela capacidade de montagem em múltiplos nós dentro do cluster EKS. Essas características são particularmente úteis em cenários que demandam modos de acesso como ReadOnlyMany e ReadWriteMany para o PersistentVolume, permitindo uma flexibilidade e escalabilidade maior na gestão de volumes e no acesso a dados por múltiplas instâncias e aplicações.

### AWS Load Balancer Controller

A criação, gestão e remoção de load balancers gerenciados pela AWS dentro de um cluster EKS requer a instalação do [AWS Load Balancer Controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller). Este controlador é fundamental para o gerenciamento eficiente de Application Load Balancers associados a recursos do tipo ingress, bem como de Network Load Balancers vinculados a recursos do tipo service.

Assim como o Amazon EBS CSI Driver necessita de permissões específicas para operar com volumes, o AWS Load Balancer Controller demanda permissões adequadas para gerenciar recursos necessários na AWS.

### Cluster Autoscaler

A escalabilidade do cluster é fundamental para ajustar dinamicamente o número de nós de acordo com a demanda de recursos das aplicações, o que é alcançado através do [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler/cloudprovider/aws). Este componente ajusta automaticamente o tamanho do cluster, adicionando ou removendo nós para garantir que as aplicações tenham os recursos necessários disponíveis e para minimizar custos com recursos subutilizados.

Um desafio comum ao usar o Cluster Autoscaler envolve a localização dos discos EBS quando utilizamos StatefulSets. Os volumes EBS são provisionados em zonas específicas dentro de uma região da AWS. Caso um nó esteja em uma zona diferente do volume EBS, o driver CSI não conseguirá anexar o volume ao nó devido a essa discrepância de zonas. Para contornar essa questão, é essencial configurar os grupos de nós para escalarem dentro de uma zona específica, garantindo a mesma zona entre nós e volumes. No entanto, isso pode representar um desafio ao usar instâncias Spot, pois a limitação de zonas restringe o mercado de Spot disponíveis. Uma alternativa é o uso do [Karpenter](https://karpenter.sh/v0.35/concepts/scheduling/#persistent-volume-topology), que gerencia essa questão de forma mais eficiente, ou adotar soluções de armazenamento como o [EFS](https://github.com/kubernetes-sigs/aws-efs-csi-driver), que suportam replicação em múltiplas zonas, embora isso possa acarretar custos adicionais por conta das réplicas.

### Karpenter

O [Karpenter](https://github.com/aws/karpenter) surge como uma solução inovadora para o provisionamento e gerenciamento eficiente dos nós em um cluster. Em certo sentido, ele atua como um substituto para o Cluster Autoscaler, com o qual compartilha algumas funções. No entanto, o Karpenter leva a vantagem de poder provisionar máquinas de diferentes tamanhos, adequando-se às solicitações específicas de recursos das aplicações, diferentemente do Cluster Autoscaler que se limita a provisionar máquinas de tamanhos fixos, baseando-se nos grupos de nodes previamente definidos. Graças a essa capacidade de ajuste fino, o Karpenter otimiza o uso das instâncias EC2 de acordo com as necessidades reais, promovendo uma maior economia nos custos operacionais do cluster.

### External Secrets

A gestão de segredos no desenvolvimento e operação de aplicações é uma preocupação fundamental, sobretudo porque a prática de armazenar segredos diretamente no git — salvo quando criptografados usando ferramentas como [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) ou [SOPS](https://github.com/mozilla/sops) — é amplamente desaconselhada. Uma alternativa eficaz para esse gerenciamento é o uso do [External Secrets](https://github.com/external-secrets/external-secrets).

O External Secrets habilita o armazenamento de informações sensíveis fora do cluster, em sistemas dedicados como o AWS Secrets Manager, e a sincronização desses segredos para dentro do cluster conforme necessário. Isso é feito através da criação de um recurso no Kubernetes que especifica quais segredos devem ser sincronizados do sistema externo, garantindo que as aplicações tenham acesso aos segredos atualizados sem a necessidade de armazená-los em locais potencialmente inseguros ou menos controlados.

### Ferramentas de observabilidade

As ferramentas de observabilidade são de fundamental importância para monitorar o estado do cluster e das aplicações. Como acredito que elas merecem um artigo à parte, deixarei apenas os links das mesmas a seguir:

- [Prometheus](https://prometheus.io)
- [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [Grafana](https://grafana.com/grafana/)

## Conclusão

Gerenciar um cluster EKS pode ser uma tarefa complexa em um primeiro momento, porém ao longo do tempo você perceberá o que fará mais sentido para seu cenário e quais aplicações são essenciais para manter o cluster rodando de forma eficiente.

Não se prenda apenas às aplicações citadas neste artigo, existem muitas outras que podem ser úteis para você e sua empresa. O importante é manter o cluster seguro, escalável e eficiente. A documentação oficial do EKS é um bom ponto de partida para entender as funcionalidades do serviço e como utilizá-las.
