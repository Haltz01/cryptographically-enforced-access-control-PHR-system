from DataStorage import DataStorage
from queue import Queue
from Server import *

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair

class Participant:
    def __init__(self, global_params):
        self.GID = global_params['group'].random(ZR)

    def decrypt(self, ciphertext_data, K, attr_list, h_GID):
        print()

        print(f"[PE - decrypt] Request for decription made by user with hashed GID {h_GID}")
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
