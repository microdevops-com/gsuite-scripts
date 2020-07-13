# -*- coding: utf-8 -*-
import os
import shutil
import sys
import time
import datetime
import yaml
import logging
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
import json
import argparse

# Custom Exceptions
class DictError(Exception):
    pass

class LoadError(Exception):
    pass

# Check needed key in dict
def check_key(key, c_dict):
    if not key in c_dict:
        raise DictError("No '{0}' key in dict '{1}'".format(key, c_dict))

# Load JSON
def load_json(f, l):
    l.info("Loading JSON from file {0}".format(f))
    try:
        json_dict = json.load(f, object_pairs_hook=OrderedDict)
    except:
        try:
            json_dict = json.load(f)
        except:
            try:
                file_data = f.read()
                json_dict = json.loads(file_data)
            except:
                raise LoadError("Reading JSON from file '{0}' failed".format(f))
    return json_dict

# Load YAML
def load_yaml(f, l):
    l.info("Loading YAML from file {0}".format(f))
    try:
        with open(f, 'r') as yaml_file:
            yaml_dict = yaml.load(yaml_file)
    except:
        raise LoadError("Reading YAML from file '{0}' failed".format(f))
    return yaml_dict

# Load FILE
def load_file_string(f, l):
    l.info("Loading string from file {0}".format(f))
    try:
        with open(f, 'r') as file_file:
            file_string = file_file.read().replace("\n", "")
    except:
        raise LoadError("Reading string from file '{0}' failed".format(f))
    return file_string

# Set logger
def set_logger(console_level, log_dir, log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir, 0o755)
    log_handler = RotatingFileHandler("{0}/{1}".format(log_dir, log_file), maxBytes=10485760, backupCount=10, encoding="utf-8")
    os.chmod("{0}/{1}".format(log_dir, log_file), 0o600)
    log_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    formatter = logging.Formatter(fmt='%(asctime)s %(filename)s %(name)s %(process)d/%(threadName)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S %Z")
    log_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.addHandler(console_handler)
    return logger
