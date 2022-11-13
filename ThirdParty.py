from charm.toolbox.pairinggroup import ZR
from Participant import Participant

# A third party is someone who will be granted read access to patient files
# The patient must provide their key (K) to this party to allow it to read files 
class ThirdParty(Participant):
    def __init__(self, global_params):
        super().__init__(global_params)
        self.GID = global_params['group'].random(ZR)
        self.patient_data = {}
        self.patient_hashed_GIDs = []
        print(f"[ThirdParty] Third Party created with GID = {self.GID}")
    
    # Add to the mapping another user and its key to allow reading personal files
    def addPatientKey(self, patient_K, patient_hash_GID, patient_filename, patient1_attr_list):
        self.patient_data[patient_hash_GID] = {
            'K' : patient_K,
            'filename' : patient_filename,
            'hashed_GID' : patient_hash_GID,
            'attr_list' : patient1_attr_list
        }
        self.patient_hashed_GIDs.append(patient_hash_GID)
        print(f"[ThirdParty] Added patient's K, hashed GID and filename to list of known patients' data ({self.GID})")   

    # Uses data from "patient_keys" to read their personal files
    def readPatientFile(self, data_storage, patient_hash_GID, ciphertext_data):
        patient_data = self.patient_data[patient_hash_GID]
        
        encrypted_message = data_storage.readFile(patient_data['filename'])
        encrypted_message = self.global_params['group'].deserialize(encrypted_message)

        ciphertext_data['c0'] = encrypted_message
        
        encrypted_message = self.decrypt(ciphertext_data, patient_data['K'], patient_data['attr_list'], patient_data['hashed_GID'])
        return encrypted_message
        