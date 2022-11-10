from Patient import Patient
from DataStorage import DataStorage
from PredicateEncryption import PredicateEncryption

def main():
    test()

def pretty_print_enc_data(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key) + ":")
      if isinstance(value, dict):
         pretty_print_enc_data(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def test():
    print("[main] Testing data storage (1)")
    data_storage = DataStorage('./test')
    test_patient = Patient("Test One", 22, "1234567890", ['AAA', 'BBB'])
    data_storage.createPatientFile(test_patient)
    test_patient.age = 23
    data_storage.updatePatientFile(test_patient)

    print("[main] Testing predicate encryption (1)")
    pe = PredicateEncryption(1) # 1 attribute
    user_id = 1
    print(f"[main] User ID is {user_id}")
    pk, sk = pe.authoritySetup()
    print(f"[main] Public key = {pk}")
    print(f"[main] Secret key = {sk}")

    K, attr_list = pe.keyGen(pk, sk, ['0'], user_id)
    print(f"[main] After key generation:\n\t Key = {K}\n\t Attributes list = {attr_list}")

    message = 111122223333 # I don't know how to create a message inside the group G and encode/decode it!!!

    encripted_data = pe.encrypt(message, "0", pk) # policies limited to 'or' and 'and'
    # pretty_print_enc_data(encripted_data)
    print(f"[main] Ciphertext: {encripted_data['c0']}")

    pe.decrypt(encripted_data, K, ['1'], user_id) # Wrong attr list
    plaintext = pe.decrypt(encripted_data, K, attr_list, user_id) # Corret attr list

    print(f"[main] Plaintext after decryption: {plaintext}")

if __name__ == "__main__":
    main()