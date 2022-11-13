from DataStorage import DataStorage
from queue import Queue
from Server import *
from MedicalFacility import *
class Patient:
    def __init__(self, name: str, age: int, id: str, allergies: list):
        # TODO: Block overwritting name and id, otherwise it will be impossible to find the .txt files
        self.name = name.strip()
        self.age = age
        self.id = id.strip()
        self.allergies = [a.strip() for a in allergies]
        self.dataStorage = DataStorage('./Patient')

    def __str__(self):
        return (f"Patient object\nName: {self.name}\nAllergies: {self.allergies}\nID document: {self.id}\nAge: {self.age}")

    def prettyPrintForFile(self) -> str:
        output = "Name: " + self.name + "\n"
        output += "Age: " + str(self.age) + "\n"
        output += "ID: " + self.id + "\n"
        output += "Alergies: "
        for allergy in self.allergies:
            output += allergy + ","
        output = output[:-1]

        return output

    def sendToServer(self, serverQueue: Queue, inputStr: str): # inputStr need to be the encrypted str
        patientMsgRecord = MsgRecord(self.id, self.name, inputStr)
        serverQueue.put(patientMsgRecord)
        return
    
    def sendToMedicalFacility(self, MedicalFacility:MedicalFacility, MedicalFacilityQueue:Queue, inputList:list): 
        # inputList is the public key of patient and usk for Medical Facilities
        if (self.id in MedicalFacility.patientIds):
            MedicalFacilityQueue.put(inputList)

class Person:
    def __init__(self, name: str, age: int, id: str):
        # TODO: Block overwritting name and id, otherwise it will be impossible to find the .txt files
        self.name = name.strip()
        self.age = age
        self.id = id.strip()
        self.readAccess = {}
        self.writeAccess = {}

    def getReadAccess(self, patient: Patient, sk: int):
        self.readAccess[patient.id] = sk

    def getWriteAccess(self, patient: Patient, pk: int):
        self.writeAccess[patient.id] = pk

class Provider():
    def __init__(self, id: str):
        # TODO: Block overwritting name and id, otherwise it will be impossible to find the .txt files
        self.id = id.strip()
        self.writeAccess = {}
    
    def getWriteAccess(self, patient: Patient, sk: int):
        self.writeAccess[patient.id] = sk

class Doctor(Person):
    pass

class Insurance(Person):
    pass

class Employer(Person):
    pass

class Hospital(Provider):
    pass

class HealthClub(Provider):
    pass

    