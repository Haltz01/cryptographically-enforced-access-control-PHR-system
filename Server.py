from queue import Queue
from DataStorage import DataStorage
import os
class Server:
    def __init__(self) -> None:
        self.dataStorage = DataStorage('./Server') # Server only storage patient data
        self.patientQueue1 = Queue(10)
        #self.patientQueue2 = Queue(10)

    def recvPatientData(self): #receive encrypted data from patients
        while self.patientQueue1.empty() == False:
            msgRecord = self.patientQueue1.get_nowait()
            self.dataStorage.createFile(msgRecord.id, msgRecord.name)
            self.dataStorage.updateFile(msgRecord.id, msgRecord.name, msgRecord.inputStr)

    def sendPatientDataToMF(self, MFQueue:Queue):#send patient's encrypted data to the medical facility
        files= os.listdir('./Server')
        for file in files: 
            with open('./Server/'+file,'r') as f:
                MFQueue.put(f.read())
    
class MsgRecord:
    def __init__(self, id: int, name: str, inputStr: str) -> None:
        self.id = id
        self.name = name
        self.inputStr = inputStr