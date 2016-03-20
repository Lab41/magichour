FROM jupyter/pyspark-notebook
MAINTAINER Lab41

# Clone the Git repo
RUN git clone https://github.com/Lab41/magichour.git

# Ensure the current dir is magichour
WORKDIR magichour

# Create the conda environment according to docker_conda/environment.yml
RUN conda env create -f docker_conda/environment.yml

# Activate the new environment whenever a bash shell is created
RUN echo "source activate magichour" >> /home/jovyan/.bashrc
