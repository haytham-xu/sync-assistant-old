
import json, enum
from support import filefolder
from support.log import logging
from support.filefolder import ReadMode

def get_filedb(folder_path:str):
    folder_name = folder_path.split('/')[-2]
    db_name = '.' + folder_name + '.json'
    db_file_path = folder_path + db_name
    return FileDB(db_file_path)

class FileDB():
    def __init__(self, db_file_path:str):
        self.db_file_path = db_file_path
        self.db = json.loads(filefolder.read_file(self.db_file_path, 'r', ReadMode.STRING))

    def get_all(self):
        return self.db
    def get_by_code(self, file_code):
        return self.db[file_code]
    def save(self, file_code, fs_id, file_name, middle_path_and_file_name, local_base_path, cloud_base_path, file_local_md5, local_mtime, db_mtime, encrypt=False, encrypt_md5=None, delete=False, delete_time=None):
        self.db[file_code] = {
            "fs_id": fs_id,
    		"file_name": file_name,
    		"middle_path": middle_path_and_file_name,
    		"local_base_path": local_base_path,
    		"cloud_base_path": cloud_base_path,
    		"source_md5": file_local_md5,
    		"encrypt_md5": encrypt_md5,
    		"encrypt": encrypt,
    		"delete": delete,
    		"delete_time": delete_time,
    		"local_mtime": local_mtime,
    		"db_mtime": db_mtime
        }
        self.persistence()
            
    def update_file_delete_status(self, file_code, delete, delete_time):
        self.check_file_code(file_code)
        self.db[file_code]["delete"] = delete
        self.db[file_code]["delete_time"] = delete_time
        self.persistence()
    def update_file_db_mtime(self, file_code, db_mtime):
        self.check_file_code(file_code)
        self.db[file_code]["db_mtime"] = db_mtime
        self.persistence()
    def update_file_local_mtime(self, file_code, local_mtime):
        self.check_file_code(file_code)
        self.db[file_code]["local_mtime"] = local_mtime
        self.persistence()
    def persistence(self):
        filefolder.write_file(self.db_file_path, json.dumps(self.db, indent=4))
    def is_exist(self, file_code):
        return file_code in self.db


    def check_file_code(self, file_code):
        if file_code not in self.db:
            raise Exception("File code not found in current DB")
    def get_fs_id(self, file_code):
        return self.db[file_code]["fs_id"]
    def get_file_name(self, file_code):
        return self.db[file_code]["file_name"]
    def get_middle_path(self, file_code):
        return self.db[file_code]["middle_path"]
    def get_local_base_path(self, file_code):
        return self.db[file_code]["local_base_path"]
    def get_cloud_base_path(self, file_code):
        return self.db[file_code]["cloud_base_path"]
    def get_source_md5(self, file_code):
        return self.db[file_code]["source_md5"]
    def get_encrypt_md5(self, file_code):
        return self.db[file_code]["encrypt_md5"]
    def get_encrypt(self, file_code):
        return self.db[file_code]["encrypt"]
    def get_delete(self, file_code):
        return self.db[file_code]["delete"]
    def get_delete_time(self, file_code):
        return self.db[file_code]["delete_time"]
    def get_local_mtime(self, file_code):
        return self.db[file_code]["local_mtime"]
    def get_db_mtime(self, file_code):
        return self.db[file_code]["db_mtime"]
