"""Payment access stays closed until real x402 verification AND settlement are integrated."""


class X402BazaarGateway:
    status = "PAYMENT_BACKEND_NOT_CONFIGURED"

    def __init__(self, resource_id="res_un_01", price="1000", recipient=None):
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("A resource identifier is required")
        if not isinstance(price, str) or not price.isascii() or not price.isdecimal() or int(price) <= 0:
            raise ValueError("Price must be a positive integer base-unit string")
        self.resource_id, self.price, self.recipient = resource_id, price, recipient

    def create_402_challenge(self):
        # A fabricated challenge must not be represented as protocol compliance.
        return {"status": 503, "code": self.status}

    def verify_proof(self, proof_str, nonce):
        return False, self.status
