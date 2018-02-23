#!/bin/sh
DIR=$(pwd)
WORK_DIR="${DIR}/.virtualenv"

if [ ! -d $WORK_DIR ] 
    then
        mkdir $WORK_DIR
fi
if [ ! -d $WORK_DIR/revapp ] 
    then
        echo "creating virtualenv under $WORK_DIR/revapp"
        virtualenv $WORK_DIR/revapp
        echo "Activating the virtualenv"
        source $WORK_DIR/revapp/bin/activate
        echo "installing the python packages"
        pip install -r $DIR/tools/requirements.txt
fi

source $WORK_DIR/revapp/bin/activate
export FLASK_APP=$DIR/server.py