#!/usr/bin/env python3
# Local fork of facundoolano/software-papers (MIT, Copyright (c) 2022 Facundo Olano).
# Modified locally: TLS, timeouts, bounded retries, and explicit verification states.
"""Check reachability: PASS=0, confirmed absence FAIL=1, UNVERIFIED=2."""
import time
from pathlib import Path

import requests
import yaml

HEADERS = {'User-Agent': 'agent-papers-link-check/1.0'}
TIMEOUT = 15
ATTEMPTS = 3


def check_link(url):
    observations = []
    for attempt in range(ATTEMPTS):
        if attempt:
            time.sleep(attempt)
        try:
            with requests.head(url, headers=HEADERS, verify=True, timeout=TIMEOUT,
                               allow_redirects=True) as response:
                status = response.status_code
            if status in (405, 501):
                with requests.get(url, headers=HEADERS, verify=True, timeout=TIMEOUT,
                                  allow_redirects=True, stream=True) as response:
                    status = response.status_code
        except requests.RequestException as exc:
            observations.append(type(exc).__name__)
            continue
        if status in (200, 204, 206):
            return 0, f'PASS HTTP {status}'
        observations.append(status)
    if all(status == observations[0] for status in observations) and observations[0] in (404, 410):
        return 1, f'FAIL confirmed HTTP {observations[0]} ({ATTEMPTS} attempts)'
    return 2, f'UNVERIFIED {observations}'


def main():
    try:
        with Path(__file__).with_name('papers.yml').open(encoding='utf-8') as stream:
            papers = yaml.safe_load(stream)
        if not isinstance(papers, list):
            raise ValueError('YAML root must be a list')
        if not papers:
            print('UNVERIFIED no papers checked')
            return 2
        all_papers = []
        for index, paper in enumerate(papers):
            if not isinstance(paper, dict):
                raise ValueError(f'paper {index} must be a mapping')
            related = paper.get('related', [])
            if not isinstance(related, list):
                raise ValueError(f'paper {index} related must be a list')
            all_papers.append(paper)
            all_papers.extend(related)
        links = []
        for index, paper in enumerate(all_papers):
            if not isinstance(paper, dict):
                raise ValueError(f'entry {index} must be a mapping')
            link = paper.get('link')
            if not isinstance(link, str) or not link.strip():
                raise ValueError(f'entry {index} link must be a nonempty string')
            links.append(link)
    except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as exc:
        print(f'UNVERIFIED input: {exc}')
        return 2
    codes = []
    for link in links:
        code, message = check_link(link)
        codes.append(code)
        print(f'{message}: {link}')
    return 1 if 1 in codes else (2 if 2 in codes else 0)


if __name__ == '__main__':
    raise SystemExit(main())
