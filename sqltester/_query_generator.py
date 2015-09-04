import re
import collections

from _config_parser import _return_configs
from _config_parser import _return_single_config

### Start of templates ###
TEMPlATE_NO_DUPLICATES = """
{{create_table_statement}} {{table_name}} as
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
  patterns = re.compile('|'.join([NO_DUPLICATES]))
  Token = collections.namedtuple('Token', ['type', 'value'])
  scanner = patterns.scanner(queries_to_parse)
  for m in iter(scanner.match, None):
    tok = Token(m.lastgroup, m.group())
    yield tok

class Evaluator(object):

  def __init__(self, queries_to_parse, path_config_file = None):
    if path_config_file != None:
      self._PATH_CONFIG_FILE = path_config_file
    else:
      self._PATH_CONFIG_FILE = 'config.cfg'
    
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
    ''' Function to generate a random number '''
    return 1
  
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
  
    print('Template after replacement')
    print(return_template)
    return return_template
  
 
  def _parse(self):
    self.tokens = _generate_tokens(self._queries_to_parse)
    self.tok = None
    self.nexttok = None
    self._advance()
    self._template_to_use = '' # reset, can be different for each statement
    return self.expr()
  
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
  
  def expr(self):
    exprval, exprtype = self.command()
    if exprtype == None:
      raise SyntaxError("Expecting command like 'no duplicates' as first token")
    
    # Which template to use
    if exprtype == "NO_DUPLICATES":
      self._template_to_use = TEMPlATE_NO_DUPLICATES
      TEMPLATE_NO_DUPLICATES = self._replace_template_variable(self._template_to_use, 
                                 'create_table_statement', self._create_table_statement)
    
  
  def command(self):
    if self._accept('NO_DUPLICATES'):
      command_type = self.tok.type;
      command_val = self.tok.value
      print(command_type)
      return command_val, command_type
    else:
      return None, None
    
    