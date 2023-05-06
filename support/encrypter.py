
from support.config import config
from cryptography.fernet import Fernet
import hashlib

BUF_SIZE = 65536

class Encrypter():
    def __init__(self):
        key = config.get_encrypt_key().encode()
        self.fernet = Fernet(key)
    def string_encrypt(self, string: str):
        return self.fernet.encrypt(string.encode())
    def string_decrypt(self, string:str):
        return self.fernet.decrypt(string).decode()
    def string_hash(self, string:str): # sha256
        sha256 = hashlib.sha256()
        sha256.update(string.encode())
        return sha256.hexdigest()
    def file_encrypt(self, source_filepath, target_filepath):
        with open(source_filepath, "rb") as file:
            file_data = file.read()
        encrypted_data = self.fernet.encrypt(file_data)
        with open(target_filepath, "wb") as file:
            file.write(encrypted_data)
    def file_decrtpt(self, source_filepath, target_filepath):
        with open(source_filepath, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = self.fernet.decrypt(encrypted_data)
        with open(target_filepath, "wb") as file:
            file.write(decrypted_data)
    def get_sha256(self,file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    def get_md5(self,file_path):
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()
    

encrypter = Encrypter()    
