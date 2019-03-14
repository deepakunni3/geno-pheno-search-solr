#!/bin/sh

## ENTRYPOINT script

service nginx start
su solr -c '/opt/solr/solr-6.6.5/bin/solr start'
cd /opt/solr/geno-pheno-search-solr
su solr -c 'python3 index-loader/solr_loader.py --use_existing --url http://localhost:8983/solr/genophenosearch-core --input topmed_curies_denormalized.tsv --output documents.json'

# This will exec the CMD from your Dockerfile
exec "$@"