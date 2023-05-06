
from support.config import config
from service import file_service

import os,shutil

def init_swap_folder(swap_base_path:str):
    if not os.path.exists(config.get_swap_folder_path()):
        os.mkdir(config.get_swap_folder_path())
    if not os.path.exists(swap_base_path):
        os.mkdir(swap_base_path)
    

def clean_swap_folder(swap_base_path:str):
    shutil.rmtree(swap_base_path)

def precheck_local_db(local_db_path):
    if not os.path.exists(local_db_path):
        with open(local_db_path, "w") as f:
            f.write("{}")
            f.close()

def precheck_cloud_db(swap_base_path, cloud_base_path, db_name):
    if file_service.is_file_exist_in_cloud(cloud_base_path + db_name):
        # local_base_path:str, cloud_base_path:str, middle_path
        file_service.download_file(swap_base_path, cloud_base_path, db_name)
    else:
        with open(swap_base_path + db_name, "w") as f:
            f.write("{}")
            f.close()
