class MedicalFacility:
    def __init__(self, name: str, addr: str, facilityId: str, patientIds: list):
        # TODO: Block overwritting name and id, otherwise it will be impossible to find the .txt files
        self.name = name.strip()
        self.addr = addr
        self.facilityId = facilityId.strip()
        self.patientIds = [a.strip() for a in patientIds] # Patients in MedicalFacility

    def __str__(self):
        return (f"MedicalFacility object\nName: {self.name}\nPatientIds: {self.patientIds}\nFacilityID document: {self.facilityId}\nAddr: {self.addr}")

    def prettyPrintForFile(self) -> str:
        output = "Name: " + self.name + "\n"
        output += "Addr: " + str(self.addr) + "\n"
        output += "FalicityID: " + self.facilityId + "\n"
        output += "PatientIds: "
        for pid in self.patientIds:
            output += pid + ","
        output = output[:-1]

        return output