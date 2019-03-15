import pysolr, logging, argparse, json
from loader_utils import parse

parser = argparse.ArgumentParser(description="Parse and load a list of annotations into a configured Solr core")
parser.add_argument('--url', help='Solr URL (Ex: http://localhost:8983/solr/core1)',type=str, required=False)
parser.add_argument('--input', help='Input TSV (Ex: topmed_curies.tsv)', type=str, required=True)
parser.add_argument('--output', help='Output JSON (Ex: documents.json)', type=str, required=True)
parser.add_argument('--use_existing', help='Use pre-built documents to load into Solr', action='store_true', required=False)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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

    logging.debug(documents)

    if args.url:
        solr = pysolr.Solr(url = args.url)
        logging.info("Adding documents to Solr: {}".format(args.url))
        solr.add(documents)
        logging.info("Optimizing Solr core")
        solr.optimize()
