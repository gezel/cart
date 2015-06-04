#!/bin/bash
export TOP_PID=$$
SOFTWARE_NAME=cart-test
SOLR_VERSION=solr
SOFTWARE_URL=http://cart.embl.de/static/cart-test.tar.gz
SOLR_INDEX_URL=https://vm-lux.embl.de/~deghou/data/drug-enrichment-tool/new-09.01.2015/${SOLR_VERSION}.tar.gz
SOLR_INDEX_URL_TEST=https://vm-lux.embl.de/~deghou/data/drug-enrichment-tool/new-09.01.2015/solr-test-version.tar.gz
PIP_SOURCE=https://bitbucket.org/pdubroy/pip/raw/tip/getpip.py
VIRTUALENV_SOURCE=http://cart.embl.de/static/virtualenv.py
DOWNLOAD_DIRECTORY=`pwd`
#CART_VENV_DIR=~
#CART_VENV_NAME=".cart-venv"
#CART_VENV_DIR_NAME=${CART_VENV_DIR}/${CART_VENV_NAME}
echo -n "Enter the absolute path of the desired installation directory and press [ENTER] (or type directly unter for an installation under ${HOME}): "
read INSTALLATION_DIRECTORY
if [ -z "$INSTALLATION_DIRECTORY" ]
then
    INSTALLATION_DIRECTORY=${HOME}
    INSTALLATION_DIRECTORY=${INSTALLATION_DIRECTORY}/drug-enrichment-tool
    echo "CART will be installed here : ${INSTALLATION_DIRECTORY}"
else
    INSTALLATION_DIRECTORY="${INSTALLATION_DIRECTORY}"
    echo "CART will be installed here : ${INSTALLATION_DIRECTORY}"
fi

SOLR_INSTALLATION_DIRECTORY=${INSTALLATION_DIRECTORY}/solr/solr
DATABASES_DIRECTORY=${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/databases
DESCRIPTION_FILE="${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/static/all-drug-description_ver3.txt"
HEADER_JS="${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/static/header_js.js"
HEADER_JS1="${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/static/header_1.js"
HEADER_JS2="${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/static/header_2.js"
FOOTER_JS="${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/static/footer_js.js"
TEST_DIRECTORY=${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/"test"
PYTHON_VIRTUALENV=${SOFTWARE_NAME}-virtualenv
######################################################
########### USER'S PYTHON VERSIONAS TO BE = 2.7  #####
######################################################
case "$(python --version 2>&1)" in
    *" 2.7"*)
        echo "Python version requirements satisfied!"
        ;;
    *)
        echo "Wrong Python version! Please install python 2.7"
	return
        ;;
esac
######################################################
########### USER'S JAVA VERSION HAS TO BE > 1.5  #####
######################################################
if type -p java; then
    echo found java executable in PATH
    _java=java
elif [[ -n "$JAVA_HOME" ]] && [[ -x "$JAVA_HOME/bin/java" ]];  then
    echo found java executable in JAVA_HOME
    _java="$JAVA_HOME/bin/java"
else
    echo "It looks like java is not installed. Please install java (version 1.6 or higher) and re-run this script."
    return
fi

if [[ "$_java" ]]; then
    version=$("$_java" -version 2>&1 | awk -F '"' '/version/ {print $2}')
    echo version "$version"
    if [[ "$version" > "1.5" ]]; then
        echo "Java version requirement is satisfied( > 1.5)"
    else
        echo "Java version is less than 1.5, please install a new java version before pursuing (java > 1.5 is required to run the name matching tool :-)"
	return 
    fi
fi
######################################################
########### SET THE VIRTUAL ENVIRONMENT    ###########
######################################################
virtualenv_installed=false
if which virtualenv; then
    virtualenv_installed=true
fi
if ! $virtualenv_installed;then
    if which curl;then
        curl ${VIRTUALENV_SOURCE} > ~/virtualenv.py
    else
        wget ${VIRTUALENV_SOURCE} -O ~/virtualenv.py
    fi
#    python ~/virtualenv.py ${CART_VENV_DIR_NAME}
     python ~/virtualenv.py ~/.${PYTHON_VIRTUALENV}
    else
#        virtualenv ${CART_VENV_DIR_NAME}
        virtualenv ~/.${PYTHON_VIRTUALENV}
