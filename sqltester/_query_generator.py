import re
import collections
import random

from _config_parser import _return_configs
from _config_parser import _return_single_config

### Start of templates ###
TEMPlATE_NO_DUPLICATES = """
{{create_table_statement}} {{table_name_to_create}} as
select
count(*) as number_duplicates,
case when count(*) > 0 then "Duplicates found in table {{table_name}}" else "" end as error_description
from
(
SELECT {{field_names}}, COUNT(*)
FROM {{table_name}}
GROUP BY {{field_names}}
HAVING COUNT(*) > 1
)x
;
"""
### End of templates


def _generate_tokens(queries_to_parse):
  
  NO_DUPLICATES = r'(?P<NO_DUPLICATES>(?i)no duplicates)'
  ON = r'(?P<ON>(?i)on)'
  IN = r'(?P<IN>(?i)in)'
  IDENTIFIER = r'(?P<IDENTIFIER>(?i)[a-z0-9_-]+)'
  WHITESPACE = r'(?P<WHITESPACE>(?i)(?:\n|\r|\s))'
  COMMA = r'(?P<COMMA>(?i),)'
  END_STATEMENT = r'(?P<END_STATEMENT>(?i);)'
  patterns = re.compile('|'.join([NO_DUPLICATES, ON, IN, 
    END_STATEMENT, WHITESPACE, IDENTIFIER, COMMA]))
  Token = collections.namedtuple('Token', ['type', 'value'])
  scanner = patterns.scanner(queries_to_parse)
  for m in iter(scanner.match, None):
    tok = Token(m.lastgroup, m.group())
    if tok.type != 'WHITESPACE':
      yield tok

class Evaluator(object):

  def __init__(self, queries_to_parse, path_config_file = None):
    self._PATH_CONFIG_FILE = path_config_file if path_config_file is not None else 'config.cfg'
    self._queries_to_parse = queries_to_parse
    self._config_tuples = list(_return_configs(self._PATH_CONFIG_FILE))
    self._generated_queries = '' # Will return all generated queries
    self._list_config_values = _return_configs(self._PATH_CONFIG_FILE)
    
    # get single config values
    self._create_table_statement = _return_single_config(self._list_config_values, 'create_table_statement')
    self._table_prefix = _return_single_config(self._list_config_values, 'table_prefix')
    self._inner_join_statement = _return_single_config(self._list_config_values, 'inner_join_statement')
    self._left_join_statement = _return_single_config(self._list_config_values, 'left_join_statement')
  
    #list of all created tables, later used to create union statement for final table
    self._created_tables = []
    
    # variables used and updated for each parse
    self._template_to_use = ''
    
    
  
  def _create_random_number(self, min, max):
    ''' Function to generate a random number
    
    Args:
      min: The minimum limit for random number
      max: The maximum limit for random number
    
    Returns:
      The generated random number >= min and <= max
    '''
    
    random.seed()
    random_number = random.randint(min, max) 
    return random_number
  
  def _replace_template_variable(self, template, variable_name, variable_value):
    ''' Replace a template variable in current template.
  
  Args:
    template: The template string
    variable_name: The name of the variable (in template in format {{variable_name}})
    variable_value: The value the variable needs to be substituted with
  
  Returns:
    A string with the passed in template contant, but all variable names subsituted with the value
  '''
  
    return_template = template.replace('{{' + variable_name + '}}', variable_value)
  
    return return_template
  
 
  def parse(self):
    queries = self._queries_to_parse.split(';')
    list_test_queries = [] #list of all generated test queries
    for query in queries:
      if len(query) >= 5: 
        self.tokens = _generate_tokens(query + ';')
        self.tok = None
        self.nexttok = None
        self._advance()
        self._table_name_to_create = (self._table_prefix + '_' + 
          str(self._create_random_number(1, 999999999)))
        self._created_query = self._expr()
        self._created_query = self._created_query.replace('\n',' ')
        self._created_query = re.sub(r'\s+',' ', self._created_query)
        self._created_query = self._created_query.strip()
        list_test_queries.append(self._created_query)
  
    return list_test_queries
  
  def _advance(self):
    'Advance one token ahead'
    self.tok, self.nexttok = self.nexttok, next(self.tokens, None)
  
  def _accept(self, toktype):
    '''Test and consume the next token if it matches toktype'''
    if self.nexttok and self.nexttok.type == toktype:
      self._advance()
      return True
    else:
      return False
    
  def _expect(self, toktype):
    '''Consume next token if it matches toktype or raise Syntax error'''
    
    if not self._accept(toktype):
      raise SyntaxError('Expected ' + toktype)
      
  # Grammar rules
  
  def _expr(self):
    exprval, exprtype = self._command()
    if exprtype == None:
      raise SyntaxError("Expecting command like 'no duplicates' as first token")
    
    # Which template to use
    if exprtype == "NO_DUPLICATES":
      self._template_to_use = TEMPlATE_NO_DUPLICATES
      self._template_to_use = self._replace_template_variable(self._template_to_use, 
                                 'create_table_statement', self._create_table_statement)
      
      self._template_to_use = self._replace_template_variable(self._template_to_use, 
                                 'table_name_to_create', self._table_name_to_create)
  
      # next token must be on, otherwise syntax error
      if self._accept('ON'):
        field_names = self._field_names()
      else:
        print("Warning: Missing 'on' token after command, auto corrected")
        field_names = self._field_names()
       
      string_field_names = ','.join(field_names)
      self._template_to_use = self._replace_template_variable(self._template_to_use, 
                                 'field_names', string_field_names)
      
      # next exptected token in
      if self._accept('IN'):
        # next token is the table name
        if self._accept('IDENTIFIER'):
          table_name = self.tok.value
          self._template_to_use = self._replace_template_variable(self._template_to_use, 
                                 'table_name', table_name)
        
          if self._accept('END_STATEMENT'):
            print("Reached end of statement")
            return self._template_to_use
          else:
            raise SyntaxError("Expect token ';' at end of statement")
          
        
  
      else:
        raise SyntaxError("Expecting token 'in' after field names")
  
      
      
  def _field_names(self):
    ''' Parses field names field_name_1, field_name_2 etc. and returns a list of all field names '''
    state = "start"
    field_names = []
    while self._accept('COMMA') or self._accept('IDENTIFIER'):
      if state == "start" and self.tok.type == 'COMMA':
        raise SyntaxError('Field names cannot start with a comma')
      if state == "start" and self.tok.type == 'IDENTIFIER':
        field_names.append(self.tok.value)
      if state == "field_name_parsed" and self.tok.type == 'IDENTIFIER':
        raise SyntaxError('Field names need to be seperated with a comma')
      if state == "comma_parsed" and self.tok.type == 'COMMA':
        raise SyntaxError("Found invalid token ',,'")
      if state == "comma_parsed" and self.tok.type == 'IDENTIFIER':
        field_names.append(self.tok.value)
        state = "field_name_parsed"
      
    return field_names
      
  def _command(self):
    ''' Checks whether input matches known command statement and returns pair token_value
        and token_type
    
    '''
    if self._accept('NO_DUPLICATES'):
      command_type = self.tok.type;
      command_val = self.tok.value
      return command_val, command_type
    else:
      return None, None
  
  def _table_name(self):
    ''' Checks whether input is valid table name and returns pair token_value and token_type '''
    if self._accept('IDENTIFIER'):
      command_type = self.tok.type;
      command_val = self.tok.value
      return command_val, command_type
    else:
      return None, None
    
    