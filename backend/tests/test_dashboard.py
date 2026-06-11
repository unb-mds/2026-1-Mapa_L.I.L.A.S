import json
import threading
import http.server
import socketserver
import time
import pytest
from pathlib import Path

import socket
def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

PORT = get_free_port()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent.parent.parent / "docs" / "ingestion"), **kwargs)

def start_server(port):
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

@pytest.fixture(scope="module", autouse=True)
def server():
    # Setup docs/ingestion directory and dummy json
    docs_dir = Path(__file__).parent.parent.parent / "docs" / "ingestion"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    dummy_history = {
        "generated_at": "2026-06-11T03:38:42Z",
        "runs": [
            {
                "mode": "incremental",
                "started_at": "2026-06-11T03:33:00Z",
                "finished_at": "2026-06-11T03:38:42Z",
                "duration_seconds": 342,
                "camara_count": 12,
                "senado_count": 7,
                "total_count": 19,
                "errors": [],
                "status": "success"
            }
        ]
    }
    with open(docs_dir / "ingestion-history.json", "w") as f:
        json.dump(dummy_history, f)
        
    # Start server in thread
    thread = threading.Thread(target=start_server, args=(PORT,), daemon=True)
    thread.start()
    time.sleep(1) # wait for server to start
    yield

def test_dashboard_renders_data(page):
    page.goto(f"http://localhost:{PORT}/index.html")
    
    # Wait for the data to load
    page.wait_for_selector("#dashboard", state="visible")
    
    # Check title
    assert "Ingestão" in page.title()
    
    # Check if total count is rendered (19)
    total_el = page.locator("#summary-total")
    assert total_el.inner_text() == "19"
    
    # Check if status is success
    status_el = page.locator("#summary-status")
    assert "Sucesso" in status_el.inner_text()
