import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from _config_parser import _return_configs
from _config_parser import _return_single_config
from _config_parser import ConfigError

class TestConfigParser(unittest.TestCase):
    def test_non_existent_file(self):
      with self.assertRaisesRegexp(IOError, 'Could not open file dont_exist.cfg') as ex:
        configGenerator = _return_configs('dont_exist.cfg')
        for pair in configGenerator:
          pass
    
    def test_misformatted_file_empty_value(self):
      expected_error_message = ('Error in file ' +
        'sqltester/tests/config_test_misformatted_empty_value.cfg in line 2')
      with self.assertRaisesRegexp(ConfigError, expected_error_message) as ex:
        configGenerator = _return_configs('sqltester/tests/config_test_misformatted_empty_value.cfg')
        for pair in configGenerator:
          pass
        
    def test_misformatted_file_missing_separator(self):
      expected_error_message = ('Error in file ' +
        'sqltester/tests/config_test_misformatted_missing_separator.cfg in line 3')
      with self.assertRaisesRegexp(ConfigError, expected_error_message) as ex:
        configGenerator = _return_configs('sqltester/tests/config_test_misformatted_missing_separator.cfg')
        for pair in configGenerator:
          pass
        
    def test_return_single_config_missing(self):
      expected_error_message = ('Missing config attribute test_attribute_1')
      with self.assertRaisesRegexp(ConfigError, expected_error_message) as ex:
        list_config_values = [('test_attribute_2', 'test_value_2'), ('test_attribute_3', 'test_value_3')]
        config_value = _return_single_config(list_config_values, 'test_attribute_1')
        
    def test_return_single_config_existent(self):
      list_config_values = [('test_attribute_2', 'test_value_2'), ('test_attribute_3', 'test_value_3')]
      config_value = _return_single_config(list_config_values, 'test_attribute_3')
      self.assertEqual(config_value, 'test_value_3', 'Should return the correct config value')
      
        
    
        
        
        
        
