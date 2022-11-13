from charm.toolbox.pairinggroup import ZR
from Participant import Participant
class MedicalFacility(Participant):
    def __init__(self, global_params):
        self.GID = global_params['group'].random(ZR)
        self.patient_keys = {}
        self.patient_hashed_GIDs = []
        print(f"[Medical Facility] Medical Facility created with GID = {self.GID}")
    
    # Add to the mapping another user and its key to allow reading personal files
    def addPatientKey(self, patient_K, patient_hash_GID):
        self.patient_keys[patient_hash_GID] = patient_K
        self.patient_hashed_GIDs.append(patient_hash_GID)
        print(f"[Medical Facility] Added patient's PK, K and hashed GID to list of known patients ({self.GID})")

    # Uses data from "patient_keys" to read their personal files
    def readPatientFile(self, patient_hash_GID):
        pass

    def writePatientFile(self, patient_hash_GID):
        pass