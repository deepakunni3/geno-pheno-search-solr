import sys, argparse, pysolr, pickle

parser = argparse.ArgumentParser(description="Accessory script to the Solr loader")
parser.add_argument('--solr_url', type=str, required=True)
parser.add_argument('--input', type=str, required=True)
args = parser.parse_args()

FH = open(args.input, "rb")
docs = pickle.load(FH)
solr = pysolr.Solr(url=args.solr_url)
solr.add(docs)
solr.optimize()
