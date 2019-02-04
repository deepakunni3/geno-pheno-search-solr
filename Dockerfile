FROM openjdk:8-jre
MAINTAINER  Deepak Unni "deepak.unni3@gmail.com"

# Install pre-requisites
RUN apt-get update && \
  apt-get -y install vim lsof htop wget python3 python3-pip git-core procps nginx

# Set environment variables
ENV SOLR_USER="solr" \
    SOLR_UID="89830" \
    SOLR_GROUP="solr" \
    SOLR_GID="89830" \
    SOLR_VERSION="6.6.5"

ENV SOLR_DISTRIBUTION="solr-${SOLR_VERSION}"
ENV SOLR_DOWNLOAD_URL=https://archive.apache.org/dist/lucene/solr/${SOLR_VERSION}/${SOLR_DISTRIBUTION}.tgz

# Set user and group
RUN groupadd -r --gid $SOLR_GID $SOLR_GROUP && \
  useradd -r --uid $SOLR_UID --gid $SOLR_GID $SOLR_USER

# 
RUN mkdir /home/solr && \
chown -R solr:solr /home/solr

RUN echo "${SOLR_VERSION} ${SOLR_DISTRIBUTION} ${SOLR_DOWNLOAD_URL}"

# Download Solr
RUN mkdir /opt/solr && \
  cd /opt/solr && \
  wget ${SOLR_DOWNLOAD_URL} && \
  tar -xvzf ${SOLR_DISTRIBUTION}.tgz

RUN chown -R $SOLR_USER:$SOLR_GROUP /opt/solr

# Download owltools
RUN wget http://build.berkeleybop.org/userContent/owltools/owltools -O /usr/bin/owltools && \
  chmod 777 /usr/bin/owltools

# Clone geno-pheno-search-solr
RUN git clone https://github.com/deepakunni3/geno-pheno-search-solr.git /opt/solr/geno-pheno-search-solr

RUN pip3 install ontobio==1.6.3

# Download necessary ontologies
RUN wget http://purl.obolibrary.org/obo/hp.obo -O /opt/solr/geno-pheno-search-solr/hp.obo
RUN wget http://purl.obolibrary.org/obo/mondo.obo -O /opt/solr/geno-pheno-search-solr/mondo.obo
RUN wget http://purl.obolibrary.org/obo/ncit.obo -O /opt/solr/geno-pheno-search-solr/ncit.obo
RUN wget http://purl.obolibrary.org/obo/oba.obo -O /opt/solr/geno-pheno-search-solr/oba.obo
RUN wget https://www.ebi.ac.uk/efo/efo.obo -O /opt/solr/geno-pheno-search-solr/efo.obo

# Download the annotations
RUN wget https://gist.githubusercontent.com/deepakunni3/6e44ebd3da27ef107c8dba539efc0545/raw/e6bb53f68ffa75482de1336dbc96aabea6ea3f53/topmed_curies_denormalized.tsv -O /opt/solr/geno-pheno-search-solr/topmed_curies_denormalized.tsv

# set up proxy for nginx
RUN wget https://gist.githubusercontent.com/deepakunni3/7033f90f935d3f98d866d77e643b6e7a/raw/ad64c87771b7c471658b98664b2b16264e6bf157/nginx-proxy.conf -O /etc/nginx/nginx.conf

# Configure Solr
RUN set -e; \
  mkdir /opt/solr/${SOLR_DISTRIBUTION}/server/solr/genophenosearch-core && \
  echo "name=genophenosearch-core\nconfig=conf/solrconfig.xml\nschema=schema.xml\ndataDir=data" > /opt/solr/${SOLR_DISTRIBUTION}/server/solr/genophenosearch-core/core.properties && \
  mkdir /opt/solr/${SOLR_DISTRIBUTION}/server/solr/genophenosearch-core/conf && \
  wget https://gist.githubusercontent.com/deepakunni3/65897f361f3b7bda53ec0216d8da772e/raw/bb2f755edc53056273b8fc8784366a8270a33a84/solrconfig.xml -O /opt/solr/${SOLR_DISTRIBUTION}/server/solr/genophenosearch-core/conf/solrconfig.xml && \
  cp /opt/solr/${SOLR_DISTRIBUTION}/server/solr/configsets/basic_configs/conf/elevate.xml /opt/solr/${SOLR_DISTRIBUTION}/server/solr/genophenosearch-core/conf && \
  cp /opt/solr/geno-pheno-search-solr/solr-schema/genophenosearch-schema.xml /opt/solr/${SOLR_DISTRIBUTION}/server/solr/genophenosearch-core/schema.xml

RUN cd /opt/solr/geno-pheno-search-solr && \
python3 /opt/solr/geno-pheno-search-solr/solr-loader/solr_loader.py --solr_url http://localhost:8983/solr/genophenosearch-core --input /opt/solr/geno-pheno-search-solr/topmed_curies_denormalized.tsv

RUN chown -R solr:solr /opt/solr

EXPOSE 80
WORKDIR /opt/solr

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]

CMD ["/bin/bash"]
