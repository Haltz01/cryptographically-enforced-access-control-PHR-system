from DataStorage import DataStorage
from queue import Queue
from Server import *
from Participant import Participant

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair

class Patient(Participant):
    def __init__(self, name, age, allergies, global_params):
        # TODO: Block overwritting name and id, otherwise it will be impossible to find the .txt files
        self.name = name.strip()
        self.age = age
        self.GID = global_params['group'].random(ZR)
        self.allergies = [a.strip() for a in allergies]
        self.dataStorage = DataStorage('./Patient')

    def __str__(self):
        return (f"Patient object\nName: {self.name}\nAllergies: {self.allergies}\nID document: {self.id}\nAge: {self.age}")

    # Generates public key and secret key for an authority given all the attributes from that authority
    # For all, all authorities have the same number of attributes
    # TODO: add parameter to indicate number of attributes for each authority
    def authoritySetup(self, global_params, qty_attributes):
        secret_key = []
        public_key = []

        group = global_params['group']
        g1 = global_params['generator']

        print(f"[Patient - authoritySetup] Generating PK/SK pair for each attribute in the scheme ({self.GID})")
        for i in range(qty_attributes): # for each attribute in the universe of attributes
            # we choose two random exponents alpha_i and y_i
            alpha_i = group.random(ZR)
            y_i = group.random(ZR)
            # print(f"[PE] alpha_i = {alpha_i}")
            # print(f"[PE] y_i = {y_i}")

            e_gg_alpha_i = pair(g1, g1) ** alpha_i # e(g_1, g_1)^{\alpha_i}
            g1_y_i = g1 ** y_i # g^{y_i}
            # print(f"[PE] e_gg_alpha_i = {e_gg_alpha_i}")
            # print(f"[PE] g1_y_i = {g1_y_i}")

            public_key.append((e_gg_alpha_i, g1_y_i)) # PK = {e(g_1, g_1)^{\alpha_i} , g^{y_i}_1 \forall i}
            secret_key.append((alpha_i, y_i)) # SK = {\alpha_i, y_i \forall i}
        print(f"[Patient - authoritySetup] All {qty_attributes} PK/SK pairs were created! ({self.GID})")

        self.secret_key = secret_key
        self.public_key = public_key

        return public_key
    
    # Creates key with a certain list of attributes that can be used to read encripted messages with a policy that matches the list of attributes in the key
    def keyGen(self, attr_list, h_GID, global_params):
        # To create a key for GID for attribute 'i' belonging to an authority, the authority computes K_{i,GID} = g^{\alpha_i}_1 * h_GID^{y_i}
        print(f"[Patient - keyGen] Generating key K for the following list of attributes: {attr_list} ({self.GID})")
        print(f"\t- User hashed GID = {h_GID}")

        g1 = global_params['generator']

        K = {}
        for attr in attr_list:
            attr = int(attr) # we consider that all attributes are going to be integers

            g1_alpha_i = g1 ** self.secret_key[attr][0] # g_{1}^{\alpha_i}

            K[attr] = g1_alpha_i * (h_GID ** self.secret_key[attr][1]) # K_{i,GID} = gg_{1}^{\alpha_i}* h_GID^{y_i}
        print(f"[Patient - keyGen] Key K created! ({self.GID})\n\t- First entry in K: {K[int(attr_list[0])]}")

        return K

    def prettyPrintForFile(self) -> str:
        output = "Name: " + self.name + "\n"
        output += "Age: " + str(self.age) + "\n"
        output += "ID: " + self.id + "\n"
        output += "Alergies: "
        for allergy in self.allergies:
            output += allergy + ","
        output = output[:-1]

        return output

    def sendToServer(self, serverQueue: Queue, inputStr: str): # inputStr could be the encode str
        patientMsgRecord = MsgRecord(self.id, self.name, inputStr)
        serverQueue.put(patientMsgRecord)
        return


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

    