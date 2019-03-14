import logging, argparse, json
from elasticsearch import Elasticsearch
from loader_utils import parse

parser = argparse.ArgumentParser(description="Parse and load a list of annotations into a configured ElasticSearch index")
parser.add_argument('--host', help='hostname',type=str, required=False)
parser.add_argument('--port', help='port',type=str, required=False)
parser.add_argument('--index', help='index name',type=str, required=False)
parser.add_argument('--input', help='Input TSV (Ex: topmed_curies.tsv)', type=str, required=True)
parser.add_argument('--output', help='Output JSON (Ex: documents.json)', type=str, required=True)
parser.add_argument('--use_existing', help='Use pre-built documents to load into ElasticSearch', action='store_true', required=False)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

DH = None
solr = None

if __name__ == "__main__":
    args = parser.parse_args()

    if args.use_existing:
        DH = open(args.output, 'r')
        documents = json.load(DH)
    else:
        # Parse input TSV and generate documents
        documents = parse(args.input)
        DH = open(args.output, 'w')
        DH.write(json.dumps(documents))
        DH.close()

    log.debug(documents)

    if args.host and args.port and args.index:
        es = Elasticsearch([{'host': args.host, 'port': args.port}])
        if es.ping():
            logging.info("Connection established to ElasticSearch on {}:{}".format(args.host, args.port))
        else:
            raise ConnectionError()

        log.info("Adding documents to ElasticSearch index: {}".format(args.index))

        for d in documents:
            try:
                response = es.index(index=args.index, doc_type="annotation", body=d)
            except Exception as ex:
                log.error('Error in indexing document')
                exit()

        log.info("Added {} documents".format(len(documents)))
