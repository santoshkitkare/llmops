import os
import sys

print('Current working directory:', os.getcwd())
current_file = os.path.abspath(__file__)
print('Current file:', current_file)
current_dir = os.path.dirname(current_file)
print('Utils directory:', current_dir)
parent_dir = os.path.dirname(current_dir)
print('Project root:', parent_dir)
config_path = os.path.join(parent_dir, 'config', 'config.yaml')
print('Config path:', config_path)
print('Config exists:', os.path.exists(config_path))
