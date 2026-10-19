import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

# Every test process blocks real network access; requests must use an injected fake.
def no_network(*args, **kwargs):
    raise AssertionError('real network forbidden in offline tests')
socket.socket.connect = no_network
socket.create_connection = no_network


def module(name, root=ROOT):
    spec = importlib.util.spec_from_file_location(name, root / (name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for f in ROOT.glob('*.py'):
            shutil.copy(f, self.root)
        if (ROOT / 'sources').is_dir():
            shutil.copytree(ROOT / 'sources', self.root / 'sources')
        self.records = json.loads((ROOT / 'verified-metadata.json').read_text())
        self.old = b'old artifact\n'
        (self.root / 'papers.yml').write_bytes(self.old)

    def build(self, records=None):
        (self.root / 'verified-metadata.json').write_text(json.dumps(self.records if records is None else records))
        return subprocess.run([PYTHON, str(self.root / 'build_papers.py')], capture_output=True, text=True)

    def reject(self, records):
        result = self.build(records)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'papers.yml').read_bytes(), self.old)

    def test_normal_48(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        import yaml
        papers = yaml.safe_load((self.root / 'papers.yml').read_text())
        self.assertEqual(len(papers), 13)
        self.assertEqual(sum(len(p.get('related', [])) for p in papers), 35)

    def test_duplicate_cache_id(self):
        self.reject(self.records + [self.records[0]])

    def test_invalid_modern_id(self):
        for aid in ['2200.11903', '2213.11903', '2201.123', '2201.11903v1', '../x', 2201]:
            with self.subTest(aid=aid):
                records = copy.deepcopy(self.records)
                records.append(dict(records[0], id=aid))
                self.reject(records)

    def test_incomplete_or_unverified_cache(self):
        for field in ['id', 'expected', 'title', 'authors', 'year', 'link', 'title_match']:
            with self.subTest(missing=field):
                records = copy.deepcopy(self.records)
                del records[0][field]
                self.reject(records)
        for values in [{'title_match': False}, {'title_match': 1}, {'title': ''},
                       {'authors': []}, {'authors': ['']}, {'authors': 'Some Person'},
                       {'year': 'x'}, {'year': '0000'}, {'year': True}, {'year': '2023'},
                       {'link': 'https://arxiv.org/abs/2203.11171v2'},
                       {'link': 'https://evil.test/abs/2201.11903'}, {'expected': ''}]:
            with self.subTest(values=values):
                records = copy.deepcopy(self.records)
                records[0].update(values)
                self.reject(records)

    def test_same_prefix_wrong_title_and_stale_expected(self):
        for change in [{'title': self.records[0]['title'] + ' Wrong conclusion'},
                       {'title': 'Unrelated paper', 'expected': 'Unrelated paper'}]:
            with self.subTest(change=change):
                records = copy.deepcopy(self.records)
                records[0].update(change)
                self.reject(records)

    def test_only_stale_expected_rejected_preserving_old_papers(self):
        for expected in ['Completely unrelated title', self.records[0]['title'] + ' wrong ending']:
            with self.subTest(expected=expected):
                records = copy.deepcopy(self.records)
                records[0]['expected'] = expected
                self.assertEqual(records[0]['title'], self.records[0]['title'])
                result = self.build(records)
                print(f'EXPECTED_ONLY={expected!r} BUILD_EXIT={result.returncode}\n'
                      f'{result.stdout}{result.stderr}')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((self.root / 'papers.yml').read_bytes(), self.old)



class TitleTests(unittest.TestCase):
    def test_full_normalization_and_exact_aliases(self):
        from paper_validation import titles_match, TITLE_ALIASES
        self.assertTrue(titles_match('2201.11903', ' A: B—C! ', 'a b c'))
        self.assertFalse(titles_match('2201.11903', 'a' * 60 + ' right', 'a' * 60 + ' wrong'))
        for aid, (expected, actual) in TITLE_ALIASES.items():
            self.assertTrue(titles_match(aid, expected, actual))
            self.assertFalse(titles_match('2201.11903', expected, actual))
            self.assertFalse(titles_match(aid, expected, actual + ' extra'))


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.v = module('verify_papers')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / 'verified-metadata.json'
        self.out.write_bytes(b'old cache\n')
        self.v.OUT = self.out
        self.records = json.loads((ROOT / 'verified-metadata.json').read_text())[:2]
        self.v.CANDIDATES = [(r['expected'], r['id']) for r in self.records]

    def run_verify(self, responses):
        output = io.StringIO()
        with patch.object(self.v, 'fetch', side_effect=responses), patch.object(self.v.time, 'sleep'), contextlib.redirect_stdout(output):
            code = self.v.main()
        print(f'VERIFY_EXIT={code}\n{output.getvalue()}', end='')
        return code, output.getvalue()

    def xml(self, rec):
        from xml.sax.saxutils import escape
        authors = ''.join('<author><name>' + escape(a) + '</name></author>' for a in rec['authors'])
        return ('<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
                f'<id>{escape(rec["link"])}</id><title>{escape(rec["title"])}</title>'
                f'<published>{rec["year"]}-01-01T00:00:00Z</published>{authors}'
                '</entry></feed>').encode()

    def test_pass(self):
        code, output = self.run_verify([self.xml(r) for r in self.records])
        self.assertEqual(code, 0, output)
        self.assertEqual(len(json.loads(self.out.read_text())), 2)

    def test_mid_refresh_network_failure_preserves_cache(self):
        code, output = self.run_verify([self.xml(self.records[0]), OSError('offline')])
        self.assertNotEqual(code, 0)
        self.assertEqual(self.out.read_bytes(), b'old cache\n')
        self.assertIn('UNVERIFIED', output)

    def test_response_conflicts_fail_preserve_cache(self):
        for values in [{'link': 'http://arxiv.org/abs/2203.11171v2'},
                       {'title': self.records[0]['title'] + ' but wrong'},
                       {'authors': []}, {'year': '2023'}, {'title': ''}]:
            with self.subTest(values=values):
                rec = dict(self.records[0], **values)
                code, output = self.run_verify([self.xml(rec), self.xml(self.records[1])])
                self.assertEqual(code, 1, output)
                self.assertIn('FAIL', output)
                self.assertEqual(self.out.read_bytes(), b'old cache\n')

    def test_malformed_xml_unverified(self):
        code, output = self.run_verify([self.xml(self.records[0]), b'<invalid'])
        self.assertEqual(code, 2, output)
        self.assertIn('UNVERIFIED', output)
        self.assertEqual(self.out.read_bytes(), b'old cache\n')

    def test_https_fetch(self):
        with patch.object(self.v.urllib.request, 'urlopen') as opening:
            self.v.fetch('2201.11903')
        self.assertTrue(opening.call_args.args[0].full_url.startswith('https://'))
        self.assertEqual(opening.call_args.kwargs['timeout'], 45)

    def test_atomic_replace_failure_preserves_cache(self):
        with patch('os.replace', side_effect=OSError('replace denied')):
            code, output = self.run_verify([self.xml(r) for r in self.records])
        self.assertEqual(code, 2, output)
        self.assertIn('UNVERIFIED', output)
        self.assertEqual(self.out.read_bytes(), b'old cache\n')
        self.assertEqual(list(self.out.parent.iterdir()), [self.out])

    def test_keyboard_interrupt_preserves_cache(self):
        with self.assertRaises(KeyboardInterrupt):
            self.run_verify([self.xml(self.records[0]), KeyboardInterrupt()])
        self.assertEqual(self.out.read_bytes(), b'old cache\n')

    def test_ambiguous_feed_and_incomplete_publication_unverified(self):
        valid = self.xml(self.records[0])
        start = valid.index(b'<entry>')
        end = valid.index(b'</entry>') + len(b'</entry>')
        for response in [valid.replace(b'</feed>', valid[start:end] + b'</feed>'),
                         valid.replace(b'-01-01T00:00:00Z', b'-99-99T00:00:00Z'),
                         valid.replace(b'-01-01T00:00:00Z', b''),
                         valid.replace(b'2022-01-01T00:00:00Z', b'abcd-01-01T00:00:00Z')]:
            with self.subTest(response=response):
                code, output = self.run_verify([response, self.xml(self.records[1])])
                self.assertEqual(code, 2, output)
                self.assertEqual(self.out.read_bytes(), b'old cache\n')


    def test_duplicate_candidates_refused_before_fetch(self):
        self.v.CANDIDATES.append(self.v.CANDIDATES[0])
        output = io.StringIO()
        with patch.object(self.v, 'fetch') as fetch, contextlib.redirect_stdout(output):
            code = self.v.main()
        self.assertEqual(code, 1, output.getvalue())
        fetch.assert_not_called()
        self.assertEqual(self.out.read_bytes(), b'old cache\n')


    def test_all_48_cached_titles_pass_as_offline_api_fixtures(self):
        self.records = json.loads((ROOT / 'verified-metadata.json').read_text())
        self.v.CANDIDATES = module('verify_papers').CANDIDATES
        code, output = self.run_verify([self.xml(r) for r in self.records])
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(self.out.read_text()), self.records)

    def test_missing_api_fields_never_publish(self):
        import re
        valid = self.xml(self.records[0])
        self.v.CANDIDATES.reverse()
        for field in ['id', 'title', 'author', 'published']:
            with self.subTest(field=field):
                response = re.sub(rb'<' + field.encode() + rb'>.*?</' + field.encode() + rb'>', b'', valid)
                code, output = self.run_verify([self.xml(self.records[1]), response])
                self.assertNotEqual(code, 0, output)
                self.assertEqual(self.out.read_bytes(), b'old cache\n')



