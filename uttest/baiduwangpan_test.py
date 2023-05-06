
import time

# from uttest import abstract_test
from support import filefolder
from support.config import config
from uttest.abstract_test import AbstractTestCase
from support import baiduwangpan
from support.encrypter import encrypter

class SyncServiceTest(AbstractTestCase):

    # file_1_middle_name = "file_1.txt"
    # file_2_middle_name = "inner/file_2.txt"
    # file_1_local_path = AbstractTestCase.local_unencrypt_path + file_1_middle_name
    # file_2_local_path = AbstractTestCase.local_unencrypt_path + file_2_middle_name
    # file_1_cloud_path = AbstractTestCase.cloud_unencryp_path + file_1_middle_name
    # file_2_cloud_path = AbstractTestCase.cloud_unencryp_path + file_2_middle_name

    def test_baidu_wangpan_api(cls):
        test_file1_name = 'file_1.txt'
        test_file2_name = 'file_2.txt'
        local_file1_absolute_path = AbstractTestCase.temp_path + test_file1_name
        cloud_file1_absolute_path = config.get_cloud_root_path() + test_file1_name
        cloud_test_folder_absolute_path = config.get_cloud_root_path() + "testFolder"
        # get user info
        time.sleep(1)
        res = baiduwangpan.get_uinfo()
        assert res["errno"] == 0
        # get quota
        time.sleep(1)
        res = baiduwangpan.get_quota()
        assert res["errno"] == 0
        # upload file
        filefolder.create_file(local_file1_absolute_path, AbstractTestCase.default_file_content)
        assert filefolder.is_exist(local_file1_absolute_path) == True
        md5, fs_id = baiduwangpan.upload_file(local_file1_absolute_path, cloud_file1_absolute_path)
        assert md5 == encrypter.get_md5(local_file1_absolute_path)
        assert fs_id != None
        # assert 
        # create folder
        time.sleep(1)
        res = baiduwangpan.create_folder(cloud_test_folder_absolute_path)
        assert res["errno"] == 0
        # copy file
        time.sleep(1)
        res = baiduwangpan.copy_file(cloud_file1_absolute_path, cloud_test_folder_absolute_path, test_file2_name)
        assert res["errno"] == 0
        # get current level file list
        time.sleep(1)
        res = baiduwangpan.get_current_level_file_list(config.get_cloud_root_path())
        assert res["errno"] == 0
        assert len(res["list"]) == 2
        # get all list
        time.sleep(1)
        res = baiduwangpan.get_multimedia_listall(config.get_cloud_root_path())
        assert res["errno"] == 0
        assert len(res["list"]) == 3
        # search
        time.sleep(1)
        res = baiduwangpan.search_file(test_file1_name, config.get_cloud_root_path()[:-1])
        assert res["errno"] == 0
        assert len(res["list"]) == 1
        # get metadata
        time.sleep(1)
        file_fsid = res["list"][0]["fs_id"]
        res = baiduwangpan.get_file_meta(file_fsid)
        assert res["errno"] == 0
        assert len(res["list"]) == 1
        # download
        time.sleep(1)
        dlink = res["list"][0]["dlink"]
        download_file_name = 'file_download.txt'
        download_file_absolute_file = AbstractTestCase.temp_path + download_file_name
        baiduwangpan.download_file(dlink, download_file_absolute_file)
        assert filefolder.is_exist(download_file_absolute_file)        
        # delete remote file
        time.sleep(1)
        res = baiduwangpan.delete_file(cloud_file1_absolute_path)
        assert res["errno"] == 0
        # delete remote folder
        time.sleep(1)
        res = baiduwangpan.delete_file(cloud_test_folder_absolute_path)
        assert res["errno"] == 0

