"""No reviewed cryptographic backend is integrated. Never accept length-only signatures."""


class HybridPQCVerifier:
    status = "NOT_IMPLEMENTED"

    def verify_hybrid(self, classical, pqc, msg, pk):
        # A real positive result requires classical AND PQC verification over the
        # exact message/key and published-vector tests, not signature length.
        return False
