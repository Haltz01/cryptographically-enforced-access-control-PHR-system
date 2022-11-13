from Patient import Patient
from DataStorage import DataStorage
from PredicateEncryption import PredicateEncryption

# Temporary import...
from charm.toolbox.pairinggroup import ZR, GT

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
    print("\n[main] Testing data storage (1)")
    data_storage = DataStorage('./test')
    test_patient = Patient("Test One", 22, "1234567890", ['AAA', 'BBB'])
    data_storage.createPatientFile(test_patient)
    test_patient.age = 23
    data_storage.updatePatientFile(test_patient)

    print("\n[main] Testing predicate encryption (1)")
    pe = PredicateEncryption(2) # 2 attributes
    user_id = pe.group.random(ZR)
    #print(f"[main] User ID is {user_id}")
    pk, sk = pe.authoritySetup()
    #print(f"[main] Public key = {pk}")
    #print(f"[main] Secret key = {sk}")

    attr_list = ['0']
    print(f"\n[main] Calling keyGen()")
    K = pe.keyGen(sk, attr_list, user_id)

    message = pe.group.random(GT) # I don't know how to create a message inside the group and encode/decode it without using this auxiliart function

    print(f"\n[main] Calling encrypt()")
    encripted_data = pe.encrypt(message, "0", pk) # policies limited to 'or' and 'and'
    # pretty_print_enc_data(encripted_data)
    
    print(f"\n[main] Calling encrypt() with wrong attributes' list")
    pe.decrypt(encripted_data, K, ['1'], user_id) # Wrong attr list

    print(f"\n[main] Calling encrypt() with correct attributes' list")
    pe.decrypt(encripted_data, K, attr_list, user_id) # Corret attr list

if __name__ == "__main__":
    main()