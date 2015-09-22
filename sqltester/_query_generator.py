import re
import collections
import random
import os.path

from _config_parser import _return_configs
from _config_parser import _return_single_config
from _config_parser import ConfigError

file_directory = os.path.dirname(os.path.realpath(__file__))

### Templates for aggregation ####
TEMPlATE_AGGREGATION = """
{{create_table_statement}} {{table_name_to_create}} as
select
error_description
from {{table_list}}
where error_description != ''
;
"""
## END Templates for aggregation ###
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
  WHITESPACE = r'(?P<WHITESPACE>(?i)(?:\s))'
  LINE_BREAK = r'(?P<LINE_BREAK>(?i)(?:\n|\r))'    
  COMMA = r'(?P<COMMA>(?i),)'
  END_STATEMENT = r'(?P<END_STATEMENT>(?i);)'
  patterns = re.compile('|'.join([NO_DUPLICATES, ON, IN, AT_LEAST, SUM_OF,
    WHERE_CONDITION, END_STATEMENT, WHITESPACE, IDENTIFIER, COMMA]))
  Token = collections.namedtuple('Token', ['type', 'value'])
  scanner = patterns.scanner(queries_to_parse)
  for m in iter(scanner.match, None):
    tok = Token(m.lastgroup, m.group())
    if tok.type != 'WHITESPACE' and tok.type != 'LINE_BREAK':
      yield tok

class Evaluator(object):

  def __init__(self, queries_to_parse, path_config_file = None):
    self._PATH_CONFIG_FILE = path_config_file if path_config_file is not None else\
      os.path.join(file_directory,'config.cfg')
    self._queries_to_parse = queries_to_parse
    self._config_tuples = list(_return_configs(self._PATH_CONFIG_FILE))
    self._generated_queries = '' # Will return all generated queries
    self._list_config_values = _return_configs(self._PATH_CONFIG_FILE)
    self._current_line = 0
    
    # get single required config values
    self._create_table_statement = _return_single_config(self._list_config_values, 'create_table_statement')
    self._table_prefix = _return_single_config(self._list_config_values, 'table_prefix')
    self._inner_join_statement = _return_single_config(self._list_config_values, 'inner_join_statement')
    self._left_join_statement = _return_single_config(self._list_config_values, 'left_join_statement')
      
     # check of optional config values
    self._commands_to_run_after = None
    try:
      self._commands_to_run_after = _return_single_config(self._list_config_values, 'commands_after_each_query')
    except ConfigError:
      pass
  
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
  
  def _create_aggregation_query(self, list_tables):
    ''' Function that returns aggregation query (union over all created test tables
    
    Args:
      list_tables: The list of created test tables
      
    Returns:
      The generated aggregation query as string
   '''
   
    _table_name_to_create = (self._table_prefix + '_' + 'aggregation' + '_' + 
          str(self._create_random_number(1, 999999999)))
   
    template_aggregation = TEMPlATE_AGGREGATION
    # Substitute create table statement
    _template_to_use = self._replace_create_table_statement(template_aggregation, 
        self._create_table_statement, _table_name_to_create)
   
    _table_names = ','.join(list_tables)
    template_aggregation = self._replace_template_variable(_template_to_use, 
     'table_list', _table_names)
   
    return template_aggregation
   
    
      
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
      create_table_statement)
    template_substituted = self._replace_template_variable(template_substituted,
      'table_name_to_create',table_name)
    
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
  
  def _add_commands_after(self, query, commands_to_add, table_name):
    ''' Member function to add commands to a generated query.
    
    In commands to add, the template variable {{table_name}} can be used and needs to be 
    substituted with the generated table name with random suffix.
    
    Args:
      query: The generated query
      commands_to_add: The commmands to add, can include template variable {{table_name}}
      table_name: The generated random table name (we need to substitute it)
      
    Returns:
      The query with commands appended
    '''
      
    commands_to_add = commands_to_add.replace('{{table_name}}', table_name)
    query = query + ' ' + commands_to_add
    return query
  def write_queries(self, list_queries_to_write, output_path):
    ''' Member function to write test queries into file
  
  Args:
    list_queries_to_write: List with all test queries to write
    output_path: Path to output file
    '''
    try:
      with open(output_path, 'w') as f:
        f.write('\n\n'.join(list_queries_to_write))
    except:
      raise RuntimeError('Cannot open ' + output_path + ' for writing')
      
    
  def parse(self):
    queries = self._queries_to_parse.split(';')
    list_test_queries = [] #list of all generated test queries
    for query in queries:
      if len(query) >= 5: 
        self._current_line = self._current_line + 1
        self.tokens = _generate_tokens(query + ';')
        self.tok = None
        self.nexttok = None
        self._advance()
        self._table_name_to_create = (self._table_prefix + '_' + 
          str(self._create_random_number(1, 999999999)))
        self._created_query = self._expr()
        # Check if member self._commands_to_run_after is not None, in this case we need to 
        # append the commands to run and to substitute {{table_name}}
        if self._commands_to_run_after is not None:
          self._created_query = self._add_commands_after(self._created_query, self._commands_to_run_after, 
              self._table_name_to_create)
        self._created_query = self._created_query.replace('\n',' ')
        self._created_query = re.sub(r'\s+',' ', self._created_query)
        self._created_query = self._created_query.replace(' )', ')')
        self._created_query = self._created_query.replace('( ', '(')
        self._created_query = self._created_query.strip()
        list_test_queries.append(self._created_query)
        self._created_tables.append(self._table_name_to_create)
    
    # Create and append aggregation query
    aggregation_query = self._create_aggregation_query(self._created_tables)
    list_test_queries.append(aggregation_query)
    list_queries_return = list(list_test_queries) # make copy before returning
    # now create final statement for tests
      
    return list_queries_return
  
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
            return self._template_to_use
          else:
            raise SyntaxError("Expect token ';' at end of statement in line " + str(self._current_line))
    
    
      else:
        raise SyntaxError("Expecting token 'in' after field names in line " + str(self._current_line))
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
          raise SyntaxError("After 'at least' token expecting number in line " + str(self._current_line))
        
        self._template_to_use = self._replace_template_variable(self._template_to_use,
          'minimum_datasets', str(self.tok.value))
        
        # Next token expected is IN
        if not self._accept('IN'):
          raise SyntaxError("After 'at least {number_datasets}' token, expecting 'in' token in line "
              + str(self._current_line))
        
        # Next token expected identifier (table name)
        if not self._accept('IDENTIFIER'):
          raise SyntaxError("After 'in' token, expecting identifier as table name in line "
          + str(self._current_line))
    
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
        raise SyntaxError("Expecting identifier as field name after token 'sum of' in line " + 
            str(self._current_line))
      
      # Next token determines what needs to be tested, currently supported at least
      if self._accept('AT_LEAST'):
        pass
      else:
        raise SyntaxError("Expecting token 'at least' after field name in command 'sum of' in line " + 
            str(self._current_line))
      
      # Next token identifier and needs to be a number
      if self._accept('IDENTIFIER'):
        is_number = self._is_number(self.tok.value)
        if is_number == False:
          raise SyntaxError("Expecting number after token 'at least' in line " + str(self._current_line))
        else:
          self._template_to_use = self._replace_template_variable(self._template_to_use,
            'minimum_sum', self.tok.value)
      else:
        raise SyntaxError("Expecting number after token 'at least' in line " + str(self._current_line))
      
      # Next token must be in
      if self._accept('IN'):
        pass
      else:
        raise SyntaxError("Expecting token 'in' after number in sum of command in line " + str(self._current_line))
      
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
    
    