
from facade import facade_support
from service import file_service
from repository.repository import FileDB, get_filedb
from support import time_utils, filefolder
from support.config import config
from support.encrypter import encrypter
from support.log import logging

import os, copy, time

def loop_sync(local_base_path:str, cloud_base_path:str, encrypt:bool):
    folder_name = local_base_path.split('/')[-2]
    db_name = '.' + folder_name + '.json'
    swap_base_path = config.get_swap_folder_path() + folder_name + "/"
    local_db_path = local_base_path + db_name
    cloud_db_local_path = swap_base_path + db_name
    cloud_db_cloud_path = cloud_base_path + db_name
    facade_support.init_swap_folder(swap_base_path)
    facade_support.precheck_local_db(local_db_path)
    facade_support.precheck_cloud_db(swap_base_path, cloud_base_path, db_name)
    # local_db = FileDB(local_base_path)
    # cloud_db = FileDB(swap_base_path)
    local_db = get_filedb(local_base_path)
    cloud_db = get_filedb(swap_base_path)
    duplicate_local_db = copy.copy(local_db.get_all())
    duplicate_cloud_db = copy.copy(cloud_db.get_all())
    for (file_local_parent_path, _, files) in os.walk(local_base_path, topdown=True):
        for file_name in files:
            try:
                local_file_execution(file_name, file_local_parent_path, local_base_path, cloud_base_path, local_db, cloud_db, duplicate_local_db, duplicate_cloud_db)
            except Exception as err:
                err_msg = "Sync file failed: {}, with error message: {}".format(file_name, err)
                logging.error(err_msg)

    # print("local db", duplicate_local_db)
    # print("cloud db", duplicate_cloud_db)
    for file_code in duplicate_local_db:
        # file already deleted, do nothing
        if local_db.get_delete(file_code):
            logging.info("already deleted, do nothing: %s" % file_local_path)
            continue
        # client delete
        cloud_path = local_db.get_cloud_base_path(file_code) + local_db.get_middle_path(file_code)
        file_service.delete_file(cloud_path)
        delete_time = time_utils.get_timestample()
        local_db.update_file_delete_status(file_code, True, delete_time)
        cloud_db.update_file_delete_status(file_code, True, delete_time)
        info_msg = "client delete, so remove cloud: %s" % cloud_path
        print(info_msg)
        logging.info(info_msg)

    for file_code in duplicate_cloud_db:
        if cloud_db.get_delete(file_code):
            continue
        # remote created
        file_local_path = cloud_db.get_local_base_path(file_code) + cloud_db.get_middle_path(file_code)
        
        fs_id = cloud_db.get_fs_id(file_code)
        file_service.download_file_by_fsid(cloud_db.get_local_base_path(file_code), cloud_db.get_middle_path(file_code), fs_id)
        local_mtime = int(os.path.getmtime(file_local_path))
        local_db.save(file_code, 
                                cloud_db.get_fs_id(file_code), 
                                cloud_db.get_file_name(file_code), 
                                cloud_db.get_middle_path(file_code), 
                                cloud_db.get_local_base_path(file_code),
                                cloud_db.get_cloud_base_path(file_code), 
                                cloud_db.get_source_md5(file_code), 
                                local_mtime, 
                                cloud_db.get_db_mtime(file_code))
        logging.info("remote creted: %s" % file_local_path)

    file_service.upload_file(cloud_db_local_path, cloud_db_cloud_path, encrypter.get_md5(cloud_db_local_path))
    facade_support.clean_swap_folder(swap_base_path)


