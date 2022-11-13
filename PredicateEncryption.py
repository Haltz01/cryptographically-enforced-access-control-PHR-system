# Maybe we can use Charm here...
# https://jhuisi.github.io/charm/install_source.html
# Run with Python 3.7

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.toolbox.ABEnc import ABEnc # interface for ABE scheme
from charm.toolbox.msp import MSP

class PredicateEncryption(ABEnc):
    def __init__(self, qty_attributes, verbose = True):
        self.qty_attributes = qty_attributes
        self.globalSetup()
        self.util = MSP(self.group, verbose)

    def __str__(self):
        return (f"PredicateEncryption object")
    
    # Group oracle to retrieve hash for GIDs 
    # Hash function H : {0, 1}^* -> G that maps global identities GID to elements of G (random oracle)
    def getHashGID(self, GID, verbose=False):
        h_GID = self.group.hash(GID, type=G1)
        if verbose:
            print(f"[PE] User {GID} has GID hash (in G1) = {h_GID}")

        return h_GID

    # Creates the nilinear group G and also defines some global parameters, such as the group order and the generator g_1
    def globalSetup(self) -> dict:
        # A bilinear group G of order N = p_1 * p_2 * p_3 is chosen
        # TODO: convert prime order group to group G of order N!
        # For now, we have a bilinear group G of prime order
        group = PairingGroup('SS512') # SS512 = symmetric eliptic curve with a 512-bit base field (has the bilinear mapping feature needed)
        g1 = group.random(G1) # Generator g_1

        # The global public parameters (GP) are: group order + generator g_1 of G
        self.group_order = group.order()
        self.g1 = g1
        self.group = group
    
    # Generates public key and secret key for an authority given all the attributes from that authority
    # For all, all authorities have the same number of attributes
    # TODO: add parameter to indicate number of attributes for each authority
    def authoritySetup(self):
        print()

        secret_key = []
        public_key = []

        print(f"[PE - authoritySetup] Generating PK/SK pair for each attribute in the scheme")
        for i in range(self.qty_attributes): # for each attribute in the universe of attributes
            # we choose two random exponents alpha_i and y_i
            alpha_i = self.group.random(ZR)
            y_i = self.group.random(ZR)
            # print(f"[PE] alpha_i = {alpha_i}")
            # print(f"[PE] y_i = {y_i}")

            e_gg_alpha_i = pair(self.g1, self.g1) ** alpha_i # e(g_1, g_1)^{\alpha_i}
            g1_y_i = self.g1 ** y_i # g^{y_i}
            # print(f"[PE] e_gg_alpha_i = {e_gg_alpha_i}")
            # print(f"[PE] g1_y_i = {g1_y_i}")

            public_key.append((e_gg_alpha_i, g1_y_i)) # PK = {e(g_1, g_1)^{\alpha_i} , g^{y_i}_1 \forall i}
            secret_key.append((alpha_i, y_i)) # SK = {\alpha_i, y_i \forall i}
        print(f"[PE - authoritySetup] All {self.qty_attributes} PK/SK pairs were created!")

        return public_key, secret_key
    
    # Creates key with a certain list of attributes that can be used to read encripted messages with a policy that
    # matches the list of attributes in the key
    # This function as called by any authority (e.g. patient owning a secret key)
    def keyGen(self, secret_key, attr_list, GID):
        print()
        # To create a key for GID for attribute 'i' belonging to an authority, the authority computes K_{i,GID} = g^{\alpha_i}_1 * h_GID^{y_i}
        print(f"[PE - keyGen] Generating key K for the following list of attributes: {attr_list}")
        print(f"\t- Request made by user with GID = {GID}")
        
        h_GID = self.getHashGID(GID)

        K = {}
        for attr in attr_list:
            attr = int(attr) # we consider that all attributes are going to be integers

            g1_alpha_i = self.g1 ** secret_key[attr][0] # g_{1}^{\alpha_i}

            K[attr] = g1_alpha_i * (h_GID ** secret_key[attr][1]) # K_{i,GID} = gg_{1}^{\alpha_i}* h_GID^{y_i}
        print(f"[PE - keyGen] Key K created!\n\t- First entry in K: {K[int(attr_list[0])]}")

        return K

    """
    Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    """
    """
    Inverse of Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function
    """
    
    def encrypt(self, message, policy_str, public_key):
        print()

        # Takes in a message M, an 'n' X 'l' access matrix A with 'p' mapping its rows to attributes, the global parameters GP, and the public keys PK of the relevant authorities

        print(f"[PE - encrypt] Message (before encryption): {message}")

        policy = self.util.createPolicy(policy_str) # converts a Boolean formula represented as a string into a policy represented like a tree
        print(f"[PE - encrypt] The following policy will be applied to the encryption: {policy}")
        policy_msp = self.util.convert_policy_to_msp(policy) # converts a policy into a monotone span program (MSP) represented by a dictionary with (attribute, row) pairs

        num_cols = self.util.len_longest_row
        
        # Choose a random 's' in Z_N and a random vector 'v' in Z_{N}^{l} with 's' as its first entry
        v = []
        for i in range(num_cols):
            rand = self.group.random(ZR) # random values
            v.append(rand)
        s = v[0] # first entry = 's' (shared secret)

        # Choose a random vector w \in Z^{l}_N with 0 as its first entry
        w = []
        for i in range(num_cols):
            rand = self.group.random(ZR) # random values
            w.append(rand)
        w[0] = 0 # first entry is zero

        # C_0 = M * e(g_1, g_1)^s
        # C_0 is the encripted message
        c0 = message * (pair(self.g1, self.g1) ** s)

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
                r_x = self.group.random(ZR)

                # C_{1,x} = e(g1, g1)^{\lambda_x} * e(g_1, g_1)^{\alpha_{p(x)} * r_x}
                c1_x = public_key[int(attr_stripped)][0] ** (r_x) # e(g_1, g_1)^{\alpha_{p(x)} * r_x}
                c1_x *= pair(self.g1, self.g1) ** lambda_x # e(g1, g1)^{\lambda_x}

                # C_{2,x} = g_{1}^{r_x}
                c2_x = self.g1 ** r_x

                # C_{3,x} = g_{1}^{y_{p(x)} * r_x} * g^{w_x}_1
                c3_x = public_key[int(attr_stripped)][1] ** r_x # g_{1}^{y_{p(x)} * r_x}
                c3_x *= self.g1 ** w_x # g_{1}^{w_x}

                C[attr] = {
                    'c1': c1_x,
                    'c2': c2_x,
                    'c3': c3_x
                }

        
        print(f"[PE - encrypt] Encripted message c_0 = {c0}")

        return { 'policy': policy, 'c0': c0, 'C': C }
    
    def decrypt(self, ciphertext_data, K, attr_list, user_id):
        print()

        print(f"[PE - decrypt] Request for decription made by user with GID {user_id}")
        print(f"\t- Ciphertext is {ciphertext_data['c0']}")
        print(f"\t- Policy is {ciphertext_data['policy']}")
        print(f"\t- User says he/she has attributes {attr_list}")

        # check if the attr_list passed to the function satisfy our policy tree
        nodes = self.util.prune(ciphertext_data['policy'], attr_list) 
        if not nodes:
            print ("[PE - decrypt] Policy not satisfied while trying to decrypt ciphertext.")
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

            # TODO: change this, so that users pass the hash to the function
            # The way we're doing now allows easy "impersonation"
            h_GID = self.getHashGID(user_id)

            # Calculate C_{1,x} * e(h_GID, C_{3,x}) / e(K_{\rho(x),GID}, C_{2,x})
            # which is equal to e(g_1, g_1)^{\lambda_x} * e(h_GID, g_1)^{w_x}
            aux = c1 * pair(h_GID, c3) / pair(K[int(attr_stripped)], c2)

            # [multiplicand] \prod_x (aux) = e(g_1, g_1)^s
            prod_x *= aux
            
            # The decryptor then chooses constants c_x ∈ Z_p such that \sum cx * Ax = (1, 0, . . . , 0) and computes:
            # TODO: missing \prod_x (aux)^{c_x}, but it looks like it's not needed...

        message = ciphertext_data['c0'] / prod_x
        print(f"[PE - decrypt] Message after decryption: {message} ")

        return message
