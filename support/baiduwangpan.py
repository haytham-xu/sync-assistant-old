
import requests, json, os, hashlib, time
from support.config import config
from support.log import logging
from support import filefolder

oauth_url = "https://openapi.baidu.com/oauth/2.0/token"
base_url = "https://pan.baidu.com"
headers = {
  'User-Agent': 'pan.baidu.com'
}

def http_request(url, method, headers, params={}, payload={}, files={}):
    res = requests.request(method, url, params=params, headers=headers, data = payload, files = files)
    time.sleep(1)
    if res.status_code == 200:
        return res
    raise Exception("Request failed, eror message: ", res.text)

def bdwp_request_with_token(url, method, headers={}, params={}, payload={} ,files=[]):
    params["access_token"] = config.get_access_token()
    return http_request(url, method, headers, params, payload ,files).json()

def refresh_token():
    params = {"grant_type": "refresh_token", "refresh_token":config.get_refresh_token(), "client_id":config.get_app_key(), "client_secret":config.get_secret_key()}
    return http_request(oauth_url, "GET", headers, params).json()

def get_uinfo():
    url = base_url + "/rest/2.0/xpan/nas"
    params = {"method":"uinfo"}
    return bdwp_request_with_token(url, "GET", headers, params)

def get_quota():
    url = base_url + "/api/quota"
    params = {"checkfree": 1, "checkexpire": 1}
    return bdwp_request_with_token(url, "GET", headers, params)

def upload_file(file_local_path, target_absolute_path):
    # pre create
    pre_create_url = base_url + "/rest/2.0/xpan/file"
    file_size = os.path.getsize(file_local_path)
    content = filefolder.read_file(file_local_path)
    block_list = json.dumps([hashlib.md5("".join(content).encode()).hexdigest()])
    # rtype 1 when path conflict, rename | 2 when path conflict but block_list different, rename | 3 when path conflict, override
    payload = {'path': file_local_path, 'size': file_size, 'block_list': block_list, 'isdir': '0', 'autoinit': '1', 'rtype': '3'}
    params = {"method": "precreate"}
    res = bdwp_request_with_token(pre_create_url, "POST", headers, params, payload)
    if res["errno"] == 0:
        logging.info("    pre-upload %s success" % file_local_path)
    upload_id = res['uploadid']
    # upload block_list
    upload_url = "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2"
    payload = {}
    file_rb = open(file_local_path,'rb')
    files = [('file', file_rb)]
    params = {"path": target_absolute_path, "uploadid": upload_id, "method": "upload", "type": "tmpfile", "partseq": 0}
    res = bdwp_request_with_token(upload_url, "POST", headers, params, payload, files)
    file_rb.close()
    
    if res["md5"] != "":
        logging.info("    blocklist-upload %s success" % file_local_path)
    file_cloud_md5 = res["md5"]
    # create file
    create_url = base_url + "/rest/2.0/xpan/file"
    payload = {'path': target_absolute_path, 'size': file_size, 'uploadid': upload_id, 'block_list': block_list, 'rtype': '3', 'isdir': '0'}
    params = {"method": "create"}
    res = bdwp_request_with_token(create_url, "POST", headers, params, payload)
    if res["errno"] == 0:
        logging.info("    upload %s success" % file_local_path)
    fs_id = res["fs_id"]
    return file_cloud_md5, fs_id

def delete_file(cloud_absolute_path):
    url = base_url + "/rest/2.0/xpan/file"
    params = {"method": "filemanager", "opera": "delete"}
    payload = {"async": "2", "filelist": json.dumps([{'path': cloud_absolute_path}])}
    return bdwp_request_with_token(url, "POST", headers, params, payload)

def get_file_count(cloud_absolute_path):
    res = 0
    for i in range(7):
        res += get_categoryinfo(cloud_absolute_path, i+1)['info'][str(i+1)]['count'] 
    return res

def get_categoryinfo(cloud_absolute_path, category):
    url = base_url + "/api/categoryinfo"
    params = {"category": category, "parent_path": cloud_absolute_path, "recursion": 1}  # category: 1 video、2 music、3 picture、4 document、5 application、6 etc、7 tom
    return bdwp_request_with_token(url, "GET", headers, params)

def create_folder(cloud_absolute_path):
    url = base_url + "/rest/2.0/xpan/file"
    params = {"method": "create"}
    payload = {'path': cloud_absolute_path, 'rtype': '1', 'isdir': '1'}
    return bdwp_request_with_token(url, "POST", headers, params, payload)

def copy_file(cloud_source_file_absolute_path, cloud_target_folder_absolute_path, new_file_name):
    url = base_url + "/rest/2.0/xpan/file"
    params = {"method": "filemanager", "opera": "copy"}
    payload = {"async": "2", "filelist": json.dumps([{'path': cloud_source_file_absolute_path, 'dest': cloud_target_folder_absolute_path, 'newname': new_file_name, 'ondup': 'fail'}])}  # ondup: fail, overwrite
    return bdwp_request_with_token(url, "POST", headers, params, payload)

def get_current_level_file_list(target_cloud_absolute_path, is_only_return_folder=0, start=0, limit=1000):
    url = base_url + "/rest/2.0/xpan/file"
    params = {"dir": target_cloud_absolute_path, "start": start, "limit": limit, "method": "list", "order": "time", "web": 0, "folder": is_only_return_folder, "desc": 1}
    return bdwp_request_with_token(url, "GET", headers, params)

def get_multimedia_listall(target_cloud_absolute_path, start=0, limit=1000):
    url = base_url + "/rest/2.0/xpan/multimedia"
    params = {"method": "listall", "path": target_cloud_absolute_path, "web": 0, "recursion": 1, "start": start, "limit": limit}
    return bdwp_request_with_token(url, "GET", headers, params)

def search_file(search_key, search_in):
    url = base_url + "/rest/2.0/xpan/file"
    params = {"key": search_key, "dir": search_in, "method": "search", "recursion": 1}
    return bdwp_request_with_token(url, "GET", headers, params)

def get_file_meta(file_fsid):
    url = base_url + "/rest/2.0/xpan/multimedia"
    params = {"fsids": json.dumps([file_fsid]), "method": "filemetas", "dlink": 1, "extra": 1, "needmedia": 1}
    return bdwp_request_with_token(url, "GET", headers, params)

def download_file(dlink, local_output_absolute_path):
    dlink += "&access_token=" + config.get_access_token()
    res = http_request(dlink, "GET", headers)
    filefolder.write_file(local_output_absolute_path, res.content, 'wb+')
