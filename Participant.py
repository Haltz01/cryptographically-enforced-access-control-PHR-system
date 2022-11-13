from charm.toolbox.pairinggroup import ZR, pair
from charm.toolbox.msp import MSP
from hashlib import sha256

class Participant:
    def __init__(self, global_params):
        self.GID = global_params['group'].random(ZR)
        self.util = MSP(global_params['group'])
        self.global_params = global_params

        self.patient_data = {} # Third Party and Medical Facility use this
        self.patient_hashed_GIDs = [] # Third Party and Medical Facility use this
    
    def encrypt(self, message, policy_str, public_key):
        # Takes in a message M, an 'n' X 'l' access matrix A with 'p' mapping its rows to attributes, the global parameters GP, and the public keys PK of the relevant authorities

        group = self.global_params['group']
        g1 = self.global_params['generator']

        policy = self.util.createPolicy(policy_str) # converts a Boolean formula represented as a string into a policy represented like a tree
        policy_msp = self.util.convert_policy_to_msp(policy) # converts a policy into a monotone span program (MSP) represented by a dictionary with (attribute, row) pairs

        num_cols = self.util.len_longest_row
        
        # Choose a random 's' in Z_N and a random vector 'v' in Z_{N}^{l} with 's' as its first entry
        v = []
        for i in range(num_cols):
            rand = group.random(ZR) # random values
            v.append(rand)
        s = v[0] # first entry = 's' (shared secret)

        # Choose a random vector w \in Z^{l}_N with 0 as its first entry
        w = []
        for i in range(num_cols):
            rand = group.random(ZR) # random values
            w.append(rand)
        w[0] = 0 # first entry is zero

        # C_0 = M * e(g_1, g_1)^s
        # C_0 is the encripted message
        c0 = message * (pair(g1, g1) ** s)

        C = {}
        for attr, row in policy_msp.items():
            cols = len(row)
            lambda_x = 0 # lambda_x = A_{x} * v, where A_x is row x of A
            w_x = 0 # w_x = A_{x} * w, where A_x is row x of A
            
            for i in range(cols):  
                lambda_x += row[i] * v[i]
                w_x += row[i] * w[i]
            
                attr_stripped = self.util.strip_index(attr) # Remove the index from an attribute (i.e., x_y -> x)

                # For each row A_x of A, we choose a random r_x in Z_N
                r_x = group.random(ZR)

                # C_{1,x} = e(g1, g1)^{\lambda_x} * e(g_1, g_1)^{\alpha_{p(x)} * r_x}
                c1_x = public_key[int(attr_stripped)][0] ** (r_x) # e(g_1, g_1)^{\alpha_{p(x)} * r_x}
                c1_x *= pair(g1, g1) ** lambda_x # e(g1, g1)^{\lambda_x}

                # C_{2,x} = g_{1}^{r_x}
                c2_x = g1 ** r_x

                # C_{3,x} = g_{1}^{y_{p(x)} * r_x} * g^{w_x}_1
                c3_x = public_key[int(attr_stripped)][1] ** r_x # g_{1}^{y_{p(x)} * r_x}
                c3_x *= g1 ** w_x # g_{1}^{w_x}

                C[attr] = {
                    'c1': c1_x,
                    'c2': c2_x,
                    'c3': c3_x
                }
        
        print(f"[Participant] Encryption done")
        print(f"\t-> Original message: {str(message)[:20]}...")
        print(f"\t-> Policy used: {policy_str}")
        print(f"\t-> Encripted message: {str(c0)[:20]}...")

        return { 'policy_str': policy_str, 'c0': c0, 'C': C }

    def decrypt(self, ciphertext_data, K, attr_list, h_GID):

        # check if the attr_list passed to the function satisfy our policy tree
        policy = self.util.createPolicy(ciphertext_data['policy_str'])
        nodes = self.util.prune(policy, attr_list) 
        if not nodes:
            print ("[Participant] Policy not satisfied while trying to decrypt ciphertext")
            return None

        prod_x = 1

        for node in nodes: # for each attribute...
            attr = node.getAttributeAndIndex() # get attribute name
            attr_stripped = self.util.strip_index(attr) # Remove the index from an attribute (i.e., x_y -> x)

            c1 = ciphertext_data['C'][attr]['c1']
            c2 = ciphertext_data['C'][attr]['c2']
            c3 = ciphertext_data['C'][attr]['c3']
            # print("c1 = ", c1)
            # print("c2 = ", c2)
            # print("c3 = ", c3)

            # Calculate C_{1,x} * e(h_GID, C_{3,x}) / e(K_{\rho(x),GID}, C_{2,x})
            # which is equal to e(g_1, g_1)^{\lambda_x} * e(h_GID, g_1)^{w_x}
            aux = c1 * pair(h_GID, c3) / pair(K[int(attr_stripped)], c2)

            # [multiplicand] \prod_x (aux) = e(g_1, g_1)^s
            prod_x *= aux
            
            # The decryptor then chooses constants c_x ∈ Z_p such that \sum cx * Ax = (1, 0, . . . , 0) and computes:
            # TODO: missing \prod_x (aux)^{c_x}, but it looks like it's not needed...

        message = ciphertext_data['c0'] / prod_x

        print(f"[Participant] Decryption done")
        print(f"\t-> Encripted message: {str(ciphertext_data['c0'])[:20]}...")
        print(f"\t-> Policy used: {ciphertext_data['policy_str']}")
        print(f"\t-> Decripted message: {str(message)[:20]}...")

        return message
    
    # Add to the mapping another user and its key to allow reading personal files
    def savePatientData(self, patient_K, patient_hash_GID, patient_attr_list):
        patient_filename = sha256(self.global_params['group'].serialize(patient_hash_GID)).hexdigest()

        self.patient_data[patient_hash_GID] = {
            'K' : patient_K,
            'filename' : patient_filename,
            'hashed_GID' : patient_hash_GID,
            'attr_list' : patient_attr_list
        }
        self.patient_hashed_GIDs.append(patient_hash_GID)

    def readPatientFile(self, data_storage, ciphertext_data, filename, K, attr_list, hashed_GID):
        encrypted_message = data_storage.readFile(filename)
        encrypted_message = self.global_params['group'].deserialize(encrypted_message)

        ciphertext_data['c0'] = encrypted_message
        
        decrypted_message = self.decrypt(ciphertext_data, K, attr_list, hashed_GID)
        
        return decrypted_message

    def writeToPatientFile(self, message, policy_str, data_storage, public_key, filename):
        enc_data = self.encrypt(message, policy_str, public_key)
        enc_message = enc_data['c0']
        msg_bytes = self.global_params['group'].serialize(enc_message)
        data_storage.updateFile(filename, msg_bytes)

        return enc_data