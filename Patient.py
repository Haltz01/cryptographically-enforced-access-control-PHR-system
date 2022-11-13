from Participant import Participant
from hashlib import sha256

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair

class Patient(Participant):
    def __init__(self, name, global_params, data_storage):
        super().__init__(global_params)
        self.name = name.strip()
        self.secret_key = ""
        self.public_key = ""
        self.qty_attributes = 0
        self.personal_record_filename = sha256(global_params['group'].serialize(self.getHashGID(self.GID))).hexdigest()
        data_storage.createFile(self.personal_record_filename)

    def __str__(self):
        return (f"Patient object\nName: {self.name}\nAllergies: {self.allergies}\nID document: {self.id}\nAge: {self.age}")
        
    def writeToRecord(self, enc_message, data_storage):
        msg_bytes = self.global_params['group'].serialize(enc_message)
        data_storage.updateFile(self.personal_record_filename, msg_bytes)

    def readFromRecord(self, data_storage, ciphertext_data):
        encrypted_message = data_storage.readFile(self.personal_record_filename)
        encrypted_message = self.global_params['group'].deserialize(encrypted_message)

        ciphertext_data['c0'] = encrypted_message
        
        all_attributes = []
        for i in range(0, self.qty_attributes): # creating a K that satisties all attributes from this authority
            all_attributes.append(str(i))
        
        K, attr_list = self.keyGen(all_attributes, self.global_params)
        encrypted_message = self.decrypt(ciphertext_data, K, all_attributes, self.getHashGID(self.GID))
        return encrypted_message
        
    # Group oracle to retrieve hash for GIDs 
    # Hash function H : {0, 1}^* -> G that maps global identities GID to elements of G (random oracle)
    def getHashGID(self, verbose=False):
        h_GID = self.global_params['group'].hash(self.GID, type=G1)
        if verbose:
            print(f"[PE] User {self.GID} has GID hash (in G1) = {h_GID}")

        return h_GID

    # Generates public key and secret key for an authority given all the attributes from that authority
    def authoritySetup(self, global_params, qty_attributes):
        # Save quantity of attributes this authority uses
        self.qty_attributes = int(qty_attributes)

        secret_key = []
        public_key = []

        group = global_params['group']
        g1 = global_params['generator']

        print(f"[Patient - authoritySetup] Generating PK/SK pair for each attribute in the scheme ({self.GID})")
        for i in range(qty_attributes): # for each attribute in the universe of attributes
            # we choose two random exponents alpha_i and y_i
            alpha_i = group.random(ZR)
            y_i = group.random(ZR)
            # print(f"[PE] alpha_i = {alpha_i}")
            # print(f"[PE] y_i = {y_i}")

            e_gg_alpha_i = pair(g1, g1) ** alpha_i # e(g_1, g_1)^{\alpha_i}
            g1_y_i = g1 ** y_i # g^{y_i}
            # print(f"[PE] e_gg_alpha_i = {e_gg_alpha_i}")
            # print(f"[PE] g1_y_i = {g1_y_i}")

            public_key.append((e_gg_alpha_i, g1_y_i)) # PK = {e(g_1, g_1)^{\alpha_i} , g^{y_i}_1 \forall i}
            secret_key.append((alpha_i, y_i)) # SK = {\alpha_i, y_i \forall i}
        print(f"[Patient - authoritySetup] All {qty_attributes} PK/SK pairs were created! ({self.GID})")

        self.secret_key = secret_key
        self.public_key = public_key
    
    # Creates key with a certain list of attributes that can be used to read encripted messages with a policy that matches the list of attributes in the key
    def keyGen(self, attr_list, global_params):
        # To create a key for GID for attribute 'i' belonging to an authority, the authority computes K_{i,GID} = g^{\alpha_i}_1 * h_GID^{y_i}
        print(f"[Patient - keyGen] Generating key K for the following list of attributes: {attr_list} ({self.GID})")
        h_GID = self.getHashGID()
        print(f"\t- User hashed GID = {h_GID}")

        g1 = global_params['generator']

        K = {}
        for attr in attr_list:
            attr = int(attr) # we consider that all attributes are going to be integers

            g1_alpha_i = g1 ** self.secret_key[attr][0] # g_{1}^{\alpha_i}

            K[attr] = g1_alpha_i * (h_GID ** self.secret_key[attr][1]) # K_{i,GID} = gg_{1}^{\alpha_i}* h_GID^{y_i}
        print(f"[Patient - keyGen] Key K created! ({self.GID})\n\t- First entry in K: {K[int(attr_list[0])]}")

        return K, attr_list

    def prettyPrintForFile(self) -> str:
        output = "Name: " + self.name + "\n"
        output += "Age: " + str(self.age) + "\n"
        output += "ID: " + self.id + "\n"
        output += "Alergies: "
        for allergy in self.allergies:
            output += allergy + ","
        output = output[:-1]

        return output

    # def sendToServer(self, serverQueue: Queue, inputStr: str): # inputStr could be the encode str
    #     patientMsgRecord = MsgRecord(self.id, self.name, inputStr)
    #     serverQueue.put(patientMsgRecord)
    #     return