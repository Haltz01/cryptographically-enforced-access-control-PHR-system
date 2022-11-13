from charm.toolbox.pairinggroup import ZR

# A third party is someone who will be granted read access to patient files
# The patient must provide their key (K) to this party to allow it to read files 
class ThirdParty:
    def __init__(self, global_params):
        self.GID = global_params['group'].random(ZR)
        self.patient_data = {}
        self.patient_hashed_GIDs = []
        print(f"[ThirdParty] Third Party created with GID = {self.GID}")
    
    # Add to the mapping another user and its key to allow reading personal files
    def addPatientKey(self, patient_public_key, patient_K, patient_hash_GID):
        self.patient_data[patient_hash_GID] = {
            'pk' : patient_public_key,
            'K' : patient_K
        }
        self.patient_hashed_GIDs.append(patient_hash_GID)
        print(f"[ThirdParty] Added patient's PK, K and hashed GID to list of known patients ({self.GID})")

    # Uses data from "patient_data" to read their personal files
    def readPatientFile(self, patient_hash_GID):
        pass
        