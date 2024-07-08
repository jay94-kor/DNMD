import yaml

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config_path = 'config/config.yaml'
settings = load_config(config_path)
