#!/bin/sh

if [[ ${CUSTOM} == True ]];then
	python3 -u main-custom.py
else
	python3 -u main.py
fi
