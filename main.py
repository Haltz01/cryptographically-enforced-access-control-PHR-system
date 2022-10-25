from Patient import Patient
from DataStorage import DataStorage

def main():
    test()

def test():
    data_storage = DataStorage('./test')
    test_patient = Patient("Test One", 22, "1234567890", ['AAA', 'BBB'])
    data_storage.createPatientFile(test_patient)
    test_patient.age = 23
    data_storage.updatePatientFile(test_patient)

if __name__ == "__main__":
    main()