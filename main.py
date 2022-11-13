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
    print("[main] Setup authorities (patients)")
    pe1 = PredicateEncryption(2)
    pe2 = PredicateEncryption(2)

    patient1 = Patient("Test One", 22, "1", ['AAA', 'BBB']) # This patient will have a doctor, an insurer and was treated by hospital
    patient2 = Patient("Test Two", 23, "2", ['AAA', 'BBB']) # This patient will have an employer and is member of sports club
    
    pk1, sk1 = pe1.authoritySetup()
    pk2, sk2 = pe2.authoritySetup()

    print("[main] Generatin keys for parties")
    userIDs1 = []
    userIDs2 = []
    for i in range(5):
        userIDs1.add(pe1.group.random(ZR))
        userIDs2.add(pe2.group.random(ZR))
    
    print("[main] Creating parties")
    insurance = Insurance("Test Three", 25, str(userIDs1.get(0)))
    doctor = Doctor("Test One", 42, str(userIDs1.get(1)))
    employer = Employer("Test Two", 23, str(userIDs2.get(0)))
    hospital = Hospital(str(userIDs1.get(2)))
    club = HealthClub(str(userIDs2.get(1)))

    attr_list = ['0','1']

    keys1 = []
    keys2 = []

    for i in range(5):
        K1 = pe1.keyGen(sk1, attr_list, userIDs1[i])
        K2 = pe2.keyGen(sk2, attr_list, userIDs2[i])
        keys1.append(K1)
        keys2.append(K2)

    print("[main] Distribute keys")

    insurance.getReadAccess(patient1, keys1[0])
    doctor.getReadAccess(patient2, keys1[1])
    employer.getReadAccess(patient1, keys2[0])

    hospital.getWriteAccess(patient1, keys1[2])
    club.getWriteAccess(patient2, keys2[1])

    print("[main] Generating encrypted messages")
    message1 = pe1.group.random(GT)
    message2 = pe2.group.random(GT)

    encripted_data1 = pe1.encrypt(message1, attr_list, pk1)
    encripted_data2 = pe2.encrypt(message2, attr_list, pk2)

    print("[main] Testing read/write")
    pe1.decrypt(encripted_data1, insurance.getReadAccess[patient1.id], attr_list, insurance.id) # Party with permissions 
    pe1.decrypt(encripted_data1, employer.getReadAccess[patient2.id], attr_list, employer.id) # Party without permissions
    pe2.decrypt(encripted_data2, employer.getReadAccess[patient2.id], attr_list, employer.id) # Party without permissions
    pe2.decrypt(encripted_data2, club.getWriteAccess[patient1.id], attr_list, club.id) # Party without permissions


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