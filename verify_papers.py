#!/usr/bin/env python3
"""Verify every paper in this list against the arXiv API.

Why this exists: a curated paper list rots through silent misattribution — a remembered title,
a wrong year, a link that 404s. So no entry in `papers.yml` is hand-written. This script takes
(expected title, arXiv id) pairs, fetches the authoritative metadata, and reports any mismatch
between the title you asked for and the title arXiv returns. `build_papers.py` then refuses to
generate `papers.yml` from anything that was not verified.

Usage:
    python3 verify_papers.py          # 网络模式：刷新 verified-metadata.json
    python3 verify_papers.py --offline  # 离线模式：只读现有缓存做校验，不发网络请求
    python3 build_papers.py           # regenerate papers.yml
    python3 safe_readme.py            # safely regenerate README.md
    python3 check_links.py            # confirm every link resolves

arXiv asks for ~3s between requests; this script obeys that and takes about 2.5 minutes.
"""
import argparse
import json
from datetime import datetime
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from atomic_output import atomic_write
from paper_validation import validate_record, titles_match, validate_id, candidates_from_source

NS = {"a": "http://www.w3.org/2005/Atom"}
OUT = Path(__file__).with_name("verified-metadata.json")

CANDIDATES = candidates_from_source()


def fetch(arxiv_id):
    url = ("https://export.arxiv.org/api/query?"
           + urllib.parse.urlencode({"id_list": arxiv_id, "max_results": 1}))
    req = urllib.request.Request(url, headers={"User-Agent": "agent-papers-verify/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read()


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    entries = root.findall("a:entry", NS)
    if len(entries) != 1:
        raise ValueError('expected exactly one API entry')
    entry = entries[0]
    published = entry.findtext("a:published", "", NS)
    datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
    return {
        "title": " ".join((entry.findtext("a:title", "", NS) or "").split()),
        "authors": [a.findtext("a:name", "", NS) for a in entry.findall("a:author", NS)],
        "year": entry.findtext("a:published", "", NS)[:4],
        "link": entry.findtext("a:id", "", NS),
    }


def main_offline():
    """只读现有缓存做上述校验，不发任何网络请求。"""
    try:
        raw = OUT.read_text(encoding='utf-8')
    except OSError as exc:
        print(f'UNVERIFIED (offline) 缓存不可读: {exc}')
        return 2
    try:
        records = json.loads(raw)
    except ValueError as exc:
        print(f'UNVERIFIED (offline) 缓存非法 JSON: {exc}')
        return 2
    if not isinstance(records, list):
        print('UNVERIFIED (offline) 缓存根须为列表')
        return 2

    expected_ids = {aid for _title, aid in CANDIDATES}
    seen = set()
    statuses = []
    for rec in records:
        aid = rec.get('id') if isinstance(rec, dict) else '<unknown>'
        try:
            validate_record(rec)
            if aid in seen:
                raise ValueError(f'缓存中重复 ID: {aid}')
            seen.add(aid)
            if aid not in expected_ids:
                raise ValueError(f'缓存中未在选文源的 ID: {aid}')
            print(f'VERIFIED (offline) {aid}')
            statuses.append(0)
        except (ValueError, KeyError, TypeError) as exc:
            print(f'UNVERIFIED (offline) {aid}: {exc}')
            statuses.append(2)
    missing = sorted(expected_ids - seen)
    if missing:
        print(f'UNVERIFIED (offline) 缓存缺失条目: {missing}')
        statuses.append(2)
    if not records:
        print('UNVERIFIED (offline) 缓存为空')
        return 2
    return 1 if 1 in statuses else (2 if 2 in statuses else 0)


def main_online():
    seen = set()
    try:
        if not CANDIDATES:
            raise ValueError('no candidates to verify')
        for expected, aid in CANDIDATES:
            validate_id(aid)
            if aid in seen or not isinstance(expected, str) or not expected.strip():
                raise ValueError(f'duplicate ID or empty candidate title: {aid}')
            seen.add(aid)
    except ValueError as exc:
        print(f'FAIL candidate configuration: {exc}')
        return 1
    results, statuses = [], []
    for expected, aid in CANDIDATES:
        try:
            data = parse(fetch(aid))
        except Exception as exc:
            print(f"UNVERIFIED {aid}: fetch/parse error: {exc}")
            statuses.append(2)
        else:
            if data is None:
                print(f"UNVERIFIED {aid}: no entry returned")
                statuses.append(2)
            else:
                rec = {"expected": expected, "id": aid, **data,
                       "title_match": titles_match(aid, expected, data['title'])}
                try:
                    validate_record(rec)
                except ValueError as exc:
                    print(f"FAIL {aid}: {exc}")
                    statuses.append(1)
                else:
                    results.append(rec)
                    print(f"VERIFIED {aid}: {data['title']}")
        time.sleep(3)
    if statuses:
        return 1 if 1 in statuses else 2
    try:
        atomic_write(OUT, json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8'))
    except Exception as exc:
        print(f"UNVERIFIED cache publication failed: {exc}")
        return 2
    print(f"VERIFIED verified {len(results)}/{len(CANDIDATES)} -> {OUT.name}")
    return 0


def main(offline=False):
    if offline:
        return main_offline()
    return main_online()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify paper metadata against arXiv.')
    parser.add_argument('--offline', action='store_true',
                        help='只读现有缓存做校验，不发任何网络请求')
    args = parser.parse_args()
    raise SystemExit(main(offline=args.offline))
