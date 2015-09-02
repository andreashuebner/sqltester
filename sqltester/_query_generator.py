import re
import collections

from _config_parser import _return_configs
from _config_parser import _return_single_config

### Start of templates ###

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

  def __init__(self, queries_to_parse):
    self._PATH_CONFIG_FILE = 'config.cfg'
    
    self._queries_to_parse = queries_to_parse
    self._config_tuples = list(_return_configs(self._PATH_CONFIG_FILE))
    self._generated_queries = '' # Will return all generated queries
    self._list_config_values = _return_configs(self._PATH_CONFIG_FILE)
    
    # get single config values
    self._table_prefix = _return_single_config(self._list_config_values, 'table_prefix')
    self._inner_join_statement = _return_single_config(self._list_config_values, 'inner_join_statement')
    self._left_join_statement = _return_single_config(self._list_config_values, 'left_join_statement')
    
    
  
  
 
  def _parse(self):
    self.tokens = _generate_tokens(self._queries_to_parse)
    self.tok = None
    self.nexttok = None
    self._advance()
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
    exprval = self.command()
    return exprval
  
  def command(self):
    if self._accept('NO_DUPLICATES'):
      command_val = self.tok.value;
      print(command_val)
      return command_val
    
    