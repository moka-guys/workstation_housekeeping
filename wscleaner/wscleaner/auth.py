#!/usr/bin/env python3
"""auth.py

Utlily classes for the workstation cleaner module.

Methods:
    get_config(): Read the DNANexus API token from the application cache file
    dx_set_auth(): Set the DNAnexus authentication token used in each instance of the application

Classes:
    SetKeyAction: Set the DNAnexus authentication token used in future instances of the application and exit
    PrintKeyAction: Print the cached DNAnexus authentication key
"""

from pathlib import Path
from pkg_resources import resource_filename
import json
import argparse
import dxpy

import logging
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'

def get_config(config=CONFIG_FILE):
    """Read the DNANexus API token from the application cache file
    
    Returns:
        filename (object): A python file object
    Raises:
        AttirbuteError: Config file not found.
    """
    # Return the file object containing the cached DNAnexus token if it exists
    filename = resource_filename('wscleaner',config)
    logger.debug(f'Config: {Path(filename).name}')
    if Path(filename).is_file():
        return filename
    else:
        raise AttributeError('Config file not found. Set auth key with --set-key.')

def dx_set_auth(auth_token=None):
    """Set the DNAnexus authentication token used in future instances of the application and exit
    
    Args:
        auth_token (str): A DNAnexus authentication key"""
    if auth_token:
        security_context = {'auth_token_type': 'Bearer', 'auth_token': auth_token}
    else:
        filename = get_config()
        with open(filename, 'r') as f:
            # Password is written to the cache as a dictionary. Loaded here using json module
            pwd = json.load(f)
            security_context = {'auth_token_type': 'Bearer', 'auth_token': pwd['auth_token']}
    dxpy.set_security_context(security_context)

class SetKeyAction(argparse.Action):
    """Set the DNAnexus authentication key based on command line arguments and exit the program.
    
    Inherits from argparse.Action, which initiates __call__() when the linked argument is present.
    """
    # Override argparse.Action.__call__() with desired behaviour
    def __call__(self, parser, namespace, values, option_string=None, config=CONFIG_FILE):
        filename = resource_filename('wscleaner',config)
        with open(filename, 'w') as f:
            # 'values' contains authentication token given on the command line. Store for future
            # wscleaner calls to set as the DNAnexus dxpy security context.
            json.dump({'auth_token': values}, f)
        parser.exit()


class PrintKeyAction(argparse.Action):
    """Print the cached DNAnexus authentication key
    
    Inherits from argparse.Action, which initiates __call__() when the linked argument is present.
    """
    # Override argparse.Action.__call__() with desired behaviour
    def __call__(self, parser, namespace, values, option_string=None):
        filename = get_config()
        with open(filename, 'r') as f:
            pwd = json.load(f)
        print(pwd)
        parser.exit()
