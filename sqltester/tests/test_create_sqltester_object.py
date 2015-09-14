import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from sqltester_driver import SqlTester
from sqltester_driver import MissingCommandLineArgumentsError

class TestCreateSqlTesterObject(unittest.TestCase):
  
  def test_input_parameter_empty_string(self):
    expected_error_message = ('Creating SqlTester object requires path to input file ' +
        'as first argument and path to output file as second argument')
    with self.assertRaisesRegexp(MissingCommandLineArgumentsError, expected_error_message) as ex:
      sqlTester = SqlTester('', 'output.csv')
      
  def test_output_parameter_empty_string(self):
    expected_error_message = ('Creating SqlTester object requires path to input file ' +
        'as first argument and path to output file as second argument')
    with self.assertRaisesRegexp(MissingCommandLineArgumentsError, expected_error_message) as ex:
      sqlTester = SqlTester('input.csv', '')
    