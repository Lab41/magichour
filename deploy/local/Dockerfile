FROM continuumio/miniconda
MAINTAINER Lab41

COPY . /magichour
WORKDIR /magichour
RUN apt-get update && \
	apt-get install -y gcc && \
	conda install conda-build && \
	conda build . && \
	conda install --use-local magichour
