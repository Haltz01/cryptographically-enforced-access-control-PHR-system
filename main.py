from Patient import Patient
from PredicateEncryption import PredicateEncryption
from ThirdParty import ThirdParty
from MedicalFacility import MedicalFacility
from DataStorage import DataStorage

from charm.toolbox.pairinggroup import GT, pair

def main():
    test()

def checkMessageEqual(original, decripted):
    if (original == decripted):
        print("[main] Decripted text is equal to the original (random) message!")
    else:
        print("[main] Decripted text is NOT equal to the original (random) message!")
        
def test():
    print(f"[main] Creating DataStorage")
    data_storage = DataStorage('./patients')
    print("===========================")

    print(f"[main] Initializing PredicateEncription()")
    pe = PredicateEncryption() 
    global_params = pe.getGlobalParams()
    print("===========================")

    print(f"[main] Creating Patient 1 for testing")
    patient1 = Patient("Test 1", global_params, data_storage)
    print("===========================")

    print(f"[main] Creating an authority associated to Patient 1")
    patient1.authoritySetup(global_params, 2) # 2 attributes
    print("===========================")

    print(f"[main] Writting random data to Patient 1's personal file")
    random_data = pe.group.random(GT)

    enc_data = patient1.writeToPatientFile(random_data, "0", data_storage)
    print("===========================")

    print(f"[main] Reading data from Patient 1's personal file")
    
    # TODO: store the policy and C inside users' personal data file
    # For testing purposes, we are only storing the encripted message and using this temporary map
    temp_ciphertext_data = {
        'policy_str': enc_data['policy_str'],
        'c0': "",
        'C': enc_data['C']
    }
    patient1_hashedGID = patient1.getHashGID()

    msg = patient1.readPatientFile(data_storage, temp_ciphertext_data)

    checkMessageEqual(random_data, msg)
    print("===========================")

    print(f"[main] Generating a read access-grating key K from Patient 1")
    patient1_K, patient1_attr_list = patient1.keyGen(["0"], global_params)
    print("===========================")

    print(f"[main] Creating a Third Party")
    third_party = ThirdParty(global_params)
    print("===========================")

    print(f"[main] Giving the paramenters from Patient 1 (K, hashed GID, etc.) to the Third Party")
    third_party.savePatientData(patient1_K, patient1_hashedGID, patient1_attr_list)
    print("===========================")
    
    print(f"[main] Reading the personal record from Patient 1 with K (as Third Party)")
    msg = third_party.readPatientFile(data_storage, patient1_hashedGID, temp_ciphertext_data)

    checkMessageEqual(random_data, msg)
    print("===========================")

    print(f"[main] Reading the personal record from Patient 1 with WRONG K (as Third Party)")
    patient1_K[0] = pair(patient1_K[0], patient1_K[0]) # Modifying one of the values for K...
    third_party.savePatientData(patient1_K, patient1_hashedGID, patient1_attr_list)
    msg = third_party.readPatientFile(data_storage, patient1_hashedGID, temp_ciphertext_data)

    checkMessageEqual(random_data, msg)
    print("===========================")

    print(f"[main] Creating a second Third Party")
    third_party2 = ThirdParty(global_params)
    print("===========================")

    print(f"[main] Generating a read access-grating key K (with attributes not used in the user's record file policy) from Patient 1")
    patient1_K2, patient1_attr_list2 = patient1.keyGen(["1"], global_params)
    print("===========================")

    print(f"[main] Giving the paramenters from Patient 1 (K, hashed GID, etc.) to the second Third Party")
    third_party2.savePatientData(patient1_K2, patient1_hashedGID, patient1_attr_list2)
    print("===========================")
    
    print(f"[main] Reading the personal record from Patient 1 with WRONG K (as Third Party) -- policy doesn't match")
    msg = third_party2.readPatientFile(data_storage, patient1_hashedGID, temp_ciphertext_data)

    checkMessageEqual(random_data, msg)
    print("===========================")

    print(f"[main] Reading the personal record from Patient 1 with WRONG K (as Third Party) -- trying to fake correct attributes")
    third_party2.patient_data[patient1.getHashGID()]['attr_list'] = ["0"] # this is just for testing purposes
    third_party2.patient_data[patient1.getHashGID()]['K'][0] = third_party2.patient_data[patient1.getHashGID()]['K'][1] # this is just for testing purposes
    msg = third_party2.readPatientFile(data_storage, patient1_hashedGID, temp_ciphertext_data)

    checkMessageEqual(random_data, msg)
    print("===========================")

    print(f"[main] Creating Medical Facility")
    med_fac = MedicalFacility(global_params)
    print("===========================")

    print(f"[main] Giving information from Patient 1 to Medical Facility")
    med_fac.savePatientData(patient1_K, patient1_hashedGID, patient1_attr_list, patient1.public_key)
    print("===========================")

    print(f"[main] Medical Facility writing data to Patient 1 file using his/her public key")
    random_data = pe.group.random(GT)
    enc_data = med_fac.writeToPatientFile(random_data, "0", data_storage, patient1_hashedGID)

    temp_ciphertext_data = {
        'policy_str': enc_data['policy_str'],
        'c0': "",
        'C': enc_data['C']
    }

    print("===========================")

    print(f"[main] Reading the personal record from Patient 1 as Patient 1")
    msg = patient1.readPatientFile(data_storage, temp_ciphertext_data)

    checkMessageEqual(random_data, msg)
    print("===========================")

if __name__ == "__main__":
    main()