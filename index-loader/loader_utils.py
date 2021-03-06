from ontobio.ontol_factory import OntologyFactory
import networkx as nx
import logging, hashlib

DOCUMENT_CATEGORY = "annotation"
SUBCLASS_OF = 'subClassOf'

prefix_to_file_map = {
    'OBA': 'oba.obo',
    'NCIT': 'ncit.obo',
    'HP': 'hp.obo',
    'MONDO': 'mondo.obo',
    'EFO': 'efo'
}

cache = {}
log = logging.getLogger()
def ancestors(ont, term, relations, reflexive=False):
    """
    Get all ancestors for a given term
    """
    global cache
    if reflexive:
        ancs = ancestors(ont, term, relations, reflexive=False)
        ancs.append(term)
        return ancs

    g = None
    if relations is None:
        g = ont.get_graph()
    else:
        key = ont.handle + '-'.join(relations)
        if key in cache:
            g = cache[key]
        else:
            g = ont.get_filtered_graph(relations)
            cache[key] = g

    if term in g:
        return list(nx.ancestors(g, term))
    else:
        return []

def get_closure(ont, term, relations, reflexive=False):
    """
    Get a closure for a given term
    """
    closure = ancestors(ont, term, relations=relations, reflexive=reflexive)
    return closure

def load(docs):
    """
    Load docs into Solr
    """
    global solr
    solr.add(docs)

def verify_curie(curie):
    """
    Verify a given CURIE
    """
    curie_list = curie.split(':')
    if len(curie_list) != 2:
        if "_" in curie:
            log.warning("{} should actually be {}".format(curie,curie.replace('_', ':')))
            curie_list = curie.split('_')
        else:
            log.error("{} is not a proper CURIE".format(curie))
    return ':'.join(curie_list)

def get_prefix(curie):
    """
    Extract prefix from a given CURIE
    """
    return curie.split(':')[0]

def parse(input_file):
    """
    Parse an input TSV into JSON documents
    """
    ontologies = {}
    term_cache = {}
    documents = []

    with open(input_file, 'r') as FH:
        for line in FH:
            element = line.split('\t')
            if len(element) != 8:
                log.error("Improperly formatted line: {}".format(line))
                exit()
            ontology_id = element[-2]
            ontology_id = verify_curie(ontology_id)

            other_annotations = element[-1].rstrip().split(',')
            if len(other_annotations) > 0:
                other_annotations = [verify_curie(x) for x in other_annotations]

            isa_closure = None
            isa_closure_label = None
            if ontology_id not in term_cache:
                prefix = get_prefix(ontology_id)
                ontology = None
                if prefix in ontologies:
                    ontology = ontologies[prefix]
                else:
                    ontology_factory = OntologyFactory()
                    log.info("loading ontology: {}".format(prefix))
                    ontology = ontology_factory.create(prefix_to_file_map[prefix])
                    ontologies[prefix] = ontology

                isa_closure = get_closure(ontology, ontology_id, [SUBCLASS_OF], True)
                isa_closure_label = [ontology.label(x) for x in isa_closure]
                term_cache[ontology_id] = {}
                term_cache[ontology_id]['isa_closure'] = isa_closure
                term_cache[ontology_id]['isa_closure_label'] = isa_closure_label
            else:
                isa_closure = term_cache[ontology_id]['isa_closure']
                isa_closure_label = term_cache[ontology_id]['isa_closure_label']

            document = {
                'id': hashlib.sha256(line.encode()).hexdigest(),
                'document_category': DOCUMENT_CATEGORY,
                'study_accession': element[2],
                'study_dataset_accession': element[4],
                'variable_phv': element[0],
                'tag_id': element[1],
                'study_url': element[3],
                'study_dataset_url': element[5],
                'ontology_class': ontology_id,
                'ontology_class_label': ontology.label(ontology_id),
                'isa_closure': isa_closure,
                'isa_closure_label': isa_closure_label,
                'other_annotations': other_annotations
            }
            documents.append(document)

    return documents
