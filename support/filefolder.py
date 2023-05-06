
import os, shutil, enum, copy

def create_file(file_path, file_content):
    parent_path = '/'.join(file_path.split('/')[:-1])
    create_folder(parent_path)
    write_file(file_path, file_content)

def create_folder(folder_path):
    if not is_exist(folder_path):
        os.makedirs(folder_path)

def remove_path(path):
    if is_exist(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def is_exist(file_folder_path):
    return os.path.exists(file_folder_path)

# enumerate
class ReadMode(enum.Enum):
    STEAM = ""
    STRING = "read()"
    STRING_LIST = "readlines()"    

def read_file(file_path, mode='r', read_mode=ReadMode.STRING_LIST):
    try:
        res = None
        with open(file_path, mode) as f:
            match read_mode:
                case ReadMode.STEAM:
                    res = f
                case ReadMode.STRING:
                    res = f.read()
                case _:
                    res = f.readlines()
        return res
    except Exception as err:
        raise Exception("Read file failed: ", err)
    finally:
        f.close()

def append_file(file_path, content, mode='a'):
    try:
        with open(file_path, mode) as f:
            f.write(content)
    except Exception as err:
        raise Exception("Append file failed: ", err)
    finally:
        f.close()

def write_file(file_path, content, mode='w'):
    try:
        with open(file_path, mode) as f:
            f.write(content)
    except Exception as err:
        raise Exception("Write file failed: ", err)
    finally:
        f.close()
