# Maybe we can use Charm here...
# https://jhuisi.github.io/charm/install_source.html
# Run with Python 3.7

from charm.toolbox.pairinggroup import PairingGroup, G1 # ZR, G2, GT, pair
from charm.toolbox.ABEnc import ABEnc # interface for ABE scheme
from charm.toolbox.msp import MSP
class PredicateEncryption(ABEnc):
    def __init__(self, verbose = True):
        self.globalSetup()
        self.util = MSP(self.group, verbose)

    def __str__(self):
        return (f"PredicateEncryption object")
    
    # def getHashGID()
    # Group oracle to retrieve hash for GIDs 
    # Hash function H : {0, 1}^* -> G that maps global identities GID to elements of G (random oracle)
    # Implemented in the Patient class

    def getGlobalParams(self):
        GP = {
            'group' : self.group,
            'group_order' : self.group_order,
            'generator' : self.g1
        }

        return GP

    # Creates the bilinear group G and also defines some global parameters, such as the group order and the generator g_1
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
        print("[PE] Global setup performed!")

    # def authoritySetup():
    # In a single authority model, the authority setup would happen here
    # # For a MA-PE, this setup happens in the the Patient class
    
    # def keyGen():
    # In a single authority model, the authority setup would happen here
    # # For a MA-PE, this setup happens in the the Patient class

    # The same applies for decrypt and encrypt functions. The participants of the system have direct access to these functions...
    # In the end, this central authority only has to perform the global setup and provide some global paramenters to all participants in the system

    """
    Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    """
    """
    Inverse of Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function
    """
