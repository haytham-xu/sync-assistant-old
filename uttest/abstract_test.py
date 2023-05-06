
import unittest, os
from support import filefolder
from support.config import config
from service import file_service

class AbstractTestCase(unittest.TestCase):

    default_file_content = 'abcdefghijklmnopqrstuvwxyz'
    testfolder_unencryp_middle_path = "testfolder_unencrypt/"
    testfolder_unencryp_db_name = ".testfolder_unencrypt.json"
    testfolder_encryp_middle_path = "testfolder_encrypt/"
    testfolder_encryp_db_name = ".testfolder_encrypt.json"

    temp_path = os.getcwd() + '/local/temp/'
    local_unencrypt_path = os.getcwd() + '/local/' + testfolder_unencryp_middle_path
    cloud_unencryp_path = config.get_cloud_root_path() + testfolder_unencryp_middle_path
    local_encryp_path = os.getcwd() + '/local/' + testfolder_encryp_middle_path
    cloud_encryp_path = config.get_cloud_root_path() + testfolder_encryp_middle_path
    

    @classmethod
    def setUp(cls):
        filefolder.create_folder(AbstractTestCase.local_unencrypt_path)
        filefolder.create_folder(AbstractTestCase.local_encryp_path)
        filefolder.create_folder(AbstractTestCase.temp_path)
  
    @classmethod 
    def tearDown(cls):
        filefolder.remove_path(AbstractTestCase.local_unencrypt_path)
        filefolder.remove_path(AbstractTestCase.local_encryp_path)
        filefolder.remove_path(AbstractTestCase.temp_path)
        file_service.delete_file(AbstractTestCase.cloud_encryp_path)
        file_service.delete_file(AbstractTestCase.cloud_unencryp_path)
