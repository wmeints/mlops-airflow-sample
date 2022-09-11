#!/bin/sh

##
## Install KNative for serverless hosting
##
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.7.1/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.7.1/serving-core.yaml

kubectl apply -l knative.dev/crd-install=true -f https://github.com/knative/net-istio/releases/download/knative-v1.7.0/istio.yaml
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.7.0/istio.yaml

kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.7.0/net-istio.yaml

kubectl patch configmap/config-domain \
    --namespace knative-serving \
    --type merge \
    --patch '{"data":{"knative.mlopsdemo.local":""}}'

kubectl apply -f ./deploy/kserve/

##
## Install Certmanager
##
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.9.1/cert-manager.yaml

##
## Install KServe
##
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.9.0/kserve.yaml
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.9.0/kserve-runtimes.yaml