fi
echo "A virtual environment has been created at: ~/.${PYTHON_VIRTUALENV}"
echo "All python libraries required for this software will be installed within this virtual envinronment"
echo "This virtual environment always needs to be activated before working with ${SOFTWARE_NAME}:"
echo "source ~/.${PYTHON_VIRTUALENV}/bin/activate"

######################################################
########### ACTIVATE VIRTUAL ENVIRONMENT   ###########
######################################################
source ~/.${PYTHON_VIRTUALENV}/bin/activate
######################################################
###########    INSTALL PYTHON LIBRARIES    ###########
######################################################
pip install pandas
pip install matplotlib
pip install scipy
pip install numpy
pip install statsmodels
pip install psutil
pip install networkx
######################################################
########### GET THE TOOL AND THE RESOURCES ###########
######################################################
###CREATE A FOLDER
if [ ! -d "${INSTALLATION_DIRECTORY}" ]; then
    mkdir ${INSTALLATION_DIRECTORY}
fi
cd ${INSTALLATION_DIRECTORY}
### Download tool
if which curl;then
    curl ${SOFTWARE_URL} > ${SOFTWARE_NAME}.tar.gz
else
    wget ${SOFTWARE_URL} -O ${SOFTWARE_NAME}.tar.gz
fi
tar -xvzf ${SOFTWARE_NAME}.tar.gz
### Download solr
if which curl;then
#curl ${SOLR_INDEX_URL} > ${SOLR_INDEX_URL}.tar.gz
    curl ${SOLR_INDEX_URL} > solr.tar.gz
else
    wget ${SOLR_INDEX_URL} -O solr.tar.gz
fi
tar -xvzf solr.tar.gz
######################################################
########### SET THE CONFIG FILE (PATHS etc)###########
######################################################
echo "[solr]
solr_install_dir = ${SOLR_INSTALLATION_DIRECTORY}
# usually, just setting this to 'java' should work fine
jre_cmd = `which java`
jre_mem = 8000m
stop_key = 8c8c8c
# list will be split into words at characters other than the set of alphanumeric ones
# expanded by '.', '-' and '_'
search_indices = collection1

[visualization]
description_file = ${DESCRIPTION_FILE}
header_js = ${HEADER_JS}
header_js1 = ${HEADER_JS1}
header_js2 = ${HEADER_JS2}
footer_js = ${FOOTER_JS}

[annotation]
db_dir = ${DATABASES_DIRECTORY}
db_format = tsv
db_prefix = DB
# list will be split into words at characters other than the set of alphanumeric ones
# expanded by '.', '-' and '_' (so these are also allowed in corresponding file names)
supp_methods = Fisher, ROC
supp_databases = all-drug-description, drug-ATC-code-L4, drugbank-targets-action, STITCH-drug-targets,
                 chembl-ftc-drug-terms, drug-ATC-code, drug-side-effects, TTD-targets-Activation,
                 chemicals_chebi, drugbank-metabolization-action, sider-indications, TTD-targets-Inhibition,
                 drug-ATC-code-L2, drugbank-targets-action-Activation, STITCH-drug-targets-Activation, TTD-targets,
                 drug-ATC-code-L3, drugbank-targets-action-Inhibition, STITCH-drug-targets-Inhibition," > ${SOFTWARE_NAME}/conf/settings.cfg
#####################################################
###########        RUNNING THE TEST        ###########
######################################################
source ~/.${PYTHON_VIRTUALENV}/bin/activate
#source ${HOME}/.${PYTHON_VIRTUALENV}/python-2.7/bin/activate
echo "######## IMPORTANT ########"
echo "To ensure that you always use the right python version when you run ${SOFTWARE_NAME}, always first run the following command before :"
echo "source ${HOME}/.${PYTHON_VIRTUALENV}/bin/activate"
echo "######## RUN TEST FILE (all at once mode) ########"
echo "cd ${INSTALLATION_DIRECTORY}/${SOFTWARE_NAME}/test"
echo "bash RUN_EXAMPLE.sh"
echo "######## IMPORTANT ########"
echo "To delete CART, simply run this :"
echo "rm -r ${INSTALLATION_DIRECTORY}"
