"""Exercise the real LM Studio adapter against reachable and unreachable loopback."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.domain import ProviderHealthStatus


class _LoopbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        if self.path != "/api/v1/models":
            self.send_error(404)
            return
        payload = {
            "models": [
                {
                    "key": "acceptance/test-model",
                    "display_name": "Acceptance Test Model",
                    "type": "llm",
                    "max_context_length": 32768,
                    "quantization": {"name": "Q4_K_M"},
                    "loaded_instances": [
                        {
                            "id": "acceptance/test-model",
                            "config": {"context_length": 8192},
                        }
                    ],
                    "capabilities": {
                        "vision": False,
                        "trained_for_tool_use": True,
                    },
                }
            ]
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("This diagnostic is valid only on native Windows.")

    server = ThreadingHTTPServer(("127.0.0.1", 0), _LoopbackHandler)
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, name="lm-studio-loopback", daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    try:
        reachable = LMStudioProvider(base_url, timeout_seconds=1.0)
        health = reachable.health()
        models = reachable.discover_models()
        if health.status is not ProviderHealthStatus.READY:
            raise RuntimeError(f"Reachable loopback provider reported {health.status}.")
        if len(models) != 1 or models[0].backend_model_id != "acceptance/test-model":
            raise RuntimeError("Reachable loopback provider returned the wrong model contract.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    unreachable = LMStudioProvider(base_url, timeout_seconds=0.5)
    unavailable_health = unreachable.health()
    if unavailable_health.status is not ProviderHealthStatus.UNAVAILABLE:
        raise RuntimeError(
            "Closed loopback provider did not report the honest unavailable state."
        )

    print(
        json.dumps(
            {
                "candidate_sha": os.environ.get("CANDIDATE_SHA", ""),
                "reachable": "PASS",
                "unreachable": "PASS",
                "model_id": models[0].backend_model_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
