
from uttest.abstract_test import AbstractTestCase

from facade import facade
from service import file_service
from repository.repository import FileDB, get_filedb
from support import filefolder, time_utils
from support.encrypter import encrypter
from support.config import config

import time, json

class SyncServiceTest(AbstractTestCase):

    file_1_middle_name = "file_1.txt"
    file_2_middle_name = "inner/file_2.txt"
    file_1_local_path = AbstractTestCase.local_unencrypt_path + file_1_middle_name
    file_2_local_path = AbstractTestCase.local_unencrypt_path + file_2_middle_name
    file_1_cloud_path = AbstractTestCase.cloud_unencryp_path + file_1_middle_name
    file_2_cloud_path = AbstractTestCase.cloud_unencryp_path + file_2_middle_name

    def test_client_create_file_unencrypt(self):
        # when
        filefolder.create_file(SyncServiceTest.file_1_local_path, AbstractTestCase.default_file_content)
        filefolder.create_file(SyncServiceTest.file_2_local_path, AbstractTestCase.default_file_content)
        # do
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        # except
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_1_cloud_path) == True
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_2_cloud_path) == True

    def test_client_update_file_unencrypt(self):
        # when
        filefolder.create_file(SyncServiceTest.file_1_local_path, AbstractTestCase.default_file_content)
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_1_cloud_path) == True
        file_code = encrypter.string_hash(SyncServiceTest.file_1_middle_name)
        config.all_configs[config.get_key_time_gap()] = 1
        time.sleep(5)
        # do
        filefolder.append_file(SyncServiceTest.file_1_local_path, "append content")
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        local_db = get_filedb(AbstractTestCase.local_unencrypt_path)
        # except
        file_service.download_file(AbstractTestCase.temp_path, AbstractTestCase.cloud_unencryp_path, SyncServiceTest.file_1_middle_name)
        file_service.download_file(AbstractTestCase.temp_path, AbstractTestCase.cloud_unencryp_path, AbstractTestCase.testfolder_unencryp_db_name)
        actual_db = FileDB(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name)
        actual_content = filefolder.read_file(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name, 'r', filefolder.ReadMode.STRING)
        except_content = AbstractTestCase.default_file_content + "append content"
        assert actual_content == except_content
        assert actual_db.get_db_mtime(file_code) == local_db.get_db_mtime(file_code)

    def test_client_delete_file_unencrypt(self):
        # when
        filefolder.create_file(SyncServiceTest.file_1_local_path, AbstractTestCase.default_file_content)
        filefolder.create_file(SyncServiceTest.file_2_local_path, AbstractTestCase.default_file_content)
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_1_cloud_path) == True
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_2_cloud_path) == True
        time.sleep(2)
        # do
        filefolder.remove_path(SyncServiceTest.file_1_local_path)
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        # except
        local_db = get_filedb(AbstractTestCase.local_unencrypt_path)
        file_service.download_file(AbstractTestCase.temp_path, AbstractTestCase.cloud_unencryp_path, AbstractTestCase.testfolder_unencryp_db_name)
        actual_db = FileDB(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name)
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_1_cloud_path) == False
        file_code = encrypter.string_hash(SyncServiceTest.file_1_middle_name)
        assert local_db.get_delete(file_code) == True
        assert actual_db.get_delete(file_code) == True
        assert local_db.get_delete_time(file_code) == actual_db.get_delete_time(file_code)


    def test_cloud_create_file_unencrypt(self):
        # when
        filefolder.create_file(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name, AbstractTestCase.default_file_content)
        fs_id = file_service.upload_file(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name,SyncServiceTest.file_1_cloud_path, encrypter.get_md5(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name))
        filefolder.create_file(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name, json.dumps({
            encrypter.string_hash(SyncServiceTest.file_1_middle_name): {
                "fs_id": fs_id,
    		    "file_name": SyncServiceTest.file_1_middle_name,
    		    "middle_path": SyncServiceTest.file_1_middle_name,
    		    "local_base_path": AbstractTestCase.local_unencrypt_path,
    		    "cloud_base_path": AbstractTestCase.cloud_unencryp_path,
    		    "source_md5": encrypter.get_md5(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name),
    		    "encrypt_md5": None,
    		    "encrypt": False,
    		    "delete": False,
    		    "delete_time": None,
    		    "local_mtime": None,
    		    "db_mtime": time_utils.get_timestample()
            }
        }, indent=4))
        file_service.upload_file(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name, AbstractTestCase.cloud_unencryp_path + AbstractTestCase.testfolder_unencryp_db_name, encrypter.get_md5(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name))
        # do
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        # expect
        assert filefolder.is_exist(AbstractTestCase.local_unencrypt_path + SyncServiceTest.file_1_middle_name) == True
        local_db = get_filedb(AbstractTestCase.local_unencrypt_path)
        assert encrypter.string_hash(SyncServiceTest.file_1_middle_name) in local_db.get_all()



    def test_cloud_modify_file_unencrypt(self):
        # when
        file_code = encrypter.string_hash(SyncServiceTest.file_1_middle_name)
        filefolder.create_file(SyncServiceTest.file_1_local_path, AbstractTestCase.default_file_content)
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_1_cloud_path) == True
        time.sleep(5)
        filefolder.create_file(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name, AbstractTestCase.default_file_content + " cloud append.")
        fs_id = file_service.upload_file(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name,SyncServiceTest.file_1_cloud_path, encrypter.get_md5(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name))
        cloud_modify_time = time_utils.get_timestample()
        
        filefolder.create_file(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name, json.dumps({
            file_code: {
                "fs_id": fs_id,
    		    "file_name": SyncServiceTest.file_1_middle_name,
    		    "middle_path": SyncServiceTest.file_1_middle_name,
    		    "local_base_path": AbstractTestCase.local_unencrypt_path,
    		    "cloud_base_path": AbstractTestCase.cloud_unencryp_path,
    		    "source_md5": encrypter.get_md5(AbstractTestCase.temp_path + SyncServiceTest.file_1_middle_name),
    		    "encrypt_md5": None,
    		    "encrypt": False,
    		    "delete": False,
    		    "delete_time": None,
    		    "local_mtime": None,
    		    "db_mtime": cloud_modify_time
            }
        }, indent=4))
        file_service.upload_file(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name, AbstractTestCase.cloud_unencryp_path + AbstractTestCase.testfolder_unencryp_db_name, encrypter.get_md5(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name))
        config.all_configs[config.get_key_time_gap()] = 1
        # do
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        # except
        local_db = get_filedb(AbstractTestCase.local_unencrypt_path)
        actual_content = filefolder.read_file(AbstractTestCase.local_unencrypt_path + SyncServiceTest.file_1_middle_name, 'r', filefolder.ReadMode.STRING)
        assert actual_content == AbstractTestCase.default_file_content + " cloud append."
        assert local_db.get_db_mtime(file_code) == cloud_modify_time

    def test_cloud_delete_file_unencrypt(self):
        # when
        file_code = encrypter.string_hash(SyncServiceTest.file_1_middle_name)
        filefolder.create_file(SyncServiceTest.file_1_local_path, AbstractTestCase.default_file_content)
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        assert file_service.is_file_exist_in_cloud(SyncServiceTest.file_1_cloud_path) == True
        file_service.delete_file(SyncServiceTest.file_1_cloud_path)
        local_db = get_filedb(AbstractTestCase.local_unencrypt_path)
        cloud_modify_time = time_utils.get_timestample()
        filefolder.create_file(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name, json.dumps({
            file_code: {
                "fs_id": local_db.get_fs_id(file_code),
    		    "file_name": local_db.get_file_name(file_code),
    		    "middle_path": local_db.get_middle_path(file_code),
    		    "local_base_path": local_db.get_local_base_path(file_code),
    		    "cloud_base_path": local_db.get_cloud_base_path(file_code),
    		    "source_md5": local_db.get_source_md5(file_code),
    		    "encrypt_md5": None,
    		    "encrypt": False,
    		    "delete": True,
    		    "delete_time": cloud_modify_time,
    		    "local_mtime": None,
    		    "db_mtime": cloud_modify_time
            }
        }, indent=4))
        file_service.upload_file(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name, AbstractTestCase.cloud_unencryp_path + AbstractTestCase.testfolder_unencryp_db_name, encrypter.get_md5(AbstractTestCase.temp_path + AbstractTestCase.testfolder_unencryp_db_name))
        # do
        facade.loop_sync(AbstractTestCase.local_unencrypt_path, AbstractTestCase.cloud_unencryp_path, False)
        # except
        assert filefolder.is_exist(SyncServiceTest.file_1_local_path) == False
        local_db = get_filedb(AbstractTestCase.local_unencrypt_path)
        assert local_db.get_delete(file_code) == True