class SerializationTests(unittest.TestCase):
    def test_yaml_string_roundtrip(self):
        import yaml
        b = module('build_papers')
        for text in ['null', 'true', 'a # comment', 'a: b', '"quoted"', "O'Reilly", 'x, y', 'a\nb']:
            with self.subTest(text=text):
                self.assertEqual(yaml.safe_load('value: ' + b.yaml_scalar(text))['value'], text)
        rec = {'title': 'null', 'authors': ['null'], 'year': '2022',
               'link': 'https://arxiv.org/abs/2201.11903'}
        parsed = yaml.safe_load('\n'.join(b.entry(rec, 0)))[0]
        self.assertEqual(parsed['title'], 'null')
        self.assertEqual(parsed['author'], 'null')

    def test_topics_roundtrip(self):
        import yaml
        b = module('build_papers')
        with tempfile.TemporaryDirectory() as directory:
            b.HERE = Path(directory)
            shutil.copy(ROOT / 'verified-metadata.json', b.HERE)
            topics = ['a, b', 'null', 'a: b', 'x # y', '"quoted"']
            b.STRUCTURE = [('2201.11903', topics, [])]
            with contextlib.redirect_stdout(io.StringIO()):
                b.main()
            self.assertEqual(yaml.safe_load((b.HERE / 'papers.yml').read_text())[0]['topics'], topics)

    def test_build_replace_failure_preserves_old(self):
        b = module('build_papers')
        with tempfile.TemporaryDirectory() as directory:
            b.HERE = Path(directory)
            shutil.copy(ROOT / 'verified-metadata.json', b.HERE)
            out = b.HERE / 'papers.yml'
            out.write_bytes(b'old papers\n')
            with patch('os.replace', side_effect=OSError('replace denied')):
                with self.assertRaises(OSError):
                    b.main()
            self.assertEqual(out.read_bytes(), b'old papers\n')
            self.assertEqual(sorted(p.name for p in b.HERE.iterdir()), ['papers.yml', 'verified-metadata.json'])


