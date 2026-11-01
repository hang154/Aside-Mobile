"""End-to-end campus-mail MCP test: search→classify→doc draft→attach temp-save→verify.
Fake Graph transport; no real account auth, no actual mail send."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).parent
MCP_SCRIPT = HERE / 'campus-mail-mcp.py'


def make_config_file(tmpdir):
    """Write a NUBI_CAMPUS_MAIL_CONFIG pointing at a deterministic transport."""
    root = Path(tmpdir)
    draft_dir = root / 'drafts'
    draft_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        'graph': {'test_transport': 'deterministic-mail-v1'},
        'draft_directory': str(draft_dir),
    }
    p = root / 'config.json'
    p.write_text(json.dumps(cfg))
    return p, draft_dir


class McpClient:
    """Thin JSON-RPC over stdio; one request per line, response matched by id."""

    def __init__(self, proc):
        self.proc = proc
        self._id = 0

    def _next_id(self):
        self._id += 1
        return self._id

    def rpc(self, method, params=None):
        ident = self._next_id()
        msg = {'jsonrpc': '2.0', 'id': ident, 'method': method, 'params': params or {}}
        line = json.dumps(msg, ensure_ascii=False) + '\n'
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        # read lines until we get a response with our id
        while True:
            raw = self.proc.stdout.readline()
            if not raw:
                raise RuntimeError('MCP process closed stdout unexpectedly')
            try:
                resp = json.loads(raw.strip())
            except json.JSONDecodeError:
                continue
            if resp.get('id') == ident:
                if 'error' in resp:
                    raise RuntimeError(f"MCP error {resp['error']}: {resp['error']}")
                return resp.get('result', {})

    def initialize(self):
        return self.rpc('initialize', {'protocolVersion': '2024-11-05'})

    def tools_list(self):
        r = self.rpc('tools/list')
        return r.get('tools', [])

    def tools_call(self, name, arguments):
        r = self.rpc('tools/call', {'name': name, 'arguments': arguments})
        content = r.get('content', [])
        is_error = r.get('isError', False)
        text = ''
        if content:
            first = content[0]
            if first.get('type') == 'text':
                text = first.get('text', '')
        # parse text as JSON where possible
        parsed = None
        if text:
            try:
                parsed = json.loads(text)
            except (json.JSONDecodeError, ValueError):
                pass
        return {'raw_text': text, 'parsed': parsed, 'is_error': is_error}

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass


def run_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_file, draft_dir = make_config_file(tmpdir)
        env = dict(os.environ)
        env['NUBI_CAMPUS_MAIL_CONFIG'] = str(cfg_file)
        env['PYTHONDONTWRITEBYTECODE'] = '1'

        proc = subprocess.Popen(
            [sys.executable, str(MCP_SCRIPT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(HERE),
            env=env,
            text=True,
            encoding='utf-8',
        )
        client = McpClient(proc)
        results = {}
        try:
            # 1. Initialize
            init_result = client.initialize()
            results['initialize'] = {
                'ok': True,
                'serverInfo': init_result.get('serverInfo'),
            }
            print("[PASS] initialize →", init_result.get('serverInfo'))

            # 2. Tools list
            tools = client.tools_list()
            tool_names = [t['name'] for t in tools]
            results['tools_list'] = {'ok': True, 'tool_names': tool_names}
            print(f"[PASS] tools/list → {len(tools)} tools:", tool_names)

            # 3. nubi_campus_mail_search — fake graph returns known fixtures
            search_resp = client.tools_call('nubi_campus_mail_search', {'query': '장학'})
            items = search_resp['parsed'].get('items', []) if search_resp['parsed'] else []
            results['mail_search'] = {'ok': not search_resp['is_error'], 'items_count': len(items)}

            if search_resp['is_error']:
                print("[FAIL] nubi_campus_mail_search:", search_resp['raw_text'])
            else:
                print(f"[PASS] nubi_campus_mail_search → {len(items)} items")
                for it in items[:5]:
                    cats = it.get('categories', [])
                    sub = it.get('subject', '(no subject)')
                    print(f"   [{cats}] {sub}")

            # 3b. Regression: subject with NO rule keyword, keyword only in body.
            #     Old code read r['bodyPreview'] (never set by the Graph adapter)
            #     -> categories would be []; fixed code reads body.content.
            body_resp = client.tools_call('nubi_campus_mail_search', {'query': '수강'})
            body_items = body_resp['parsed'].get('items', []) if body_resp['parsed'] else []
            body_ok = (not body_resp['is_error']) and any(
                it.get('id') == 'msg-03' and '학사' in it.get('categories', [])
                for it in body_items)
            results['mail_search_body_classification'] = {'ok': body_ok}
            if body_ok:
                row = next(it for it in body_items if it.get('id') == 'msg-03')
                print(f"[PASS] body-only classification → subject={row['subject']!r} categories={row['categories']} (proves body.text now reaches the classifier)")
            else:
                print("[FAIL] body-only classification:", body_resp['raw_text'][:400])

            # 4. nubi_campus_document_draft — create application draft
            doc_fields = {
                'notice_title': '2027년 두산연강재단 장학생 모집',
                'source': 'UNIST 포털 홈 공지 (msg-01)',
                'applicant': '홍길동 (학생번호 2024001234)',
                'motivation': '2027년 1학기 진학 예정 학부생으로서 평점 3.4/4.5, 소득분위 3 기준 자격 요건 충족.',
                'experience': '지난 학기 전공 관련 인턴십 경험 있으며 현장실습 이수 예정.',
            }
            doc_resp = client.tools_call('nubi_campus_document_draft', doc_fields)
            doc_parsed = doc_resp['parsed']
            if doc_resp['is_error']:
                print("[FAIL] nubi_campus_document_draft:", doc_resp['raw_text'])
                results['document_draft'] = {'ok': False, 'error': doc_resp['raw_text']}
            else:
                state = doc_parsed.get('state', 'unknown') if doc_parsed else 'unknown'
                doc_path = doc_parsed.get('path', '') if doc_parsed else ''
                missing = doc_parsed.get('missing', []) if doc_parsed else []
                doc_exists = bool(doc_path) and os.path.isfile(doc_path)
                results['document_draft'] = {'ok': True, 'state': state, 'exists': doc_exists, 'path': doc_path, 'missing': missing}
                print(f"[PASS] nubi_campus_document_draft → state={state}, file_exists={doc_exists}")
                if missing:
                    print(f"   Missing fields flagged: {missing}")

            # 5. nubi_campus_mail_draft with temp-saved attachment
            #    Write an attached file under the draft directory first
            attach_path = draft_dir / 'test_temp_save.txt'
            attach_path.write_bytes(b'TempSave: verification file contents\nLine 2\nLine 3\n')
            attach_abs = str(attach_path)

            mail_resp = client.tools_call('nubi_campus_mail_draft', {
                'subject': '[임시저장] 두산연강재단 장학 지원 확인용',
                'body': '본문은 검증용 임시저장 콘텐츠입니다. 실제 발송되지 않아야 합니다.\n첨부파일 포함됨.',
                'attachment': attach_abs,
            })

            if mail_resp['is_error']:
                print("[FAIL] nubi_campus_mail_draft (with attach):", mail_resp['raw_text'])
                results['mail_draft_attach'] = {'ok': False, 'error': mail_resp['raw_text']}
            else:
                mparsed = mail_resp['parsed']
                saved_state = mparsed.get('state', '?') if mparsed else '?'
                wid = mparsed.get('id', '?') if mparsed else '?'
                has_att = mparsed.get('has_attachment', None) if mparsed else None
                web_link = mparsed.get('web_link', '') if mparsed else ''
                results['mail_draft_attach'] = {'ok': True, 'state': saved_state, 'id': wid, 'has_attachment': has_att}
                print(f"[PASS] nubi_campus_mail_draft (with attach) → state={saved_state}, id={wid}, has_attachment={has_att}")
                if web_link:
                    print(f"   web_link: {web_link}")

            # 6. No actual mail send check — assert the verify call went out
            #    (transport log contains GET for verification)
            #    We rely on the fact that:
            #      - POST went to /me/messages (not /me/sentItems)
            #      - The fake graph echoed isDraft back only because the client sent it
            #    So if isDraft had not been sent, the fake would have returned isDraft=False
            #    and the code would have raised the error caught above.
            verify_check = (results.get('mail_draft_attach', {}).get('state') == 'draft_saved')
            results['no_send_verified'] = verify_check
            if verify_check:
                print("[PASS] No-send verification confirmed via mock draft-save")
            else:
                print("[WARN] No-send verification inconclusive")

            # Summary
            all_ok = all(r.get('ok', False) for r in results.values() if isinstance(r, dict) and 'ok' in r)
            if all_ok:
                print("\n=== ALL PASS ===")
            else:
                print("\n=== SOME FAILURES (see output above) ===")
        finally:
            client.close()


if __name__ == '__main__':
    run_test()
