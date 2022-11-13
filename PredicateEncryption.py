# Maybe we can use Charm here...
# https://jhuisi.github.io/charm/install_source.html
# Run with Python 3.7

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.toolbox.ABEnc import ABEnc # interface for ABE scheme
from charm.toolbox.msp import MSP

class PredicateEncryption(ABEnc):
    def __init__(self, verbose = True):
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

    def getGlobalParams(self):
        GP = {
            'group' : self.group,
            'group_order' : self.group_order,
            'generator' : self.g1
        }

        return GP

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

    # def authoritySetup():
    # In a single authority model, the authority setup would happen here
    # # For a MA-PE, this setup happens in the the Patient class
    
    # def keyGen():
    # In a single authority model, the authority setup would happen here
    # # For a MA-PE, this setup happens in the the Patient class

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
