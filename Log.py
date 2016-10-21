#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7
# encoding: utf-8

import logging

def InitLogger():
	logger = logging.getLogger("MapCreatorLog")
	logger.setLevel(logging.DEBUG)
	logHandler = logging.FileHandler("MapCreator.log")
	formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
	logHandler.setFormatter(formatter)
	logger.addHandler(logHandler)

def info(in_str):
	logger = logging.getLogger("MapCreatorLog")
	logger.info(in_str)

def warning(in_str):
	logger = logging.getLogger("MapCreatorLog")
	logger.warning(in_str)

def error(in_str):
	logger = logging.getLogger("MapCreatorLog")
	logger.error(in_str)
