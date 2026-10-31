import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import URLError

from services.conway.automaton_engine import ConwayAutomatonEngine
from services.pqc.hybrid_pqc_verifier import HybridPQCVerifier
from services.quicknode.provider import QuickNodeProvider
from services.x402.bazaar_gateway import X402BazaarGateway


class SimulationTests(unittest.TestCase):
    def board(self, cells, size=8):
        grid = [[0] * size for _ in range(size)]
        for r, c in cells:
            grid[r][c] = 1
        return ConwayAutomatonEngine(size, size, grid)

    def test_still_life(self):
        engine = self.board({(2,2), (2,3), (3,2), (3,3)})
        old = engine.state_hash()
        self.assertEqual(engine.step(), old)
        self.assertEqual(engine.generation, 1)

    def test_blinker(self):
        engine = self.board({(3,2), (3,3), (3,4)})
        original = engine.state_hash()
        self.assertNotEqual(engine.step(), original)
        self.assertEqual(engine.step(), original)

    def test_glider_moves_after_four_steps(self):
        engine = self.board({(1,2), (2,3), (3,1), (3,2), (3,3)})
        for _ in range(4):
            engine.step()
        expected = self.board({(2,3), (3,4), (4,2), (4,3), (4,4)})
        self.assertEqual(engine.state_hash(), expected.state_hash())

    def test_toroidal_edges(self):
        engine = self.board({(1,0), (2,0), (3,0)}, size=5)
        engine.step()
        self.assertEqual(engine.grid[2], [1,1,0,0,1])

    def test_snapshot_is_detached_and_input_is_copied(self):
        grid = [[0]*3 for _ in range(3)]
        engine = ConwayAutomatonEngine(3,3,grid)
        grid[0][0] = 1
        snapshot = engine.snapshot()
        snapshot["grid"][1][1] = 1
        self.assertEqual(sum(map(sum,engine.grid)),0)

    def test_invalid_and_oversized_grids_rejected(self):
        for w,h in ((2,8), (257,8), (True,8), (8,0)):
            with self.subTest(w=w,h=h), self.assertRaises(ValueError):
                ConwayAutomatonEngine(w,h)
        with self.assertRaises(ValueError):
            ConwayAutomatonEngine(3,3,[[0]*3]*2)
        with self.assertRaises(ValueError):
            ConwayAutomatonEngine(3,3,[[2]*3]*3)


class VerificationBoundaryTests(unittest.TestCase):
    def test_forged_and_empty_payments_are_rejected(self):
        gateway = X402BazaarGateway()
        for proof in ("", "0"*64, None, '{"paid":true}'):
            self.assertFalse(gateway.verify_proof(proof,"unrelated-nonce")[0])
        self.assertEqual(gateway.create_402_challenge()["status"],503)

    def test_payment_configuration_is_preserved_and_price_checked(self):
        gateway = X402BazaarGateway("resource","42","recipient")
        self.assertEqual((gateway.resource_id,gateway.price,gateway.recipient),("resource","42","recipient"))
        for price in ("-1","0","1.5","Infinity"):
            with self.subTest(price=price), self.assertRaises(ValueError):
                X402BazaarGateway(price=price)

    def test_forged_long_signatures_and_wrong_keys_are_rejected(self):
        verifier = HybridPQCVerifier()
        self.assertFalse(verifier.verify_hybrid(b"a"*64,b"b"*1024,b"message",b"wrong-key"))
        self.assertFalse(verifier.verify_hybrid(None,None,None,None))
        self.assertEqual(verifier.status,"NOT_IMPLEMENTED")

    def test_missing_rpc_or_chain_identity_is_unhealthy(self):
        self.assertFalse(QuickNodeProvider(rpc_url="https://example.invalid").verify_health())
        self.assertFalse(QuickNodeProvider(rpc_url="file:///example",chain_id=1).verify_health())

    def test_wrong_chain_stale_head_and_transport_errors_are_unhealthy(self):
        provider = QuickNodeProvider(rpc_url="https://example.invalid",chain_id=1)
        with patch.object(provider,"_rpc",return_value="0x2"):
            self.assertFalse(provider.verify_health())
        with patch.object(provider,"_rpc",side_effect=["0x1",{"number":"0x1","timestamp":"0x1"}]):
            self.assertFalse(provider.verify_health())
        with patch.object(provider,"_rpc",side_effect=URLError("opaque transport failure")):
            self.assertFalse(provider.verify_health())

    def test_malformed_rpc_results_are_unhealthy(self):
        provider = QuickNodeProvider(rpc_url="https://example.invalid",chain_id=1)
        for block in (None, {}, {"number":"oops","timestamp":"0x1"}):
            with self.subTest(block=block), patch.object(provider,"_rpc",side_effect=["0x1",block]):
                self.assertFalse(provider.verify_health())

    def test_real_local_http_probe_checks_chain_and_fresh_head(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                result = "0x2105" if request["method"]=="eth_chainId" else {"number":"0x1","timestamp":hex(int(time.time()))}
                body = json.dumps({"jsonrpc":"2.0","id":request["id"],"result":result}).encode()
                self.send_response(200); self.send_header("Content-Type","application/json")
                self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
            def log_message(self,*args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            provider = QuickNodeProvider(rpc_url="http://127.0.0.1:"+str(server.server_port),chain_id=8453)
            self.assertTrue(provider.verify_health())
            provider.chain_id = 1
            self.assertFalse(provider.verify_health())
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)


if __name__=="__main__":
    unittest.main()
