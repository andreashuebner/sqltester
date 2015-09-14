import sys
import re
from _query_generator import Evaluator

# Some constants
REQUIRED_COMMAND_LINE_ARGUMENTS = ['input', 'output']

class SqlTester(object):
  
  def __init__(self, input, output):
    ''' Constructor function for SqlTester.
    
    Args:
      input: Path to input file with test cases
      output: Path to output file to write the generated sql queries
    
    Throws:
      MissingCommandLineArgumentsError in case input or output are missing or are empty strings
   '''
    
    if input == '' or output == '':
      raise MissingCommandLineArgumentsError('Creating SqlTester object requires path to input file '
          + 'as first argument and path to output file as second argument')
      
    self._path_input_file = input
    self._path_output_file = output
    
  def create_test_queries(self):
    #read in content of input file
    with open(self._path_input_file, 'r') as f:
      content = f.read()
      evaluator = Evaluator(content)
      list_queries = evaluator.parse()
      evaluator.write_queries(list_queries, self._path_output_file)    

class MissingCommandLineArgumentsError(Exception):
  ''' Exception type for missing command line arguments '''
  pass

def check_file_exists_readable(path_to_file):
  ''' Checks whether we can read from the file.
  
  Args:
    path_to_file: Path to file to read
  
  Returns:
    True if no OSException occured, otherwise False
 '''
  
  try:
    with open(path_to_file, 'r') as f:
      return True
  except IOError:
    return False
    
def check_required_command_line_arguments_exist(list_command_line_arguments,
  list_required_parameters):
  ''' Function to check that we received all required command line parameters.
  
  Args:
    list_command_line_arguments: A list of tuples, first element of tuple command line argument
    list_required_parameters: A list of required command line arguments
  
  Returns:
    Empty list if no parameters are missing, or the list of required command line parameters
 '''
  
  list_required = list(list_required_parameters) # make copy to avoid side effects
  list_arguments_not_found = [] # here we will save the arguments not found
  list_existing_arguments = []
  
  for pair in list_command_line_arguments:
    command_line_argument, command_line_arguments = pair
    list_existing_arguments.append(command_line_argument)
  
  for required_argument in list_required:
    if required_argument not in list_existing_arguments:
      list_arguments_not_found.append(required_argument)
      
  return list_arguments_not_found

def command_line_parser(list_command_line_arguments):
  ''' Parses command line options provided in format --[commandLineParameter]=[commandLineValue]
  e.g. --input=test_cases.csv --ouput=output.csv
  
  Args:
    list_command_line_arguments: A list of all command line parameters (except sys.argv[0])
    
  Returns:
    A list of tuples, the first element the command line parameter, the second element the command
      line value (e.g. [('input', 'test_cases.csv'), ('output', 'output.csv')]
  '''
  
  list_command_line_tuples = []
  for argument in list_command_line_arguments:
    list_elements = argument.split('=') # should result in two elements, format is --argument=value
    if len(list_elements) != 2:
      raise RuntimeError('Invalid command line parameter {}'.format(argument))
    
    command_line_argument = list_elements[0]
    command_line_argument = command_line_argument.replace('--','')
    command_line_argument = command_line_argument.strip()
    command_line_value = list_elements[1]
    command_line_value = command_line_value.strip()
    command_line_pair = (command_line_argument, command_line_value)
    list_command_line_tuples.append(command_line_pair)
  
  return list_command_line_tuples

def main():
  if len(sys.argv) < 3:
    raise MissingCommandLineArgumentsError('Usage: python sqltester.py --input=[pathInputFile] ' +
      ' --output=[pathOutputFile]')
  
  list_command_line_parameters = command_line_parser(sys.argv[1:])
  missing_command_line_arguments = check_required_command_line_arguments_exist(list_command_line_parameters, 
    REQUIRED_COMMAND_LINE_ARGUMENTS)
  
  if missing_command_line_arguments:
    raise MissingCommandLineArgumentsError('Usage: python sqltester.py --input=[pathInputFile] ' +
      ' --output=[pathOutputFile]')
  
  path_input_file = ''
  path_output_file = ''
  for pair in list_command_line_parameters:
    command_line_argument, command_line_value = pair
    if command_line_argument == 'input':
      path_input_file = command_line_value
    if command_line_argument == 'output':
      path_output_file = command_line_value
  
  #read in content of input file
  with open(path_input_file, 'r') as f:
    content = f.read()
    evaluator = Evaluator(content)
    list_queries = evaluator.parse()
    evaluator.write_queries(list_queries, path_output_file)
    
  
  

if __name__ == '__main__':
  main()