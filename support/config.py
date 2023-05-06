
import yaml
from support.log import logging

config_file_path = 'config.yaml'

class Config():
    def __init__(self):
        try:
            self.all_configs = {}
            config_file = open(config_file_path)
            self.all_configs.update(yaml.safe_load(config_file))
            current_profile = self.all_configs['profile']
            profile_config_path = './config-{}.yaml'.format(current_profile)
            profile_config_file = open(profile_config_path)
            self.all_configs.update(yaml.safe_load(profile_config_file))
            logging.info("config init success")
        except Exception:
            err_msg = "Read config file failed."
            logging.error(err_msg)
            raise Exception(err_msg)
        finally:
            config_file.close()
            profile_config_file.close()

    def get_config_by_key(self, key):
        return self.all_configs[key]
    def get_access_token(self):
        return self.all_configs["access_token"]
    def get_cloud_root_path(self):
        return self.all_configs["cloud_root_path"]
    def get_local_root_path(self):
        return self.all_configs["local_root_path"]
    def get_app_id(self):
        return self.all_configs["app_id"]
    def get_app_name(self):
        return self.all_configs["app_name"]
    def get_app_key(self):
        return self.all_configs["app_key"]
    def get_secret_key(self):
        return self.all_configs["secret_key"]
    def get_sign_key(self):
        return self.all_configs["sign_key"]
    def get_bdwp_code(self):
        return self.all_configs["bdwp_code"]
    def get_encrypt_key(self) -> str:
        return self.all_configs["encrypt_key"]
    def get_sync_folder(self):
        return self.all_configs["sync_folder"]
    def get_swap_folder_path(self) -> str:
        return self.all_configs["swap_folder_path"]
    def get_refresh_token(self) -> str:
        return self.all_configs["refresh_token"]
    def get_time_gap(self):
        return self.all_configs["time_gap"]
    def get_key_local_folder(self):
        return "local_folder"
    def get_key_cloud_folder(self):
        return "cloud_folder"
    def get_key_encrypt(self):
        return "encrypt"
    def get_key_sync_folder(self):
        return "sync_folder"
    def get_key_time_gap(self):
        return "time_gap"

config = Config()
