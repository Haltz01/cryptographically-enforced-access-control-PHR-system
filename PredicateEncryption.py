# Maybe we can use Charm here...
# https://jhuisi.github.io/charm/install_source.html
# Run with Python 3.7

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.toolbox.ABEnc import ABEnc # interface for ABE scheme
from charm.toolbox.msp import MSP
import math

class PredicateEncryption(ABEnc):
    def __init__(self, qty_attributes, verbose = True):
        self.qty_attributes = qty_attributes
        self.globalSetup()
        self.util = MSP(self.group, verbose)

    def __str__(self):
        return (f"PredicateEncryption object")

    def globalSetup(self) -> dict:
        # A bilinear group G of order N = p_1 * p_2 * p_3 is chosen
        group_order = 512
        group = PairingGroup('SS512') # SS512 = symmetric curve with a 512-bit base field
        g1 = group.random(G1) # Generator g_1
        g2 = group.random(G2) # Generator g_2

        # The global public parameters (GP) are: group order + generator g_1 of G_{p_1}
        self.group_order = group_order 
        self.g1 = g1
        self.g2 = g2
        self.group = group
        
        #The description of a hash function H : {0, 1}^{\star} \rightarrow G that maps global identities GID to elements of G should be published -- H is modeled here as a random oracle.
    
    # Generates public key and secret key for an authority given all the attributes from that authority
    # For all, all authorities have the same number of attributes
    # TODO: add parameter to indicate number of attributes for each authority
    def authoritySetup(self):
        secret_key = []
        public_key = []

        for i in range(self.qty_attributes): # for each attribute in the universe of attributes
            print(f"[PE] Generating PK/SK pair for attribute index {i}")
            # we choose two random exponents alpha_i and y_i
            alpha_i = self.group.random(ZR)
            y_i = self.group.random(ZR)
            print(f"[PE] alpha_i = {alpha_i}")
            print(f"[PE] y_i = {y_i}")

            e_gg_alpha_i = pair(self.g1, self.g1) ** alpha_i # e(g_1, g_1)^{\alpha_i}
            g1_y_i = self.g1 ** y_i # g^{y_i}
            print(f"[PE] e_gg_alpha_i = {e_gg_alpha_i}")
            print(f"[PE] g1_y_i = {g1_y_i}")

            public_key.append((e_gg_alpha_i, g1_y_i)) # PK = {e(g_1, g_1)^{\alpha_i} , g^{y_i}_1 \forall i}
            secret_key.append((alpha_i, y_i)) # SK = {\alpha_i, y_i \forall i}

        return public_key, secret_key
        
    def keyGen(self, public_key, secret_key, attr_list, user_id):
        # To create a key for GID for attribute 'i' belonging to an authority, the authority computes K_{i,GID} = g^{\alpha_i}_1 * h_GID^{y_i}
        
        # H is the hashing function (oracle) that maps global identities GID to elements of G.
        # TODO: implement this hasing function ^^^^
        h_GID = self.g1 ** user_id

        K = {}
        for attr in attr_list:
            attr = int(attr)

            g1_alpha_i = self.g1 ** secret_key[attr][0] # g^{\alpha_i}_1

            K[attr] = g1_alpha_i * (h_GID ** secret_key[attr][1])# K_{i,GID} = g^{\alpha_i}_1 * h_GID^{y_i}

        return K, attr_list

    def encodeMessage(self, message):
        gt = pair(self.g1, self.g1)
        return gt * message

    def decodeMessage(self, encoded_msg):
        gt = pair(self.g1, self.g1)
        return encoded_msg / gt
    
    """
    Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    """
    """
    Inverse of Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function
    """

    def encrypt(self, message, policy_str, public_key):
        # Takes in a message M, an 'n' X 'l' access matrix A with 'p' mapping its rows to attributes, the global parameters GP, and the public keys PK of the relevant authorities

        message = self.encodeMessage(message)
        print(f"[PE] Encoded message: ", message)

        policy = self.util.createPolicy(policy_str) # converts a Boolean formula represented as a string into a policy represented like a tree
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

                # For each row A_x of A, choose a random r_x in Z_N
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

        return { 'policy': policy, 'c0': c0, 'C': C }
    
    def decrypt(self, ciphertext, K, attr_list, user_id):
        # check if the attr_list passed to the function satisfy our policy tree
        nodes = self.util.prune(ciphertext['policy'], attr_list) 
        if not nodes:
            print ("[PE] Policy not satisfied while trying to decrypt ciphertext.")
            return None

        prod_x = 1

        for node in nodes: # for each attribute...
            attr = node.getAttributeAndIndex() # get attribute name
            attr_stripped = self.util.strip_index(attr) # Remove the index from an attribute (i.e., x_y -> x)

            c1 = ciphertext['C'][attr]['c1']
            c2 = ciphertext['C'][attr]['c2']
            c3 = ciphertext['C'][attr]['c3']
            # print("c1 = ", c1)
            # print("c2 = ", c2)
            # print("c3 = ", c3)

            h_GID = self.g1 ** user_id

            # C_{1,x} * e(h_GID, C_{3,x}) / e(K_{\rho(x),GID}, C_{2,x}) = e(g_1, g_1)^{\lambda_x} * e(h_GID, g_1)^{w_x}
            aux = c1 * pair(h_GID, c3) / pair(K[int(attr_stripped)], c2)

            # [multiplicand] \prod_x (aux) = e(g_1, g_1)^s
            prod_x *= aux

        message = ciphertext['c0'] / prod_x
        print(f"[PE] Encoded message after decryption: ", message)

        return self.decodeMessage(message)
