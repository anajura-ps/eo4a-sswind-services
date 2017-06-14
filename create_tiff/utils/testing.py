"""
Testing utilities.
"""

# Conveniently import all assertions in one place. 
# Inspired by https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/utils/testing.py
# TODO: this was a copy from the GAVITA repo, so there are some GAVIP-specific settings etc
# below - these will be removed over time.
#from django.conf import settings
#from django.test import TestCase
import glob
import logging
from nose.tools import assert_equal
from nose.tools import assert_greater 
from nose.tools import assert_greater_equal
from nose.tools import assert_less_equal
from nose.tools import assert_not_equal
from nose.tools import assert_true
from nose.tools import assert_false
from nose.tools import assert_raises
from nose.tools import raises
from nose import SkipTest
from nose import with_setup
import os
import pandas as pd
import shutil
import tempfile
import unittest
from unittest import skipUnless

__all__ = ["assert_equal", "assert_not_equal",
           "assert_true",
           "assert_false", "assert_raises"
           ]

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(processName)s [%(levelname)s] %(module)s - %(message)s',level=logging.INFO)

SKIP_REASON = "Executed only in unit testing mode."

#UNITTESTING_MODE = not getattr(settings, 'IN_EO4ATLANTIC_BUILD', False)
"""
Used to ensure that certain tests are only run in unit testing mode
"""
#logger.info('settings.IN_EO4ATLANTIC_BUILD: %s, UNITTESTING_MODE: %s', settings.IN_EO4ATLANTIC_BUILD, UNITTESTING_MODE)


def setUp():
    # Create a temporary directory
    return tempfile.mkdtemp()
        

def tearDown(test_dir):
    # Remove the directory after the test
    if test_dir and isinstance(test_dir, str):
        shutil.rmtree(test_dir)
            

