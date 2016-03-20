# MagicHour: Identifying System Events in Raw Log Files 
- - -

### Contribute

Contributors welcome! If you want to contribute, please issue a pull request.

### Read The Docs

Please see our Read The Docs page at <http://magichour.readthedocs.org/en/latest/>.

## About
- - -

#### The Framework:

**MagicHour is a framework for identifying events in raw log files and it is written primarily in Python and PySpark.** The framework performs pre-processing and template discovery on raw log files, organizes templates in time-based windows, and outputs a list of frequently occurring and/or highly correlated events. The identified events are represented as n-tuples of templates and can be used by an analyst to organize large volumes of log files or examine patterns in system events of interest. Most of MagicHour’s components have been implemented for both local computing and distributed computing environments.

The framework includes the following components:  

* ***Pre-processing:*** MagicHour includes functionality to find, replace and store typical high entropy strings from log files. These strings include IP addresses, usernames, hostnames and file paths. The pre-processing step outputs a list of tuples and each tuple contains the processed log line text and all of the original values that were replaced with a simplified variable string (ex: FILEPATH). The purpose of the pre-processing step is to significant reduce the variety of the log lines provided to the template discovery engine.

* ***Template Discovery:*** MagicHour expects log files to resemble a tuple consisting of a timestamp and a message. MagicHour includes two algorithms for template discovery, both of which attempt to map similar processed log lines into groups, which we refer to as templates. Each processed log line is mapped to a template identifier. The two algorithms use different criteria for assessing similarity. The template discovery step outputs a list of tuples and each tuple contains the timestamp and template identifier associated with a processed log line. 

* ***Event Discovery:*** The event discovery component is designed to identify unordered sequences of templates that occur frequently or are highly correlated. The first step is to organize the the output of the template discovery step into multiple time-based windows that resemble row-based transactions. MagicHour includes two algorithms for event discovery on these transactions and the algorithms use different thresholds for assessing sequence frequency and template correlation. The event discovery step outputs a list of tuples that represent events, and each tuple contains a list of template identifiers that are represented in the event.

#### The Research

Prior to building the MagicHour framework, Lab41 surveyed log file analysis and event generation algorithms and metrics. The research included reviews of academic literature, meeting with companies in private industry and consultations with academic researchers.

## Installation and Setup
- - -

#### Package Requirements

Local Computing Components
* git
* python2.7
* pip
* conda

Distributed Computing Components
* Jupyter Notebook
* Apache Spark 
* Apache Hadoop 

#### Installation

##### Cloning the repository

Clone MagicHour repository from the command line, then cd into the directory
```
git clone https://github.com/Lab41/magichour.git
cd magichour
```

##### Kicking the tires

Below we've provided three different ways that you can get set up with MagicHour in order to get it running on your data.

###### Pip

We have dependencies like scikit-learn and hdbscan. scikit-learn requires Numpy and scipy, while hdbscan will require cython. These dependencies will likely need to be installed separately. From the scikit-learn website: We don’t recommend installing scipy or numpy using pip on linux, as this will involve a lengthy build-process with many dependencies. Without careful configuration, building numpy yourself can lead to an installation that is much slower than it should be.)

For Fedora/Debian/CentOS:

yum install -y numpy scipy cython

For Ubuntu/Debian:

apt-get install -y python-numpy python-scipy cython

Note that using Linux package managers to install python dependencies typically installs them in a different location from where pip places packages. Double-check to ensure that the installed location is in your $PYTHONPATH (especially if you are using a virtual environment!)

After doing the above, you should be able to install the dependencies for magichour

pip install -r requirements.txt

If you just want to play around with the codebase and make changes interactively, simply cd into the MagicHour root directory and start the Python REPL. The Python REPL always appends the current directory to PYTHONPATH. Alternatively, you can manually add it into your PYTHONPATH, or use something like virtualenvwrapper’s add2virtualenv command to add it to your environment’s PYTHONPATH.

If you want to install the MagicHour package into your python environment, cd into the MagicHour root directory and call:

pip install .

###### Conda

Anaconda is a completely free Python distribution. It includes more than 400 of the most popular Python packages for science, math, engineering, and data analysis. Anaconda includes conda, a cross-platform package manager and environment manager and seen by some as the successor to pip.

Before getting started, you’ll need both conda and gcc installed on your system.

Once that’s done, if you’re looking to just kick the tires and get a development environment set up as fast as possible, you can create an new environment on your system by calling:

conda env create -f environment.yml

After it finishes, you should have a new conda environment named magichour containing all of the dependencies. Activate it by calling

source activate magichour

if you want to install the MagicHour package into an already existing conda environment, first install conda-build by calling:

conda install conda-build

then cd into the deploy/ directory. Build and install the MagicHour package and its dependencies:

conda build .

conda install —use-local magichour

###### Docker

We are including a Dockerfile to get you a development environment up and running really quickly. Ensure that Docker is installed on your machine before continuing.

Once you have installed Docker on your machine, navigate to the docker_conda/ directory and run the docker build command:

```
cd docker_conda/
docker build -t lab41/magichour .
```

This will build to the Docker image containing all of the dependencies. This Docker image is based on jupyter/pyspark-notebook, maintained by the Jupyter project. It contains Python, Jupyter, as well as a single-node pyspark cluster.

It uses the docker_conda/environment.yml file in order to reproduce a conda environment containing all of the correct dependencies.

Finally, the last step in the Dockerfile is adding a line to the .bashrc file in order to ensure that the newly created magichour environment is used as the default environment whenever the container is started.

Once the image is finished building, you should be able to verify that it exists by running:

```
docker images
```

Start the docker image by running:

```
docker run -d -p 8888:8888 lab41/magichour
```

This starts the container as a daemon running Jupyter notebook on port 8888 of your machine. Navigate to the appropriate URL (likely 192.168.99.100:8888) in order to view the Jupyter interface.

Alternatively, you can also run:

```
docker run -it -p 8888:8888 lab41/magichour /bin/bash
```

to drop into a bash shell for other commands.

