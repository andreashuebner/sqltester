import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from sqltester_driver import command_line_parser

class TestCommandLineParsing(unittest.TestCase):
  def test_no_command_line_arguments(self):
    list_command_line_arguments = command_line_parser([])
    self.assertEqual(list_command_line_arguments, [], ('No command line arguments should result in '
        'empty list'))
    
  def test_input_output_parameters(self):
    list_command_line_arguments = command_line_parser(['--input=input.csv', '--output=output.csv'])
    self.assertEqual(list_command_line_arguments[0], ('input', 'input.csv'), 'First tuple in list' +
      ' should be first command line arguments, second element in tuple the value')
    self.assertEqual(list_command_line_arguments[1], ('output', 'output.csv'), 'Second tuple in list' +
      ' should be second command line arguments, second element in tuple the value')
  
  def test_invalid_output_parameter(self):
    with self.assertRaisesRegexp(RuntimeError, 'Invalid command line parameter --outputoutput') as ex:
      command_line_parser(['--input=input.csv', '--outputoutput'])