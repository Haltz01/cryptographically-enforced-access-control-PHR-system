from genericpath import exists
from os import path, mkdir

class DataStorage:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        if (not exists(data_folder)):
            mkdir(data_folder)

    def __str__(self):
        return (f"Data Storage object\nData folder: {self.data_folder}")

    def getFilePath(self, h_GID: str) -> str:
        file_name = str(h_GID) + '.txt'

        # TODO: Fix path traversal vuln here!
        file_path = self.data_folder + '/' + file_name

        return file_path

    def createFile(self, GID) -> bool:
        file_path = self.getFilePath(GID)
        print(f"[DataStorage] Trying to create  file: {file_path}")
        print(f"[DataStorage] Checking if file ({file_path}) already exists...")
        
        if (path.exists(file_path)):
            print(f"[DataStorage] File <{file_path}> already exists!")
            return False # False means something went wrong (file was not created)
        
        print(f"[DataStorage] File <{file_path}> created!")

        return True

    def updateFile(self, GID, input_str) -> bool:
        file_path = self.getFilePath(GID)
        print(f"[DataStorage] Trying to update file: {file_path} ")

        if (not exists(self.data_folder)):
            print(f"[DataStorage] File <{file_path}> doesn't exist!") 
            return False

        file_writer = open(file_path, "wb")
        file_writer.write(input_str)
        file_writer.close()
        print(f"[DataStorage] File <{file_path}> updated!")

        return True

    def readFile(self, GID) -> str:
        file_path = self.getFilePath(GID)
        print(f"[DataStorage] Trying to read file: {file_path} ")

        if (not exists(self.data_folder)):
            print(f"[DataStorage] File <{file_path}> doesn't exist!") 
            return False

        file = open(file_path, "rb")
        encrypted_content = file.read()
        file.close()

        print(f"[DataStorage] File <{file_path}> read!")

        return encrypted_content