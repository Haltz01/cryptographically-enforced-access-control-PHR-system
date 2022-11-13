from genericpath import exists
from os import path, mkdir
from Patient import Patient
from MedicalFacility import MedicalFacility

class DataStorage:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        if (not exists(data_folder)):
            mkdir(data_folder)

    def __str__(self):
        return (f"Data Storage object\nData folder: {self.data_folder}")

    def getPatientFilePath(self, id: str, name: str) -> str:
        patient_name_formatted = name.replace(" ", "_")
        file_name = id + '-' + patient_name_formatted + '.txt'

        # TODO: Fix path traversal vuln here!
        file_path = self.data_folder + '/' + file_name

        return file_path

    def createPatientFile(self, patient: Patient) -> bool:
        print(f"[DataStorage] Trying to create patient file")
        file_path = self.getPatientFilePath(patient.id, patient.name)
        print(f"[DataStorage] Checking if patient file ({file_path}) already exists...")
        
        if (path.exists(file_path)):
            print(f"[DataStorage] File <{file_path}> already exists!")
            return False # False means something went wrong (file was not created)
        
        print(f"[DataStorage] File <{file_path}> created!")

        return True

    def updatePatientFile(self, patient: Patient) -> bool:
        print("[DataStorage] Trying to update patient file") 
        file_path = self.getPatientFilePath(patient.id, patient.name)
        if (not exists(file_path)):
            print(f"[DataStorage] File <{file_path}> doesn't exist!") 
            return False

        file_writer = open(file_path, "w")
        file_writer.write(patient.prettyPrintForFile())
        file_writer.close()
        print(f"[DataStorage] File <{file_path}> updated!")

        return True

    def getMedicalFacilityFilePath(self, fid: str, fname: str) -> str:
        medicalFacility_name_formatted = fname.replace(" ", "_")
        file_name = fid + '-' + medicalFacility_name_formatted + '.txt'

        # TODO: Fix path traversal vuln here!
        file_path = self.data_folder + '/' + file_name

        return file_path

    def createMedicalFacilityFile(self, medicalFacility: MedicalFacility) -> bool:
        print(f"[DataStorage] Trying to create medicalFacility file")
        file_path = self.getMedicalFacilityFilePath(medicalFacility.falicityId, medicalFacility.name)
        print(f"[DataStorage] Checking if medicalFacility file ({file_path}) already exists...")
        
        if (path.exists(file_path)):
            print(f"[DataStorage] File <{file_path}> already exists!")
            return False # False means something went wrong (file was not created)
        
        print(f"[DataStorage] File <{file_path}> created!")

        return True

    def updateMedicalFacilityFile(self, medicalFacility: MedicalFacility) -> bool:
        print("[DataStorage] Trying to update medicalFacility file") 
        file_path = self.getMedicalFacilityFilePath(medicalFacility.falicityId, medicalFacility.name)
        if (not exists(file_path)):
            print(f"[DataStorage] File <{file_path}> doesn't exist!") 
            return False

        file_writer = open(file_path, "w")
        file_writer.write(medicalFacility.prettyPrintForFile())
        file_writer.close()
        print(f"[DataStorage] File <{file_path}> updated!")

        return True