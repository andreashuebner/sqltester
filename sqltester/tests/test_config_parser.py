import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from _config_parser import _return_configs
from _config_parser import ConfigError

class TestConfigParser(unittest.TestCase):
    def test_non_existent_file(self):
      with self.assertRaisesRegexp(IOError, 'Could not open file dont_exist.cfg') as ex:
        configGenerator = _return_configs('dont_exist.cfg')
        for pair in configGenerator:
          pass
    
    def test_misformatted_file_empty_value(self):
      excepted_error_message = ('Error in file ' +
        'sqltester/tests/config_test_misformatted_empty_value.cfg in line 2')
      with self.assertRaisesRegexp(ConfigError, excepted_error_message) as ex:
        configGenerator = _return_configs('sqltester/tests/config_test_misformatted_empty_value.cfg')
        for pair in configGenerator:
          pass
        
        
        
