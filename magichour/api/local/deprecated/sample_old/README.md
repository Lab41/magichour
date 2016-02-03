Setting up a virtual environment

1) I like to install virtualenv, virtualenvwrapper in order to keep python environments separate.

pip install virtualenv virtualenvwrapper

2) Add three lines to your shell startup file (.bashrc, .profile, etc.) to set the location where the virtual environments should live, the location of your development project directories, and the location of the script installed with this package:

export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh

3) source ~/.bashrc

4) workon magichour_venv (you can choose your own name for your virtenv)


Setting up Jupyter so you can work in a notebook.

