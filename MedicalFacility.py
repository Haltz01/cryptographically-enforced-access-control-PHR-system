from charm.toolbox.pairinggroup import ZR
from Participant import Participant
class MedicalFacility(Participant):
    def __init__(self, global_params):
        super().__init__(global_params)
        self.GID = global_params['group'].random(ZR)
        self.patient_data = {}
        self.patient_hashed_GIDs = []
        print(f"[Medical Facility] Medical Facility created with GID = {self.GID}")
    
    # Add to the mapping another user and its key to allow reading personal files
    def savePatientData(self, patient_K, patient_hash_GID, patient_filename, patient1_attr_list, patient_public_key):
        self.patient_data[patient_hash_GID] = {
            'K' : patient_K,
            'filename' : patient_filename,
            'hashed_GID' : patient_hash_GID,
            'attr_list' : patient1_attr_list,
            'public_key' : patient_public_key
        }
        self.patient_hashed_GIDs.append(patient_hash_GID)
        print(f"[MedicalFacility] Added patient's K, hashed GID, filename and PK to list of known patients' data ({self.GID})")  

    # Uses data from "patient_data" to read their personal files
    def readPatientFile(self, patient_hash_GID):
        pass

    def writeToPatientFile(self, data_storage, enc_message, patient_hash_GID):
        msg_bytes = self.global_params['group'].serialize(enc_message)
        filename = self.patient_data[patient_hash_GID]['filename']
        data_storage.updateFile(filename, msg_bytes)