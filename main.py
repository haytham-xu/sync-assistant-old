

from facade import facade
from support.config import config
from support.log import logging

if __name__ == "__main__":
    sync_folder_list = config.get_sync_folder()
    for a_sync_folder in sync_folder_list:
        local_base_path: str = a_sync_folder[config.get_key_local_folder()]
        local_base_path = local_base_path if local_base_path.endswith('/') else local_base_path + '/'
        cloud_file_path: str = a_sync_folder[config.get_key_cloud_folder()]
        cloud_file_path = cloud_file_path if cloud_file_path.endswith('/') else cloud_file_path + '/'
        encrypt: bool = a_sync_folder[config.get_key_encrypt()]
        try:
            facade.loop_sync(local_base_path, cloud_file_path, encrypt)
        except Exception as err:
            err_msg = "Error from loop sync" + err
            print(err_msg)
            logging.error(err_msg)
