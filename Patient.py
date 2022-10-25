class Patient:
    def __init__(self, name: str, age: int, id: str, allergies: list):
        # TODO: Block overwritting name and id, otherwise it will be impossible to find the .txt files
        self.name = name.strip()
        self.age = age
        self.id = id.strip()
        self.allergies = [a.strip() for a in allergies]

    def __str__(self):
        return (f"Patient object\nName: {self.name}\nAllergies: {self.allergies}\nID document: {self.id}\nAge: {self.age}")

    def prettyPrintForFile(self) -> str:
        output = "Name: " + self.name + "\n"
        output += "Age: " + str(self.age) + "\n"
        output += "ID: " + self.id + "\n"
        output += "Alergies: "
        for allergy in self.allergies:
            output += allergy + ","
        output = output[:-1]

        return output