class LinkTests(unittest.TestCase):
    def run_links(self, statuses, url='https://arxiv.org/abs/2201.11903'):
        import requests
        import runpy
        import yaml
        calls = []
        sequence = iter(statuses)

        def request(method, link, **kwargs):
            calls.append((method, link, kwargs))
            item = next(sequence)
            if isinstance(item, BaseException):
                raise item
            response = requests.Response()
            response.status_code = item
            response.url = link
            response._content = b''
            response._content_consumed = True
            return response

        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory, 'check_links.py')
            shutil.copy(ROOT / 'check_links.py', script)
            Path(directory, 'papers.yml').write_text(yaml.safe_dump([
                {'title': 'Test', 'author': 'Tester', 'year': '2022', 'link': url}]))
            with contextlib.chdir(directory), patch('requests.head', side_effect=lambda u, **kw: request('HEAD', u, **kw)), patch('requests.get', side_effect=lambda u, **kw: request('GET', u, **kw)), patch('time.sleep') as sleeping, contextlib.redirect_stdout(output):
                try:
                    runpy.run_path(str(script), run_name='__main__')
                except SystemExit as exc:
                    code = exc.code
        self.waits = [c.args[0] for c in sleeping.call_args_list]
        print(f'LINK_EXIT={code}\n{output.getvalue()}', end='')
        return code, output.getvalue(), calls

    def test_pass_uses_tls_and_timeout(self):
        code, output, calls = self.run_links([200])
        self.assertEqual(code, 0, output)
        self.assertTrue(calls[0][2].get('verify', True))
        self.assertEqual(calls[0][2].get('timeout'), 15)
        self.assertIn('PASS', output)

    def test_uncertain_and_skipped_are_unverified(self):
        import requests
        for status in [429, 500, 503, 403, 401, 202, 301, requests.exceptions.SSLError('cert'), requests.exceptions.Timeout('timeout')]:
            with self.subTest(status=status):
                code, output, calls = self.run_links([status] * 3)
                self.assertEqual(code, 2, output)
                self.assertIn('UNVERIFIED', output)
                self.assertEqual(len(calls), 3)
                self.assertEqual(self.waits, [1, 2])
        code, output, calls = self.run_links([403] * 3, 'https://dl.acm.org/example')
        self.assertEqual(code, 2, output)
        self.assertEqual(len(calls), 3)

    def test_confirmed_absence_fails(self):
        for status in [404, 410]:
            code, output, calls = self.run_links([status] * 3)
            self.assertEqual(code, 1, output)
            self.assertIn('FAIL', output)
            self.assertEqual(len(calls), 3)

    def test_transient_recovers_and_head_fallback(self):
        code, output, calls = self.run_links([503, 200])
        self.assertEqual(code, 0, output)
        self.assertEqual(len(calls), 2)
        code, output, calls = self.run_links([405, 200])
        self.assertEqual(code, 0, output)
        self.assertEqual([c[0] for c in calls], ['HEAD', 'GET'])
        self.assertEqual(calls[1][2]['timeout'], 15)
        self.assertTrue(calls[1][2].get('verify', True))
        self.assertTrue(calls[1][2]['stream'])

    def test_mixed_absence_uncertain(self):
        code, output, _ = self.run_links([404, 503, 404])
        self.assertEqual(code, 2, output)

    def test_head_not_implemented_get_fallback(self):
        code, output, calls = self.run_links([501, 200])
        self.assertEqual(code, 0, output)
        self.assertEqual([c[0] for c in calls], ['HEAD', 'GET'])

    def test_empty_input_is_unverified_without_requests(self):
        links = module('check_links')
        output = io.StringIO()
        with patch.object(links.yaml, 'safe_load', return_value=[]), patch.object(links.requests, 'head') as request, contextlib.redirect_stdout(output):
            self.assertEqual(links.main(), 2)
        request.assert_not_called()
        self.assertIn('UNVERIFIED', output.getvalue())



class ReadmeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ['gen_readme.py', 'papers.yml', 'README.md.template', 'safe_readme.py', 'atomic_output.py']:
            if (ROOT / name).exists():
                shutil.copy(ROOT / name, self.root)
        self.out = self.root / 'README.md'
        self.out.write_bytes(b'old README\n')

    def generate(self):
        return subprocess.run([PYTHON, str(self.root / 'safe_readme.py')], cwd='/', capture_output=True)

    def test_success_matches_unmodified_generator(self):
        result = self.generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = subprocess.run([PYTHON, 'gen_readme.py'], cwd=self.root, capture_output=True, check=True).stdout
        self.assertEqual(self.out.read_bytes(), expected)

    def test_failed_or_interrupted_generator_preserves_readme(self):
        self.assertTrue((self.root / 'safe_readme.py').exists(), 'safe entry point missing')
        for source in ["print('partial'); raise ValueError('bad input')", "print('partial'); raise KeyboardInterrupt()"]:
            with self.subTest(source=source):
                (self.root / 'gen_readme.py').write_text(source)
                result = self.generate()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.out.read_bytes(), b'old README\n')

    def test_replace_failure_and_parent_interrupt_preserve_readme(self):
        self.assertTrue((self.root / 'safe_readme.py').exists(), 'safe entry point missing')
        safe = module('safe_readme', self.root)
        with patch('os.replace', side_effect=OSError('denied')), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(safe.main(), 2)
        self.assertEqual(self.out.read_bytes(), b'old README\n')
        with patch.object(safe.subprocess, 'run', side_effect=KeyboardInterrupt()):
            with self.assertRaises(KeyboardInterrupt):
                safe.main()
        self.assertEqual(self.out.read_bytes(), b'old README\n')


