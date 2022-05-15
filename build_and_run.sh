#!/usr/bin/env sh

docker build . -t kkchau/trulia_to_notion:latest && docker run --rm -e NOTION_API_TOKEN=$NOTION_API_TOKEN kkchau/trulia_to_notion:latest
