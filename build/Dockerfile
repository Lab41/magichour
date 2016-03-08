FROM jupyter/pyspark-notebook
MAINTAINER Lab41

RUN git clone https://github.com/Lab41/magichour.git
WORKDIR magichour
RUN conda env create -f build/environment.yml && \
	conda install -c anaconda-nb-extensions nb_conda_kernels
