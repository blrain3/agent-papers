"""Small offline validation rules shared by the cache builder and refresher."""
import re
from pathlib import Path

import yaml

ID_PATTERN = r'[0-9]{2}(?:0[1-9]|1[0-2])\.[0-9]{4,5}'

SOURCE_CANDIDATES = [
    Path(__file__).resolve().parent / 'sources' / 'papers-source.yml',
    Path.cwd() / 'sources' / 'papers-source.yml',
]


def _resolve_source_path():
    for candidate in SOURCE_CANDIDATES:
        if candidate.is_file():
            return candidate
    # 向上逐级查找仓库根（兼容把脚本拷贝到临时目录再运行的情形）
    here = Path(__file__).resolve().parent
    for ancestor in here.parents:
        candidate = ancestor / 'sources' / 'papers-source.yml'
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f'找不到选文源: 已尝试 {SOURCE_CANDIDATES} 及 {here} 及其祖先下的 sources/papers-source.yml')


SOURCE_PATH = _resolve_source_path()


def load_source():
    """从统一人工选文源读取全部 48 篇条目（列表，顺序即 CANDICATES 顺序）。"""
    with SOURCE_PATH.open(encoding='utf-8') as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict) or not isinstance(data.get('papers'), list):
        raise ValueError('选文源格式错误：缺少 papers 列表')
    return data['papers']


def candidates_from_source(papers=None):
    """由选文源生成 (expected_title, arXiv id) 候选清单，供 verify_papers 使用。"""
    if papers is None:
        papers = load_source()
    candidates = []
    seen = set()
    for entry in papers:
        aid = entry['id']
        title = entry['expected_title']
        if aid in seen:
            raise ValueError(f'选文源中重复 ID: {aid}')
        seen.add(aid)
        candidates.append((title, aid))
    return candidates


def structure_from_source(papers=None):
    """由选文源生成 (top_id, topics, related) 主线结构，供 build_papers 使用。"""
    if papers is None:
        papers = load_source()
    structure = []
    for entry in papers:
        topics = entry.get('topics') or []
        related = entry.get('related') or []
        if topics:
            structure.append((entry['id'], list(topics), list(related)))
    return structure


def validate_id(aid):
    if not isinstance(aid, str) or not re.fullmatch(ID_PATTERN, aid):
        raise ValueError(f'invalid modern arXiv ID: {aid!r}')


def validate_record(rec):
    if not isinstance(rec, dict):
        raise ValueError('metadata record must be an object')
    for field in ('id', 'expected', 'title', 'authors', 'year', 'link', 'title_match'):
        if field not in rec:
            raise ValueError(f'missing metadata field: {field}')
    aid = rec['id']
    validate_id(aid)
    for field in ('expected', 'title'):
        if not isinstance(rec[field], str) or not rec[field].strip():
            raise ValueError(f'invalid {field}: {aid}')
    if (not isinstance(rec['authors'], list) or not rec['authors']
            or any(not isinstance(a, str) or not a.strip() for a in rec['authors'])):
        raise ValueError(f'invalid authors: {aid}')
    if rec['year'] != '20' + aid[:2]:
        raise ValueError(f'invalid publication year: {aid}')
    if (not isinstance(rec['link'], str)
            or not re.fullmatch(r'https?://arxiv\.org/abs/' + re.escape(aid)
                                + r'(?:v[1-9][0-9]*)?', rec['link'])):
        raise ValueError(f'returned link ID differs from requested ID: {aid}')
    if rec['title_match'] is not True:
        raise ValueError(f'unverified title: {aid}')
    if not titles_match(aid, rec['expected'], rec['title']):
        raise ValueError(f'cached expected title conflicts with actual title: {aid}')


TITLE_ALIASES = {
    '2307.07924': (
        'Communicative Agents for Software Development',
        'ChatDev: Communicative Agents for Software Development'),
    '2406.12045': (
        'tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains',
        '$τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains'),
    '2506.06941': (
        'The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models',
        'The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity'),
}


def normalize_title(title):
    import unicodedata
    title = unicodedata.normalize('NFKC', title).casefold()
    return ' '.join(''.join(' ' if unicodedata.category(c)[0] in 'PZ' else c
                            for c in title).split())


def titles_match(aid, expected, actual):
    if normalize_title(expected) == normalize_title(actual):
        return True
    alias = TITLE_ALIASES.get(aid)
    return bool(alias and normalize_title(expected) == normalize_title(alias[0])
                and normalize_title(actual) == normalize_title(alias[1]))
