#REQUIEREMENTS : Installation

#kind : https://kind.sigs.k8s.io/docs/user/quick-start/
#Kubectl : https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
#https://helm.sh/docs/intro/install/

#RESSOURCES

#Ressource video : https://www.youtube.com/watch?v=AjBADrVQJv0
#Ressource apache cluster Quick start with Kind : https://airflow.apache.org/docs/helm-chart/stable/quick-start.html#install-kind-and-create-a-cluster
#Ressource apache cluster Helm https://airflow.apache.org/docs/helm-chart/stable/index.html
#Ressource tutorials : https://www.clearpeaks.com/kubernetes-for-managing-microservices/?utm_source=website&utm_medium=blog-post&utm_campaign=airflow-kubernetes
#Ressource tutorials : https://www.clearpeaks.com/deploying-apache-airflow-on-a-kubernetes-cluster/


#Diasgnostics
kubectl get secret airflow-airflow-metadata --namespace <namespace>
kubectl get events
kubectl get pods --namespace jle-airflow
helm list
helm uninstall airflow --namespace airflow
helm delete airflow --namespace airflow

#Add K8 entities
kubectl apply -f metadata-secret.yaml
kubectl apply -f airflow-configmap.yaml

