#!/bin/sh

curl -o CloudFormationResourceSpecification.json https://d3teyb21fexa9r.cloudfront.net/latest/CloudFormationResourceSpecification.json
python generate-snippets.py
rm -fr snippets/*
mv snippets.generated/* snippets
cp snippets.static/* snippets
rm -fr snippets.generated
