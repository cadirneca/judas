#!/usr/bin/env python3
# -*- coding: utf8 -*-
# source: synapse https://github.com/TheHive-Project/Synapse

import logging
import os
from configparser import ConfigParser

logger = logging.getLogger('workflows')

def getConf():
    logger.info('%s.getConf starts', __name__)

    currentPath = os.path.dirname(os.path.abspath(__file__))
    app_dir = currentPath + '/../../..'
    cfg = ConfigParser()
    confPath = app_dir + '/conf/judas.conf' # mod here to access to judas.conf
    try:
        cfg.read(confPath)
        return cfg
    except Exception as e:
        logger.error('%s', __name__, exc_info=True)


