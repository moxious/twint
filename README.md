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

## Twint Documentation

See [twint usage examples](https://github.com/twintproject/twint#cli-basic-examples-and-combos)