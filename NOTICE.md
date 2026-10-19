# Third-party notices

## Vendored scripts

`gen_readme.py` is taken unmodified from
[facundoolano/software-papers](https://github.com/facundoolano/software-papers).
Its original header and bytes are preserved; this offline repair did not change it.

`check_links.py` is a local fork from the same project. Local modifications enable
TLS verification, timeouts, bounded retries with waits, HEAD-to-GET fallback,
and explicit PASS / FAIL / UNVERIFIED results. It no longer skips ACM as success.
Both scripts retain the upstream MIT copyright and license below:

Baseline of this repair: commit `a1f027a` (2026-09-16), "Initial commit: 48 arXiv-verified
papers on LLM agents and agent systems". `gen_readme.py` is byte-identical to that
baseline (verified with `git diff master -- gen_readme.py` empty). `check_links.py`
has been locally modified since the baseline; the diff scope is limited to request
verification/timeout/retry behavior and result reporting, with the upstream MIT
copyright notice and attribution retained.

```
MIT License

Copyright (c) 2022 Facundo Olano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Paper metadata

Titles, author lists, publication years and links come from the existing arXiv API
metadata cache. The offline repair did not refresh that cache or verify live links.
The papers themselves belong to their authors and are linked, not redistributed.
