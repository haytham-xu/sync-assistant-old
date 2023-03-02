
import yaml
from support.log import logging

class Config():
    def __init__(self):
        self.all_configs = {}
        with open('config.yaml', 'r') as config:
            self.all_configs.update(yaml.safe_load(config))
            current_profile = self.all_configs['profile']
            profile_config_path = './config-{}.yaml'.format(current_profile)
            with open(profile_config_path, 'r') as currentProfileConfig:
                self.all_configs.update(yaml.safe_load(currentProfileConfig))
        logging.info("config init success")
    def get_config_by_key(self, key):
        return self.all_configs[key]
    
    def get_access_token(self):
        return self.all_configs["access_token"]

config = Config()
