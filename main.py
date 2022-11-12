from Patient import *
from Server import *
from PredicateEncryption import PredicateEncryption

# Temporary import...
from charm.toolbox.pairinggroup import ZR, GT

def main():
    test()
    test2()
    patientSendToServerTest()

def pretty_print_enc_data(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key) + ":")
      if isinstance(value, dict):
         pretty_print_enc_data(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def test():
    print("[main] Testing data storage (1)")
    test_patient = Patient("Test One", 22, "1234567890", ['AAA', 'BBB'])
    test_patient.dataStorage.createFile(test_patient.id, test_patient.name)
    test_patient.age = 23
    test_patient.dataStorage.updateFile(test_patient.id, test_patient.name, test_patient.prettyPrintForFile())

    print("[main] Testing predicate encryption (1)")
    pe = PredicateEncryption(2) # 2 attributes
    user_id = pe.group.random(ZR)
    #print(f"[main] User ID is {user_id}")
    pk, sk = pe.authoritySetup()
    #print(f"[main] Public key = {pk}")
    #print(f"[main] Secret key = {sk}")

    attr_list = ['0']
    print(f"[main] Calling keyGen()")
    K = pe.keyGen(sk, attr_list, user_id)

    message = pe.group.random(GT) # I don't know how to create a message inside the group and encode/decode it without using this auxiliart function

    encripted_data = pe.encrypt(message, "0", pk) # policies limited to 'or' and 'and'
    # pretty_print_enc_data(encripted_data)

    pe.decrypt(encripted_data, K, ['1'], user_id) # Wrong attr list
    pe.decrypt(encripted_data, K, attr_list, user_id) # Corret attr list

def test2():
    print("[main] Setup")
    patient1 = Patient("Test One", 22, "1", ['AAA', 'BBB'])
    patient2 = Patient("Test Two", 23, "2", ['AAA', 'BBB'])
    insurance = Insurance("Test Three", 25, "2")
    doctor = Doctor("Test One", 42, "1")
    employer = Employer("Test Two", 23, "3")
    hospital = Hospital("1")
    club = HealthClub("1")

    insurance.getReadAccess(patient1, 0)
    doctor.getReadAccess(patient2, 1)
    employer.getReadAccess(patient1, 0)
    employer.getReadAccess(patient2, 0)

    hospital.getWriteAccess(patient1, 0)
    club.getWriteAccess(patient2, 0)

    print("[main] Testing read/write")

def patientSendToServerTest():
    print("[main] Testing data storage (1)")
    test_patient = Patient("Test One", 22, "1234567890", ['AAA', 'BBB'])
    test_patient.dataStorage.createFile(test_patient.id, test_patient.name)
    test_patient.age = 23
    test_patient.dataStorage.updateFile(test_patient.id, test_patient.name, test_patient.prettyPrintForFile())

    server = Server()

    test_patient.sendToServer(server.patientQueue, test_patient.prettyPrintForFile())
    server.recvPatientData()

if __name__ == "__main__":
    main()