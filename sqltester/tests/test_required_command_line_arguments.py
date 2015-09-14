import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from sqltester_driver import check_required_command_line_arguments_exist

class TestRequiredCommandLineParameters(unittest.TestCase):
  def setUp(self):
    self.list_required_arguments = ['input', 'output']
  def test_input_argument_missing(self):
    existing_argument_pairs = [('output', 'output.csv')]
    missing_arguments = check_required_command_line_arguments_exist(existing_argument_pairs, 
      self.list_required_arguments)
    self.assertEqual(missing_arguments[0], 'input', 'If input missing, should be returned as ' +
      'missing argument')
  
  def test_output_argument_missing(self):
    existing_argument_pairs = [('input', 'input.csv')]
    missing_arguments = check_required_command_line_arguments_exist(existing_argument_pairs, 
      self.list_required_arguments)
    self.assertEqual(missing_arguments[0], 'output', 'If output missing, should be returned as ' +
      'missing argument')
    
  def test_no_arguments_missing(self):
    existing_argument_pairs = [('input', 'input.csv'), ('output', 'output.csv')]
    missing_arguments = check_required_command_line_arguments_exist(existing_argument_pairs, 
      self.list_required_arguments)
    self.assertEqual(len(missing_arguments), 0, 'If no arguments missing ' +
      'should return empty list')