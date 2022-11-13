from Participant import Participant

# A third party is someone who will be granted read access to patient files
# The patient must provide their key (K) to this party to allow it to read files 
class ThirdParty(Participant):
    def __init__(self, global_params):
        super().__init__(global_params)
        print(f"[ThirdParty] New third party created. GID = {str(self.GID)[:15]}...")
    
    # Add to the mapping another user and its key to allow reading personal files
    def savePatientData(self, patient_K, patient_hash_GID, patient1_attr_list):
        super().savePatientData(patient_K, patient_hash_GID, patient1_attr_list)
        print(f"[ThirdParty] Saved parameters to be able to decript files from user <{str(patient_hash_GID)[:15]}...>")

    # Uses data from "patient_keys" to read their personal files
    def readPatientFile(self, data_storage, patient_hash_GID, ciphertext_data):
        patient_data = self.patient_data[patient_hash_GID]
        
        decrypted_message = super().readPatientFile(data_storage, ciphertext_data, patient_data['filename'], patient_data['K'], patient_data['attr_list'], patient_data['hashed_GID'])
        print(f"[ThirdParty] Read {str(decrypted_message)[:20]}... from user {str(patient_hash_GID)[:15]}... personal record file")

        return decrypted_message
        