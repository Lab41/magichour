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

##### Using conda

We recommend creating a conda environment instead of installing into your global distribution
```
conda create --name magichour python
source activate magichour
```

Navigate to the deploy folder and use conda to install MagicHour packages from the command line
```
cd deploy
conda build .
conda install --use-local magichour
```

##### Using pip
We recommend using conda to install this package due to its dependencies on cython, scipy, numpy, and scikit-learn. However, if you are able to install them via another method, you can use pip to install the magichour package.

```
pip install .
```
or
```
python setup.py install
```