class AdditionalValidationTests(unittest.TestCase):
    def test_duplicate_structure_ids_rejected_before_write(self):
        b = module('build_papers')
        with tempfile.TemporaryDirectory() as directory:
            b.HERE = Path(directory)
            shutil.copy(ROOT / 'verified-metadata.json', b.HERE)
            out = b.HERE / 'papers.yml'
            out.write_bytes(b'old\n')
            b.STRUCTURE = [('2201.11903', ['Test'], ['2201.11903'])]
            with self.assertRaises(ValueError):
                b.main()
            self.assertEqual(out.read_bytes(), b'old\n')


class AtomicTests(unittest.TestCase):
    def test_partial_staging_write_or_interrupt_preserves_destination(self):
        import atomic_output
        real_temporary = atomic_output.tempfile.NamedTemporaryFile
        for failure in [OSError('disk full'), KeyboardInterrupt()]:
            with self.subTest(failure=type(failure).__name__), tempfile.TemporaryDirectory() as directory:
                out = Path(directory) / 'artifact'
                out.write_bytes(b'old')

                @contextlib.contextmanager
                def broken_file(**kwargs):
                    with real_temporary(**kwargs) as stream:
                        class BrokenWriter:
                            name = stream.name

                            def write(self, content):
                                stream.write(content[:3])
                                raise failure
                        yield BrokenWriter()

                with patch.object(atomic_output.tempfile, 'NamedTemporaryFile', broken_file):
                    with self.assertRaises(type(failure)):
                        atomic_output.atomic_write(out, b'new contents')
                self.assertEqual(out.read_bytes(), b'old')
                self.assertEqual(list(Path(directory).iterdir()), [out])

    def test_serialization_failure_before_publication(self):
        import yaml
        b = module('build_papers')
        real_dump = yaml.safe_dump
        calls = 0

        def fail_later(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 7:
                raise yaml.YAMLError('serialization failed mid-build')
            return real_dump(*args, **kwargs)

        with tempfile.TemporaryDirectory() as directory:
            b.HERE = Path(directory)
            shutil.copy(ROOT / 'verified-metadata.json', b.HERE)
            out = b.HERE / 'papers.yml'
            out.write_bytes(b'old')
            with patch.object(b.yaml, 'safe_dump', side_effect=fail_later):
                with self.assertRaises(yaml.YAMLError):
                    b.main()
            self.assertEqual(out.read_bytes(), b'old')
            self.assertEqual(calls, 7)


class PortabilityTests(unittest.TestCase):
    def test_normal_build_in_checkout_without_sibling_venv(self):
        import shlex
        with tempfile.TemporaryDirectory(prefix='portability-', dir=ROOT) as directory:
            parent = Path(directory)
            checkout = parent / 'random-checkout'
            checkout.mkdir()
            self.assertFalse((parent / 'venv').exists())
            for source in ROOT.glob('*.py'):
                shutil.copy(source, checkout)
            shutil.copy(ROOT / 'verified-metadata.json', checkout)
            if (ROOT / 'sources').is_dir():
                shutil.copytree(ROOT / 'sources', checkout / 'sources')
            (checkout / 'tests').mkdir()
            shutil.copy(ROOT / 'tests/test_offline.py', checkout / 'tests')
            command = [sys.executable, '-B', '-m', 'unittest', '-v',
                       'tests.test_offline.BuildTests.test_normal_48']
            result = subprocess.run(command, cwd=checkout, capture_output=True, text=True)
            output = result.stdout + result.stderr
            print(f'COPY_CHECKOUT_CWD={checkout}\n$ {shlex.join(command)}\n'
                  f'{output}COPY_CHECKOUT_EXIT={result.returncode}')
            self.assertEqual(result.returncode, 0, output)
            self.assertIn('Ran 1 test', output)
            self.assertIn('OK', output)


class ReviewLinkSchemaTests(unittest.TestCase):
    def test_malformed_yaml_structure_is_unverified_before_any_request(self):
        cases = ['- 7', 'foo: bar', '[null]', '7', 'null', '{}',
                 '- link: https://example.test\n  related: null',
                 '- link: https://example.test\n  related: {}',
                 '- link: https://example.test\n  related: text',
                 '- link: https://example.test\n  related: [7]',
                 '- link: https://example.test\n  related: [null]',
                 '- link: https://example.test\n  related: [{}]',
                 '- {}', '- link: null', '- link: 7', '- link: []', '- link: {}',
                 '- link: ""', '- link: "   "',
                 '- link: https://example.test\n  related: [{link: 7}]',
                 '- link: https://example.test\n- 7']
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            shutil.copy(ROOT / 'check_links.py', root)
            links = module('check_links', root)
            for source in cases:
                with self.subTest(source=source):
                    (root / 'papers.yml').write_text(source)
                    output = io.StringIO()
                    with patch.object(links.requests, 'head') as head, patch.object(links.requests, 'get') as get, patch('time.sleep'), contextlib.redirect_stdout(output):
                        try:
                            code = links.main()
                        except Exception as exc:
                            self.fail(f'{source!r}: unhandled {type(exc).__name__}: {exc}')
                    print(f'SCHEMA_INPUT={source!r} EXIT={code} OUTPUT={output.getvalue()!r}')
                    self.assertEqual(code, 2, output.getvalue())
                    self.assertIn('UNVERIFIED input:', output.getvalue())
                    self.assertNotIn('FAIL', output.getvalue())
                    head.assert_not_called()
                    get.assert_not_called()


class SourceUnificationTests(unittest.TestCase):
    def test_source_counts_and_grouping_match_papers_yml(self):
        import yaml
        pv = module('paper_validation')
        source = pv.load_source()
        ids = [entry['id'] for entry in source]
        self.assertEqual(len(ids), 48, source)
        self.assertEqual(len(set(ids)), 48, '源中 id 必须唯一')
        top = [entry for entry in source if entry.get('topics')]
        self.assertEqual(len(top), 13, '主线条目应为 13 篇')
        related_total = sum(len(entry.get('related') or []) for entry in top)
        self.assertEqual(related_total, 35, '关联条目应为 35 篇')
        declared = set(ids)
        for entry in top:
            for rid in entry.get('related') or []:
                self.assertIn(rid, declared, f'主线 {entry["id"]} 引用了未声明的 related {rid}')
        # build_papers 的 STRUCTURE 与源中的主线条目一致
        self.assertEqual(
            pv.structure_from_source(),
            [(e['id'], list(e.get('topics') or []), list(e.get('related') or [])) for e in top],
        )
        # papers.yml 分组与源一致：13 主线 / 35 关联，主线 id 顺序一致
        yml = yaml.safe_load((ROOT / 'papers.yml').read_text())
        self.assertEqual(len(yml), 13)
        self.assertEqual(sum(len(p.get('related', [])) for p in yml), 35)
        yml_top_ids = [p['link'].rsplit('/', 1)[-1] for p in yml]
        self.assertEqual(yml_top_ids, [e['id'] for e in top])


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.v = module('verify_papers')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / 'verified-metadata.json'
        self.v.OUT = self.out

    def run_offline(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = self.v.main(offline=True)
        return code, output.getvalue()

    def test_offline_valid_cache_all_verified(self):
        self.out.write_bytes((ROOT / 'verified-metadata.json').read_bytes())
        code, output = self.run_offline()
        self.assertEqual(code, 0, output)
        self.assertEqual(output.count('VERIFIED (offline)'), 48, output)
        self.assertNotIn('UNVERIFIED', output)

    def test_offline_corrupt_cache_rejected_and_preserved(self):
        records = json.loads((ROOT / 'verified-metadata.json').read_text())
        bad = copy.deepcopy(records)
        del bad[0]['title_match']
        self.out.write_text(json.dumps(bad), encoding='utf-8')
        before = self.out.read_bytes()
        code, output = self.run_offline()
        self.assertNotEqual(code, 0, output)
        self.assertIn('UNVERIFIED (offline)', output)
        self.assertEqual(self.out.read_bytes(), before, '离线校验失败不得改写缓存')

    def test_offline_missing_cache_unverified(self):
        self.out.unlink(missing_ok=True)
        code, output = self.run_offline()
        self.assertEqual(code, 2, output)
        self.assertIn('UNVERIFIED (offline)', output)


class ReproducibilityTests(unittest.TestCase):
    def test_build_twice_identical_bytes(self):
        b = module('build_papers')
        with tempfile.TemporaryDirectory() as directory:
            b.HERE = Path(directory)
            shutil.copy(ROOT / 'verified-metadata.json', b.HERE)
            if (ROOT / 'sources').is_dir():
                shutil.copytree(ROOT / 'sources', b.HERE / 'sources')
            out = b.HERE / 'papers.yml'
            with contextlib.redirect_stdout(io.StringIO()):
                b.main()
            first = out.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                b.main()
            second = out.read_bytes()
        self.assertEqual(first, second, '两次生成必须字节相同')
        self.assertEqual(first.count(b'- title:'), 48)


if __name__ == '__main__':
    unittest.main()
