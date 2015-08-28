import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from sqltester import command_line_parser

class TestCommandLineParsing(unittest.TestCase):
  def test_no_command_line_arguments(self):
    listCommandLineArguments = command_line_parser('')
    self.assertEqual(listCommandLineArguments, '', ('No command line arguments should result in '
        'empty list'))