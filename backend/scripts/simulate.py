"""Simulate a customer: start a session, then pass/fail each challenge.

  python scripts/simulate.py
  python scripts/simulate.py --fail-second
  python scripts/simulate.py --video ~/photo.jpg
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"

SAMPLE = {
    "products": [
        {
            "id": "sku_headphones",
            "name": "AeroPods headphones",
            "reason": "left hinge cracked",
            "price_cents": 29900,
        },
        {
            "id": "sku_keyboard",
            "name": "KeyLine 75",
            "reason": "spacebar stuck",
            "price_cents": 14900,
        },
    ]
}


def pretty(data: dict) -> None:
    action = data.get("action")
    last = data.get("last") or {}
    current = data.get("current")
    print(f"\naction={action}  last.challenge={last.get('challenge')}  last.product={last.get('product')}")
    if last.get("reason"):
        print(f"  reason: {last['reason']}")
    if current:
        p, c = current["product"], current["challenge"]
        print(f"  now: {p['name']} ({p['index']}/{p['total']}) · challenge {c['index']}/{c['total']}")
        print(f"  → {c['instruction']}")
    if data.get("terminal"):
        pay = data["terminal"]["payment"]
        print(f"  PAYMENT {pay['status']}: {pay['message']}")
        for item in data["terminal"]["products"]:
            print(f"    - {item['name']}: {'refund' if item['refunded'] else 'return item'}")


def request(url: str, *, method: str = "GET", json_body: dict | None = None, form: dict | None = None, file: tuple[str, bytes] | None = None) -> dict:
    headers: dict[str, str] = {}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None or file is not None:
        boundary = uuid.uuid4().hex
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        chunks: list[bytes] = []
        for key, value in (form or {}).items():
            chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
        if file:
            name, blob = file
            chunks.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{name}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode()
            )
            chunks.append(blob)
            chunks.append(b"\r\n")
        chunks.append(f"--{boundary}--\r\n".encode())
        data = b"".join(chunks)
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=60) as res:
            return json.loads(res.read().decode())
    except HTTPError as err:
        sys.exit(err.read().decode())
    except URLError as err:
        sys.exit(f"backend not reachable at {url}: {err.reason}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE)
    parser.add_argument("--fail-second", action="store_true", help="demo-fail the 2nd challenge")
    parser.add_argument("--video", type=Path, help="real image/video file for the OpenAI judge")
    args = parser.parse_args()

    request(f"{args.base}/health")
    started = request(f"{args.base}/api/sessions", method="POST", json_body=SAMPLE)
    print("session", started["session_id"])
    pretty(started)

    step = 0
    session_id = started["session_id"]
    video_path: Path | None = args.video
    while True:
        step += 1
        demo = "fail" if args.fail_second and step == 2 else "pass"
        url = f"{args.base}/api/sessions/{session_id}/recordings"
        if video_path and video_path.exists():
            print(f"\nuploading {video_path.name} (OpenAI judge) …")
            body = request(url, method="POST", file=(video_path.name, video_path.read_bytes()))
            video_path = None
        else:
            print(f"\nsending demo_result={demo} …")
            body = request(url, method="POST", form={"demo_result": demo})
        pretty(body)
        if body["action"] == "done":
            break


if __name__ == "__main__":
    main()
