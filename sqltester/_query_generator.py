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
  
TEMPlATE_MINIMUM_DATASETS = """
{{create_table_statement}} {{table_name_to_create}} as
select
case when number_datasets < {{minimum_datasets}} then "Expected at least {{minimum_datasets}} datasets in table
{{table_name}}" else "" end as error_description
from
(
SELECT COUNT(*) as number_datasets
FROM {{table_name}}
{{conditions}}
)x
;
"""

TEMPlATE_MINIMUM_SUM = """
{{create_table_statement}} {{table_name_to_create}} as
select
case when sum_of_field < {{minimum_sum}} then "Expected sum of {{field_name}} in table
{{table_name}} to be at least {{minimum_sum}}" else "" end as error_description
from
(
SELECT SUM({{field_name}}) as sum_of_field
FROM {{table_name}}
{{conditions}}
)x
;
"""
### End of templates


def _generate_tokens(queries_to_parse):
  
  NO_DUPLICATES = r'(?P<NO_DUPLICATES>(?i)no duplicates)'
  ON = r'(?P<ON>(?i)(?:\n|\r|\t|\s)on(?:\n|\r|\t|\s))'
  IN = r'(?P<IN>(?i)(?:\n|\r|\t|\s)in(?:\n|\r|\t|\s))'
  AT_LEAST = r'(?P<AT_LEAST>(?i)at least(?:\n|\r|\t|\s))'
  SUM_OF = r'(?P<SUM_OF>(?i)sum of(?:\n|\r|\t|\s))'
  WHERE_CONDITION = r'(?P<WHERE_CONDITION>(?i)where((?:.|\n|\t|\r|\s)+?);)'
  IDENTIFIER = r'(?P<IDENTIFIER>(?i)[a-z0-9_-]+)'
  WHITESPACE = r'(?P<WHITESPACE>(?i)(?:\n|\r|\s))'
  COMMA = r'(?P<COMMA>(?i),)'
  END_STATEMENT = r'(?P<END_STATEMENT>(?i);)'
  patterns = re.compile('|'.join([NO_DUPLICATES, ON, IN, AT_LEAST, SUM_OF,
    WHERE_CONDITION, END_STATEMENT, WHITESPACE, IDENTIFIER, COMMA]))
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
    
  def _is_number(self, number_to_check):
    ''' Function to check whether input represent int or double
    
    Args:
      number_to_check: The input to check
      
    Returns:
      True if input can be cast to int or double, False if not
      
   '''
   
    is_valid_number = True
    try:
      number_to_check = float(number_to_check)
    except:
      is_valid_number = False
   
    return is_valid_number
  
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
  
  def _replace_create_table_statement(self, template, create_table_statement, table_name):
    ''' Helper function to replace create table statement and table name to create in template
  
    Uses member variables self._create_table_statement and self._table_name_to_create
  
    Args:
      template: The template string
      create_table_statement: The value to substitute placeholder create table statement with
      table_name: The value to substitute placeholder table_name to create with
  
    Returns:
      The template string with placeholders substituted
    '''
      
    template_substituted = self._replace_template_variable(template, 'create_table_statement', 
      self._create_table_statement)
    template_substituted = self._replace_template_variable(template_substituted,
      'table_name_to_create', self._table_name_to_create)
    
    return template_substituted
    
      
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
    ### START PARSING NO DUPLICATE STATEMENT
    if exprtype == "NO_DUPLICATES":
      self._template_to_use = TEMPlATE_NO_DUPLICATES
      self._template_to_use = self._replace_create_table_statement(self._template_to_use, 
        self._create_table_statement, self._table_name_to_create)
  
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
    ### END PARSING NO DUPLICATES STATEMENT ###
    
    ### START PARSING AT LEAST STATEMENT ####
    elif exprtype == "AT_LEAST":
      self._template_to_use = TEMPlATE_MINIMUM_DATASETS
      self._template_to_use = self._replace_create_table_statement(self._template_to_use, 
        self._create_table_statement, self._table_name_to_create)
    
      # Next token must be identifier and this number must be either int or double
      if self._accept('IDENTIFIER'):
        is_number = self._is_number(self.tok.value)
        if is_number == False:
          raise SyntaxError("After 'at least' token expecting number")
        
        self._template_to_use = self._replace_template_variable(self._template_to_use,
          'minimum_datasets', str(self.tok.value))
        
        # Next token expected is IN
        if not self._accept('IN'):
          raise SyntaxError("After 'at least {number_datasets}' token, expecting 'in' token")
        
        # Next token expected identifier (table name)
        if not self._accept('IDENTIFIER'):
          raise SyntaxError("After 'in' token, expecting identifier as table name")
    
        #current token value is table name
        self._template_to_use = self._replace_template_variable(self._template_to_use,
          'table_name', self.tok.value)
    
        # Now either token conditions expected or end of command
        if self._accept('END_STATEMENT'):
          # remove placeholder conditions
          self._template_to_use = self._replace_template_variable(self._template_to_use,
          'conditions', '')
          return self._template_to_use
        
        elif self._accept('WHERE_CONDITION'):
          condition = self.tok.value.replace(';','') # we match ; as well, remove
          self._template_to_use = self._replace_template_variable(self._template_to_use,
            'conditions', condition)
          return self._template_to_use
        else:
          raise SyntaxError("Expect token ';' at end of statement")
       
    ### END PARSING AT LEAST STATEMENT ####
    
    ### START PARSING MINIMUM SUM STATEMENT ###
    elif exprtype == "SUM_OF":
      self._template_to_use = TEMPlATE_MINIMUM_SUM
      self._template_to_use = self._replace_create_table_statement(self._template_to_use, 
        self._create_table_statement, self._table_name_to_create)
      
      # next token must be identifier (the field name)
      if self._accept('IDENTIFIER'):
        self._template_to_use = self._replace_template_variable(self._template_to_use, 
                                 'field_name', self.tok.value)
      else:
        raise SyntaxError("Expecting identifier as field name after token 'sum of'")
      
      # Next token determines what needs to be tested, currently supported at least
      if self._accept('AT_LEAST'):
        pass
      else:
        raise SyntaxError("Expecting token 'at least' after field name in test 'sum of'")
      
      # Next token identifier and needs to be a number
      if self._accept('IDENTIFIER'):
        is_number = self._is_number(self.tok.value)
        if is_number == False:
          raise SyntaxError("Expecting number after token 'at least'")
        else:
          self._template_to_use = self._replace_template_variable(self._template_to_use,
            'minimum_sum', self.tok.value)
      else:
        raise SyntaxError("Expecting number after token 'at least'")
      
      # Next token must be in
      if self._accept('IN'):
        pass
      else:
        raise SyntaxError("Expecting token 'in' after number in sum of command")
      
      #Last required token is identifier (table name) and optionally after where condition(s)
      if self._accept('IDENTIFIER'):
        self._template_to_use = self._replace_template_variable(self._template_to_use,
          'table_name', self.tok.value)
      else:
        raise SyntaxError("Expecting identifier after token 'in'")
      
      # check optionally for where conditions
      if self._accept('END_STATEMENT'):
          # remove placeholder conditions
          self._template_to_use = self._replace_template_variable(self._template_to_use,
          'conditions', '')
          return self._template_to_use
      elif self._accept('WHERE_CONDITION'):
          condition = self.tok.value.replace(';','') # we match ; as well, remove
          self._template_to_use = self._replace_template_variable(self._template_to_use,
            'conditions', condition)
          return self._template_to_use
      else:
          raise SyntaxError("Expect token ';' at end of statement")
    else:
      raise SnytaxError("Unknown command")
    
        
  
      
  
      
      
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
    if self._accept('NO_DUPLICATES') or self._accept('AT_LEAST') or self._accept('SUM_OF'):
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
    
    