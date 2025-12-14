#!/bin/bash

# Wait for Elasticsearch to start up
until curl -s http://localhost:9200 > /dev/null; do
    echo 'Waiting for Elasticsearch...'
    sleep 3
done

# Create index with mappings
curl -X PUT "localhost:9200/news" -H "Content-Type: application/json" -d @/usr/share/elasticsearch/mappings/news.json 