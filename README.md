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

## Twint Documentation

See [twint usage examples](https://github.com/twintproject/twint#cli-basic-examples-and-combos)