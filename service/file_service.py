
from support import baiduwangpan
from support.log import logging

def upload_file(file_local_path:str, file_cloud_path:str, file_local_md5:str):
    file_cloud_md5, fs_id = baiduwangpan.upload_file(file_local_path, file_cloud_path)
    if file_cloud_md5 == file_local_md5:
        logging.info("%s upload success" % file_local_path)
        return fs_id
    logging.error("%s upload failed" % file_local_path)
    # error code != 0, skip this file
    # cloud_md5 != local_md5, delete cloud, try again

def download_file(local_base_path:str, cloud_base_path:str, middle_path:str):
    try:
        res = baiduwangpan.search_file(middle_path, cloud_base_path)
        fs_id = res['list'][0]['fs_id']
        res = baiduwangpan.get_file_meta(fs_id)
        dlink = res['list'][0]['dlink']
        baiduwangpan.download_file(dlink, local_base_path + middle_path)
    except Exception as err:
        raise Exception("Download file Failed: {}".format(err))
    # todo: shoudl compare md5

def download_file_by_fsid(local_base_path:str, middle_path:str, fs_id:str):
    res = baiduwangpan.get_file_meta(fs_id)
    print(res, local_base_path, middle_path, fs_id)
    dlink = res['list'][0]['dlink']
    baiduwangpan.download_file(dlink, local_base_path + middle_path)
    # todo: shoudl compare md5

def is_file_exist_in_cloud(cloud_file_path:str):
    search_key = cloud_file_path.split('/')[-1]
    search_in = "/".join(cloud_file_path.split('/')[:-1])
    res = baiduwangpan.search_file(search_key, search_in)
    return len(res['list']) != 0

def delete_file(cloud_absolute_path:str):
    baiduwangpan.delete_file(cloud_absolute_path)
