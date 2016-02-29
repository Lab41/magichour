FROM jupyter/pyspark-notebook
MAINTAINER Lab41

COPY . /magichour
WORKDIR /magichour
RUN conda install conda-build && \
	conda build --python 2.7 . && \
	conda install --use-local -n python2 magichour
