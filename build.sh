#!/bin/sh

python generate-snippets.py
rm -fr snippets/*
mv snippets.generated/* snippets
cp snippets.static/* snippets
rm -fr snippets.generated
