---
title: Um ou múltiplos arquivos yaml no Kubernetes
date: 2021-06-20
layout: post
---

Neste artigo vamos explorar diferentes formas de organizar seus arquivos yaml. Os arquivos yaml para o kubernetes contem as definições de services, deployments, pods, namespaces, configmaps, secrets e outros objetos. Vamos perceber que determinadas formas de organização podem trazer vantagens e desvantagens. Ao final iremos utilizar o *Kustomize*, já presente no *kubectl*.

## Ambiente de testes

Para que você possa ter um entendimento maior deste artigo, recomendo configurar em sua máquina um ambiente de testes. Assim você poderá reproduzir todos os passos que virão a seguir.

Para seu ambiente local vamos utilizar o [Kind](https://kind.sigs.k8s.io/), já citado no artigo em que falamos sobre [pods anti affinity]({{< ref aumentando-disponibilidade-com-inter-pod-anti-affinity >}}). Iremos precisar também do [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) para gerenciar nosso cluster.

Então, vamos criar nosso cluster local, para isso vamos ao terminal:

```console
$ kind create cluster --name yamls-test
Creating cluster "yamls-test" ...
 ✓ Ensuring node image (kindest/node:v1.20.2) 🖼 
 ✓ Preparing nodes 📦  
 ✓ Writing configuration 📜 
 ✓ Starting control-plane 🕹️ 
 ✓ Installing CNI 🔌 
 ✓ Installing StorageClass 💾 
Set kubectl context to "kind-yamls-test"
You can now use your cluster with:

kubectl cluster-info --context kind-yamls-test

Not sure what to do next? 😅  Check out https://kind.sigs.k8s.io/docs/user/quick-start/

$ kubectl get nodes
NAME                       STATUS   ROLES                  AGE     VERSION
yamls-test-control-plane   Ready    control-plane,master   9m43s   v1.20.2
```

## Único arquivo yaml

Ao longo deste artigo iremos usar como exemplo somente duas definições de objetos do kubernetes. Uma definição de namespace e outra de pod. Essas definições podem coexistir em um único arquivo como podemos ver a seguir.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
---
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
  labels:
    app: my-app
spec:
  containers:
    - name: my-app
      image: k8s.gcr.io/pause:3.2
```

As definições devem ser separadas por ```---```. No primeiro bloco temos a definição de namespace e no segundo bloco temos a do pod. Vamos observar que a do pod tem uma dependência com a do namespace.

```yaml
...
metadata:
  name: my-pod
  namespace: my-namespace
...
```

Vamos salvar essas definições em um arquivo yaml.

```console
$ cat << EOF > all-objects.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
---
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
  labels:
    app: my-app
spec:
  containers:
    - name: my-app
      image: k8s.gcr.io/pause:3.2
EOF

$ ls
all-objects.yaml
```

Vemos que nosso arquivo com todas as definições foi criado e agora vamos aplicá-lo em nosso cluster com o kubectl.

```console
$ kubectl apply -f ./
namespace/my-namespace created
pod/my-pod created

$ kubectl get namespaces
kubectl get namespaces
NAME                 STATUS   AGE
default              Active   77m
kube-node-lease      Active   77m
kube-public          Active   77m
kube-system          Active   77m
local-path-storage   Active   77m
my-namespace         Active   16s

$ kubectl get pods -n my-namespace
NAME     READY   STATUS    RESTARTS   AGE
my-pod   1/1     Running   0          45s
```

Podemos observar que tudo funcionou como esperado. O namespace foi criado antes do pod, conforme a ordem definida no arquivo.

Vamos realizar um experimento agora. Primeiro vamos deletar os objetos que criamos.

```console
$ kubectl delete -f ./
namespace "my-namespace" deleted
pod "my-pod" deleted
```

Agora invertemos a ordem dos objetos em nosso yaml e tentaremos aplicar as mudanças.

```console
$ cat << EOF > all-objects.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
  labels:
    app: my-app
spec:
  containers:
    - name: my-app
      image: k8s.gcr.io/pause:3.2
---
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
EOF

$ kubectl apply -f ./
namespace/my-namespace created
Error from server (NotFound): error when creating "all-objects.yaml": namespaces "my-namespace" not found
```

Nosso pod tinha uma dependência com o namespace. Como o namespace não existia no momento de criação do pod, obtivemos o erro descrito acima.

Esse modo de um único arquivo evita esse tipo de problema, porém em definições numerosas e complexas pode ficar difícil de gerenciar e prejudicar o entendimento de seu projeto.

Para finalizar essa parte devemos excluir os recursos criados e o arquivo.

```console
$ kubectl delete --ignore-not-found=true -f ./
namespace "my-namespace" deleted

$ rm -v all-objects.yaml
removido 'all-objects.yaml'
```

## Múltiplos arquivos yaml

Nesta seção vamos organizar os recursos em múltiplos arquivos. Iremos perceber que esta forma torna nossas definições mais simples de entender e mais organizada, porém também pode gerar alguns problemas, como veremos a seguir.

Criaremos agora dois arquivos separados contendo nossas definições de namespace e pod.

```console
$ cat << EOF > my-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
  labels:
    app: my-app
spec:
  containers:
    - name: my-app
      image: k8s.gcr.io/pause:3.2
EOF

$ cat << EOF > namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
EOF

$ ls
my-pod.yaml  namespace.yaml
```

Se tentarmos aplicar nossas definições no cluster receberemos um erro. Isso porque ele tentou aplicar a definição do pod, *my-pod.yaml*, antes da definição do namespace, *namespace.yaml*.

```console
$ kubectl apply -f ./
namespace/my-namespace created
Error from server (NotFound): error when creating "my-pod.yaml": namespaces "my-namespace" not found

$ kubectl delete --ignore-not-found=true -f ./
namespace "my-namespace" deleted
```

E se nós atribuirmos novos nomes aos arquivos para manter a ordem correta? Iremos renomear o *namespace.yaml* para *00-namespace.yaml* e o *my-pod.yaml* para *01-my-pod.yaml*, depois tentaremos aplicar novamente nossas definições.

```console
$ mv -v namespace.yaml 00-namespace.yaml
renomeado 'namespace.yaml' -> '00-namespace.yaml'

$ mv -v my-pod.yaml 01-my-pod.yaml
renomeado 'my-pod.yaml' -> '01-my-pod.yaml'

$ ls
00-namespace.yaml  01-my-pod.yaml

$ kubectl apply -f ./
namespace/my-namespace created
pod/my-pod created
```

Resolvemos nosso problema, porém não é uma solução muito elegante. Em projetos grandes e em desenvolvimento, pode resultar na necessidade de renomear constantemente nossas definições. Por exemplo, quando uma nova definição for dependência, como um ConfigMap por exemplo. Se ele fosse dependência do pod, teríamos que renomear o *01-my-pod.yaml* para *02-my-pod.yaml* e o ConfigMap seria algo como *01-my-configmap.yaml*.

Vamos remover os recursos criados para avançarmos para a próxima seção.

```console
$ kubectl delete -f ./
pod "my-pod" deleted
namespace "my-namespace" deleted
```

## Múltiplos arquivos yaml com Kustomize

O [Kustomize](https://kustomize.io/) permite a listagem de todos os arquivos yaml que farão parte de nosso projeto em um arquivo yaml.

Primeiro vamos renomear nossos arquivos para o nome anterior.

```console
$ mv -v 00-namespace.yaml namespace.yaml
renomeado '00-namespace.yaml' -> 'namespace.yaml'

$ mv -v 01-my-pod.yaml my-pod.yaml
renomeado '01-my-pod.yaml' -> 'my-pod.yaml'

$ ls
my-pod.yaml  namespace.yaml
```

O template que iremos usar segue o padrão definido abaixo.

```console
$ cat << EOF > kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - my-pod.yaml
  - namespace.yaml
EOF

$ ls
kustomization.yaml  my-pod.yaml  namespace.yaml
```

Felizmente o *kubectl* já vem com [suporte ao *kustomize*](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/). Basta utilizarmos a flag **-k** no lugar da **-f**, ```kubectl apply -k ./```.

```console
$ kubectl apply -k ./
namespace/my-namespace created
pod/my-pod created
```

Vimos que utilizando o *Kustomize* resolvemos nosso problema. Os objetos são ordenados de acordo com uma [hierarquia já definida no código fonte](https://github.com/kubernetes-sigs/kustomize/blob/cb4f5c39837e50a02e063e48941ed515da28356f/kyaml/resid/gvk.go#L132-L159). Isso minimiza quaisquer problemas relacionados a yaml que dependem de outro recurso, como o caso visto neste artigo.

É importante ressaltar que o *Kustomize* não se limita a esse uso. Ele possui recursos que trazem muitas vantagens para seus templates yaml. Você pode checar as [principais features no site oficial](https://kubectl.docs.kubernetes.io/guides/introduction/kustomize/).

```console
$ kubectl delete -k ./
pod "my-pod" deleted
namespace "my-namespace" deleted
```

## Conclusão

Vimos 3 maneiras diferentes de organizar um pequeno conjunto de definições do kubernetes. Em cada uma delas existem vantagens e desvantagens, cabendo ao desenvolvedor a escolha da mais adequada ao seu projeto.

O uso do Kustomize pode aparentar trazer ao projeto uma pequena complexidade a mais, porém suas vantagens não se limitam às apresentadas aqui. Em projetos onde você precisa fazer pequenas alterações em seu yaml, como aumentar o número de réplicas por ambiente ou ter labels diferentes em produção e desenvolvimento, ele será um facilitador.

## Extra

Podemos usar o *Kustomize* para gerar um único yaml. Tendo nossos 3 arquivos de exemplo no diretório, o kustomization, o do namespace e o do pod, basta executar o comando ```kubectl kustomize ./```

```console
$ ls
kustomization.yaml  my-pod.yaml  namespace.yaml

$ kubectl kustomize ./
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: my-app
  name: my-pod
  namespace: my-namespace
spec:
  containers:
  - image: k8s.gcr.io/pause:3.2
    name: my-app
```
