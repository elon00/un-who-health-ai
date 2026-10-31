"""Read-only EVM RPC health probe. Other chain runtimes need separate adapters."""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class QuickNodeProvider:
    def __init__(self, network="mainnet", rpc_url=None, chain_id=None, timeout=5):
        self.network = network
        self.rpc_url = rpc_url or os.environ.get("QUICKNODE_RPC_URL")
        self.chain_id = chain_id
        if type(timeout) not in (int, float) or not 0 < timeout <= 15:
            raise ValueError("Timeout must be between zero and 15 seconds")
        self.timeout = timeout

    def _rpc(self, method, params):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        req = Request(self.rpc_url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with build_opener(NoRedirect()).open(req, timeout=self.timeout) as response:
            packet = json.load(response)
        if packet.get("jsonrpc") != "2.0" or packet.get("id") != 1 or "error" in packet or "result" not in packet:
            raise ValueError("RPC result unavailable")
        return packet["result"]

    def verify_health(self):
        try:
            if not self.rpc_url or type(self.chain_id) is not int or self.chain_id <= 0:
                return False
            url = urlparse(self.rpc_url)
            if (url.username or url.password or url.fragment or
                    not (url.scheme == "https" and url.hostname or
                         url.scheme == "http" and url.hostname in ("localhost", "127.0.0.1", "::1"))):
                return False
            if int(self._rpc("eth_chainId", []), 16) != self.chain_id:
                return False
            block = self._rpc("eth_getBlockByNumber", ["latest", False])
            if not isinstance(block, dict) or int(block["number"], 16) < 0:
                return False
            age = time.time() - int(block["timestamp"], 16)
            return -60 <= age <= 300
        except (HTTPError, URLError, OSError, ValueError, TypeError, KeyError, AttributeError):
            # No endpoint tokens or exception strings escape through health output.
            return False
