class ConfigError(Exception):
  ''' Exception type for errors in configuration file '''
  pass

def _return_single_config(list_tuples_configs, attribute):
  ''' Returns the value for a single configuration from a list of config tuple values
  
  Args:
    list_tuples_configs: A list with config tuples [(config_parameter, config_value)]
    attribute: The config attribute to extract
  
  Returns:
    The value for the config parameter
    
  Raises:
    ConfigError if config_parameter not in list
    
 '''
  
  for pair in list_tuples_configs:
    config_attribute, config_value = pair
    if config_attribute == attribute:
      return config_value
  
  # If we are still here, then config parameter was not found
  raise ConfigError('Missing config attribute ' + attribute)
def _return_configs(path_config_file):
  ''' Generator function to return configs as tuples
  
  Args:
    path_config_file: The path to the configuration file
  
  Returns:
    A tuple in format (config_parameter, config_value) with each iteration
  
  Raises:
    IOError in case the config file cannot be openend
    ConfigError in case of misformatted config file
  '''
  try:
    with open(path_config_file) as f:
      line_counter = 1
      for line in f:
        line = line.strip()
        if line != '':
          fields = line.split(':')
          if len(fields) != 2:
            raise ConfigError('Error in file {} in line {}'.format(path_config_file, line_counter))
          configParameter = fields[0].strip()
          configValue = fields[1].strip()
          if configParameter == '' or configValue == '':
            raise ConfigError('Error in file {} in line {}'.format(path_config_file, line_counter))  
          yield configParameter, configValue
        line_counter += 1
  except IOError as error:
    error_message = 'Could not open file {}'.format(path_config_file)
    raise IOError(error_message)
  except Exception as error:
    raise error
  
  
  