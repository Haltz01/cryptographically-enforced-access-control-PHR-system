from queue import Queue
from DataStorage import DataStorage
class Server:
    def __init__(self) -> None:
        self.dataStorage = DataStorage('./Server') # Server only storage patient data
        self.patientQueue = Queue(10)

    def recvPatientData(self):
        while self.patientQueue.empty() != False:
            msgRecord = self.patientQueue.get_nowait()
            self.dataStorage.createFile(msgRecord.id, msgRecord.name)
            self.dataStorage.updateFile(msgRecord.id, msgRecord.name, msgRecord.inputStr)
    
class MsgRecord:
    def __init__(self, id: int, name: str, inputStr: str) -> None:
        self.id = id
        self.name = name
        self.inputStr = inputStr