#!/bin/sh

helm repo add elastic https://helm.elastic.co
helm repo update

helm upgrade --install elasticsearch elastic/elasticsearch -f ./deploy/elasticsearch/values-override.yml --namespace logging --create-namespace
helm upgrade --install kibana elastic/kibana -f ./deploy/kibana/values-override.yml --namespace logging --create-namespace
helm upgrade --install filebeat elastic/filebeat -f ./deploy/filebeat/values-override.yml --namespace logging --create-namespace
helm upgrade --install logstash elastic/logstash -f ./deploy/logstash/values-override.yml --namespace logging --create-namespace