#!/bin/sh

## ENTRYPOINT script

service nginx start
su solr -c '/opt/solr/solr-6.6.5/bin/solr start'
cd /opt/solr/geno-pheno-search-solr
su solr -c 'python3 solr-loader/load_documents.py --solr_url http://localhost:8983/solr/genophenosearch-core --input /tmp/documents.pkl'

# This will exec the CMD from your Dockerfile
exec "$@"