def local_file_execution(file_name:str, file_local_parent_path:str, local_base_path:str, cloud_base_path:str, local_db:FileDB, cloud_db:FileDB, duplicate_local_db, duplicate_cloud_db):
    if file_name.startswith("."):
        return
    file_local_path = file_local_parent_path + file_name if file_local_parent_path[-1] == '/' else file_local_parent_path + '/' + file_name
    file_middle_path = file_local_path.removeprefix(local_base_path)
    file_cloud_path = cloud_base_path + file_middle_path
    file_local_md5 = encrypter.get_md5(file_local_path)
    # print("-f1-> ", os.path.getmtime(file_local_path))
    os_mtime = int(os.path.getmtime(file_local_path))
    # print("-f2-> ", os_mtime)
    db_mtime = time_utils.get_timestample()
    file_code = encrypter.string_hash(file_middle_path)

    if local_db.is_exist(file_code):
        del duplicate_local_db[file_code]
    if cloud_db.is_exist(file_code):
        del duplicate_cloud_db[file_code]
    # client create
    if not local_db.is_exist(file_code ):
        fs_id = file_service.upload_file(file_local_path, file_cloud_path, file_local_md5)
        local_db.save(file_code, fs_id, file_name, file_middle_path, local_base_path, cloud_base_path, file_local_md5, os_mtime, db_mtime)
        cloud_db.save(file_code, fs_id, file_name, file_middle_path, local_base_path, cloud_base_path, file_local_md5, None, db_mtime)
        info_msg = "Client create A: {}".format(file_local_path)
        # print(info_msg)
        logging.info(info_msg)
        return
    # client create
    if not cloud_db.is_exist(file_code):
        fs_id = file_service.upload_file(file_local_path, file_cloud_path, file_local_md5)
        db_mtime = local_db.get_db_mtime(file_code)
        cloud_db.save(file_code, fs_id, file_name, file_middle_path, local_base_path, cloud_base_path, file_local_md5, None, db_mtime)
        info_msg = "Client create B: {}".format(file_local_path)
        # print(info_msg)
        logging.info(info_msg)
        return
    # remote delete
    if cloud_db.get_delete(file_code):
        filefolder.remove_path(file_local_path)
        local_db.update_file_delete_status(file_code, cloud_db.get_delete(file_code), cloud_db.get_delete_time(file_code))
        info_msg = "Remote delete: {}".format(file_local_path)
        print(info_msg)
        logging.info(info_msg)
        return
    file_local_mtime = local_db.get_local_mtime(file_code)
    # impossible case
    if os_mtime < file_local_mtime:
        logging.error("error, mtime in db could not newer than os_mtimw for file %s" % file_local_path)
        return
    # print("-f3-> ", os_mtime, file_local_mtime, os_mtime > file_local_mtime)
    # client modify, update local_mtime and local db_mtime
    if os_mtime > file_local_mtime:
        local_db.update_file_local_mtime(file_code, os_mtime)
        local_db.update_file_db_mtime(file_code, os_mtime)
        # file_local_mtime = os_mtime
        # db_mtime = os_mtime
    cloud_db_mtime = cloud_db.get_db_mtime(file_code)
    local_db_mtime = local_db.get_db_mtime(file_code)
    # print("-f4-> ", local_db_mtime, cloud_db_mtime)
    # file not change
    if abs(cloud_db_mtime - local_db_mtime) <= config.get_time_gap():
        info_msg = "File not changed: {}".format(file_local_path)
        # print(info_msg)
        logging.info(info_msg)
        return
    # local modify
    if local_db_mtime > cloud_db_mtime:
        file_service.upload_file(file_local_path, file_cloud_path, file_local_md5)
        cloud_db.update_file_db_mtime(file_code, local_db_mtime)
        # print(cloud_db.get_db_mtime(file_code), local_db.get_db_mtime(file_code))
        # local_db.update_file_db_mtime(file_code, )
        info_msg = "Local modify:: {}".format(file_local_path)
        # print(info_msg)
        logging.info(info_msg)
        return
    # remote modify
    if cloud_db_mtime > local_db_mtime:
        # def download_file(local_base_path:str, cloud_base_path:str, middle_path:str):
        # file_service.download_file_by_fsid(cloud_db.get_local_base_path(file_code), cloud_db.get_middle_path(file_code), fs_id)
        # file_service.download_file(file_cloud_path, file_local_parent_path)
        # def download_file_by_fsid(local_base_path:str, middle_path:str, fs_id:str):
        file_service.download_file_by_fsid(cloud_db.get_local_base_path(file_code), cloud_db.get_middle_path(file_code), cloud_db.get_fs_id(file_code))
        local_db.update_file_db_mtime(file_code, cloud_db_mtime)
        info_msg = "Remote modify: {}".format(file_local_path)
        # print(info_msg)
        logging.info(info_msg)
    # "encrypt_md5", "encrypt", "delete", "delete_time"
