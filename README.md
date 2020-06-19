# Twint

Tooling for working with Twitter & graphs

## Quickstart

```
pipenv install 
pipenv run twint -u username -o username.json --json

export NEO4J_URI=neo4j://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=admin

pipenv run python3 import-tweets username.json
```

## Docker

```
docker build . -t twint:latest

export CONFIG='{"Username":"realDonaldTrump","Limit":10,"Bucket":"meetup-data"}'

export KEY=`cat /path/to/service-key.json`

docker run -e KEY -e CONFIG twint:latest 
```

Optional CONFIG keys:
* BaseDirectory - the directory in the bucket to use for storage (default=twint)
* DataSet - directory for the named dataset this
fetch belongs to, so you can group related scrapes.  (default='default')

## Run as a GCP instance, one-shot

(Not working well for a variety of reasons, explore alternatives)

export REGISTRY=gcr.io/testbed-187316
export IMAGE=twint
export TAG=latest

gcloud compute instances create-with-container \
    twint-$(head -c 256 /dev/urandom | md5sum | head -c 8) \
     --container-image $REGISTRY/$IMAGE:$TAG

## Twint Documentation

See [twint usage examples](https://github.com/twintproject/twint#cli-basic-examples-and-combos)