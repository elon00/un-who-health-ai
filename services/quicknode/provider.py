# QuickNode Multichain RPC Provider
class QuickNodeProvider:
    def __init__(self, network="mainnet"):
        self.network = network
    def verify_health(self):
        return True
