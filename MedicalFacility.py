from Participant import Participant

class MedicalFacility(Participant):
    def __init__(self, global_params):
        super().__init__(global_params)
        print(f"[MedicalFacility] New third party created. GID = {str(self.GID)[:15]}...")
    
    # Add to the mapping another user and its key to allow reading personal files
    def savePatientData(self, patient_K, patient_hash_GID, patient_attr_list, patient_public_key):
        super().savePatientData(patient_K, patient_hash_GID, patient_attr_list)
        self.patient_data[patient_hash_GID]['public_key'] = patient_public_key # extra data stored here to allow encription of data in behalf of the user
        print(f"[MedicalFacility] Saved parameters to be able to decript/encript files from user <{str(patient_hash_GID)[:15]}...>")

    def writeToPatientFile(self, message, policy_str, data_storage, patient_hash_GID):
        public_key = self.patient_data[patient_hash_GID]['public_key']
        filename = self.patient_data[patient_hash_GID]['filename']

        enc_data = super().writeToPatientFile(message, policy_str, data_storage, public_key, filename)
        print(f"[MedicalFacility] Wrote {str(enc_data['c0'])[:20]}... to user <{str(patient_hash_GID)[:15]}...> personal record")

        return enc_data

    def readPatientFile(self, data_storage, patient_hash_GID, ciphertext_data):
        patient_data = self.patient_data[patient_hash_GID]
        
        decrypted_message = super().readPatientFile(data_storage, ciphertext_data, patient_data['filename'], patient_data['K'], patient_data['attr_list'], patient_data['hashed_GID'])
        print(f"[MedicalFacility] Read {str(decrypted_message)[:20]}... from user {str(patient_hash_GID)[:15]}... personal record file")

        return decrypted_message