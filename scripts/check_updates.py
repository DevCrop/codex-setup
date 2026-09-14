"""Read-only source monitor; reports candidates without changing managed policy."""
import argparse
import concurrent.futures
import difflib
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import urllib.request
from datetime import datetime, timezone

from setup import ROOT, Deployment, read_json, save_json


class Body(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ignore = 0
        self.parts = []
        self.primary = []
        self.primary_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("main", "article"):
            self.primary_depth += 1
        if tag in ("script", "style", "nav", "footer", "header"):
            self.ignore += 1

    def handle_endtag(self, tag):
        if tag in ("main", "article"):
            self.primary_depth = max(0, self.primary_depth - 1)
        if tag in ("script", "style", "nav", "footer", "header"):
            self.ignore = max(0, self.ignore - 1)

    def handle_data(self, text):
        if not self.ignore:
            self.parts.append(text)
            if self.primary_depth:
                self.primary.append(text)


def fetch(item):
    url = item["url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TRACE-Setup-source-monitor/1"})
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read(4_000_001)
            if len(data) > 4_000_000:
                raise ValueError("Response exceeds monitor limit")
            text = data.decode("utf-8")
            if url.startswith("https://api.github.com/"):
                commits = json.loads(text)
                text = json.dumps({"sha": commits[0]["sha"], "message": commits[0]["commit"]["message"]}, sort_keys=True)
            if "text/html" in response.headers.get("Content-Type", ""):
                body = Body()
                body.feed(text)
                text = " ".join(body.primary or body.parts)
            normalized = re.sub(r"\s+", " ", text).strip()
            if len(normalized) < 50:
                raise ValueError("Empty or unexpectedly short body")
            if any(marker in normalized.lower() for marker in ("verify you are human", "just a moment...", "access denied")):
                raise ValueError("Access challenge instead of document")
            return {"id": item["id"], "url": url, "status": "fetched",
                    "sha256": hashlib.sha256(normalized.encode()).hexdigest(),
                    "body": normalized}
    except Exception as exc:
        return {"id": item["id"], "url": url, "status": "error", "error": type(exc).__name__}


def check(state, items, fetcher=fetch):
    if not items or len({item['id'] for item in items}) != len(items):
        raise ValueError('Monitor requires nonempty, unique source IDs')
    previous = read_json(state / "source-status.json", {})
    previous = {k: v for k, v in previous.items() if k in {item['id'] for item in items}}
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(fetcher, items):
            if row["status"] == "fetched":
                old = previous.get(row["id"])
                row["change"] = "baseline" if not old else "unchanged" if old["sha256"] == row["sha256"] else "candidate"
                if old and row["change"] == "candidate":
                    row["diff_excerpt"] = "\n".join(difflib.unified_diff(
                        old["body"].split(". "), row["body"].split(". "),
                        fromfile="previous", tofile="current", lineterm=""))[:12000]
                # State keeps one body per source, not a growing history. Actual
                # policy updates and upstream version adoption require approval.
                previous[row["id"]] = {"sha256": row["sha256"], "body": row.pop("body")}
            results.append(row)
    now = datetime.now(timezone.utc).isoformat()
    report = {"checked_at": now, "results": results,
              "limit": "Hash change is a review candidate, not a verified semantic or policy change."}
    save_json(state / "source-status.json", previous)
    save_json(state / "source-report.json", report)
    if all(r["status"] == "fetched" for r in results):
        save_json(state / "source-success.json", {"last_success": now})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()
    state = args.state or Deployment().state
    registry = read_json(ROOT / "references/registry.json")
    items = [x for x in registry["sources"] if x.get("monitor")]
    for s in read_json(ROOT / "versions.lock.json")["skills"]:
        items.append({"id": "upstream-" + s["name"], "url": f'https://api.github.com/repos/{s["repository"]}/commits?per_page=1'})
    report = check(state, items)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if any(r['status'] == 'error' for r in report['results']) else 0


if __name__ == "__main__":
    sys.exit(main())
