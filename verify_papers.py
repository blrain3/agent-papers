#!/usr/bin/env python3
"""Verify every paper in this list against the arXiv API.

Why this exists: a curated paper list rots through silent misattribution — a remembered title,
a wrong year, a link that 404s. So no entry in `papers.yml` is hand-written. This script takes
(expected title, arXiv id) pairs, fetches the authoritative metadata, and reports any mismatch
between the title you asked for and the title arXiv returns. `build_papers.py` then refuses to
generate `papers.yml` from anything that was not verified.

Usage:
    python3 verify_papers.py          # fetch/refresh verified-metadata.json
    python3 build_papers.py           # regenerate papers.yml
    python3 gen_readme.py > README.md # regenerate README.md
    python3 check_links.py            # confirm every link resolves

arXiv asks for ~3s between requests; this script obeys that and takes about 2.5 minutes.
"""
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"a": "http://www.w3.org/2005/Atom"}
OUT = Path(__file__).with_name("verified-metadata.json")

CANDIDATES = [
    ("Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", "2201.11903"),
    ("Self-Consistency Improves Chain of Thought Reasoning in Language Models", "2203.11171"),
    ("Least-to-Most Prompting Enables Complex Reasoning in Large Language Models", "2205.10625"),
    ("Tree of Thoughts: Deliberate Problem Solving with Large Language Models", "2305.10601"),
    ("ReAct: Synergizing Reasoning and Acting in Language Models", "2210.03629"),
    ("Reflexion: Language Agents with Verbal Reinforcement Learning", "2303.11366"),
    ("Self-Refine: Iterative Refinement with Self-Feedback", "2303.17651"),
    ("Let's Verify Step by Step", "2305.20050"),
    ("Chain of Agents: Large Language Models Collaborating on Long-Context Tasks", "2406.02818"),
    ("Toolformer: Language Models Can Teach Themselves to Use Tools", "2302.04761"),
    ("ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs", "2307.16789"),
    ("Gorilla: Large Language Model Connected with Massive APIs", "2305.15334"),
    ("Executable Code Actions Elicit Better LLM Agents", "2402.01030"),
    ("MemGPT: Towards LLMs as Operating Systems", "2310.08560"),
    ("Generative Agents: Interactive Simulacra of Human Behavior", "2304.03442"),
    ("A-MEM: Agentic Memory for LLM Agents", "2502.12110"),
    ("Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory", "2504.19413"),
    ("LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory", "2410.10813"),
    ("Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "2005.11401"),
    ("Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", "2310.11511"),
    ("Lost in the Middle: How Language Models Use Long Contexts", "2307.03172"),
    ("Cognitive Architectures for Language Agents", "2309.02427"),
    ("The Rise and Potential of Large Language Model Based Agents: A Survey", "2309.07864"),
    ("A Survey on Large Language Model based Autonomous Agents", "2308.11432"),
    ("A Survey of AI Agent Protocols", "2504.16736"),
    ("SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", "2310.06770"),
    ("SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering", "2405.15793"),
    ("OpenHands: An Open Platform for AI Software Developers as Generalist Agents", "2407.16741"),
    ("WebArena: A Realistic Web Environment for Building Autonomous Agents", "2307.13854"),
    ("OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments", "2404.07972"),
    ("AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation", "2308.08155"),
    ("MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework", "2308.00352"),
    ("CAMEL: Communicative Agents for \"Mind\" Exploration of Large Language Model Society", "2303.17760"),
    ("Communicative Agents for Software Development", "2307.07924"),
    ("Why Do Multi-Agent LLM Systems Fail?", "2503.13657"),
    ("AI Agents That Matter", "2407.01502"),
    ("AgentBench: Evaluating LLMs as Agents", "2308.03688"),
    ("tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", "2406.12045"),
    ("Agent-as-a-Judge: Evaluate Agents with Agents", "2410.10934"),
    ("The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models", "2506.06941"),
    ("Training language models to follow instructions with human feedback", "2203.02155"),
    ("Direct Preference Optimization: Your Language Model is Secretly a Reward Model", "2305.18290"),
    ("Constitutional AI: Harmlessness from AI Feedback", "2212.08073"),
    ("DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", "2501.12948"),
    ("Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters", "2408.03314"),
    ("Measuring AI Ability to Complete Long Software Tasks", "2503.14499"),
    ("Towards a Science of Scaling Agent Systems", "2512.08296"),
    ("Voyager: An Open-Ended Embodied Agent with Large Language Models", "2305.16291"),
]

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def fetch(arxiv_id):
    url = ("http://export.arxiv.org/api/query?"
           + urllib.parse.urlencode({"id_list": arxiv_id, "max_results": 1}))
    req = urllib.request.Request(url, headers={"User-Agent": "agent-papers-verify/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read()


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    entry = root.find("a:entry", NS)
    if entry is None:
        return None
    return {
        "title": " ".join((entry.findtext("a:title", "", NS) or "").split()),
        "authors": [a.findtext("a:name", "", NS) for a in entry.findall("a:author", NS)],
        "year": entry.findtext("a:published", "", NS)[:4],
        "link": entry.findtext("a:id", "", NS),
    }


def main():
    results, problems = [], []
    for expected, aid in CANDIDATES:
        try:
            data = parse(fetch(aid))
        except Exception as exc:  # noqa: BLE001
            problems.append((expected, aid, f"fetch error: {exc}"))
            time.sleep(3)
            continue
        if data is None:
            problems.append((expected, aid, "no entry returned"))
            time.sleep(3)
            continue
        ok = norm(expected)[:40] in norm(data["title"]) or norm(data["title"])[:40] in norm(expected)
        results.append({"expected": expected, "id": aid, **data, "title_match": ok})
        first = data["authors"][0].split()[-1] if data["authors"] else "?"
        print(f'{"ok " if ok else "!! "}{data["year"]}  {first:<12} {aid:<11} {data["title"][:60]}')
        if not ok:
            problems.append((expected, aid, f"MISMATCH -> {data['title']}"))
        time.sleep(3)

    OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nverified {len(results)}/{len(CANDIDATES)}  ->  {OUT.name}   problems: {len(problems)}")
    for exp, aid, why in problems:
        print(f"  {aid}: {why}\n      expected: {exp}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
