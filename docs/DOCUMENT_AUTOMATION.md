# 누비 문서 자동화 0.2.4

## 동작

각 목표의 채팅에서 `L시리즈`, `UIRP`, `예산서`, `지원요청서`, `문서 작성`, `DOCX`, `HWPX`, `SharePoint`가 현재 지시에 포함되면 문서 실행기로 보낸다. 이전 대화에만 해당 단어가 있는 경우 브라우저 작업을 문서로 바꾸지 않는다. 같은 사용자 요청의 작업 ID는 중복 생성하지 않는다.

메일·첨부/등록된 자료 → Qwen의 구조화된 작성 도구 호출 → 인용 구절/금액/통화/등록 계좌/누락 검사 → DOCX와 HWPX → 준비된 문서만 지정 SharePoint 폴더에 업로드 → 다운로드한 원격 바이트의 SHA-256 재검증 순서다. 메일 발송은 포함하지 않는다.

`needs_information`은 초안 생성 완료이며 제출 완료가 아니다. `needs_destination`은 문서 검산 후 업로드 연결이 없는 상태, `draft_only`는 사용자 지시에 따른 작성 전용, `uploaded`만 실제 업로드·원격 파일 재확인이 끝난 상태다. 앱 대화에 상태와 DOCX/HWPX 열기 버튼을 저장한다. 파일 다운로드는 인증된 TLS와 파일 해시를 검증하고 목표에 귀속된 생성 파일만 허용한다.

## 지원 범위

- DOCX/HWPX 생성, DOCX/HWPX/HWP5 및 텍스트 입력. HWP5 바이너리 `.hwp` 저장은 지원하지 않는다. HWPX는 확장자를 바꾼 텍스트 파일이 아니라 실제 XML ZIP 문서다.
- 실제 UIRP·AICP 추가지원금 DOCX 양식은 지정된 6개 표 구조와 셀 서식을 보존해 채운다. 표 구조가 바뀌면 오류로 멈춘다. 서명은 만들지 않는다.
- L시리즈는 근거 기반 예산/지원요청 문서를 새로 작성한다. 기존 HWPX는 읽기 근거다. 기존 L시리즈의 모든 공식 양식·이미지·페이지 배치를 자동 재현하는 기능은 아직 없다.
- 금액과 수량은 인용 근거에 있는 수치로 검증하며 Decimal로 계산한다. USD와 KRW를 합산하지 않는다. 해외 결제는 실제 원화 정산액을 확인하기 전 제출 가능한 원화 합계로 표시하지 않는다.
- 학교 등록 은행/계좌와 신청 은행/계좌를 비교한다. 계좌 끝자리만으로 전체 계좌를 추정하지 않는다. 모든 의미적 사실이나 기관의 지원 자격을 자동 증명하는 것은 아니다.
- 문서 ZIP 무결성·텍스트 재추출·합계를 검사한다. 모든 한글/Word 앱에서 페이지 잘림과 서체까지 보장하는 시각 검수는 별도다.

## 호스트 설정

의존성은 `opencli-nubi/documents/requirements.txt`에 고정한다. Python 환경과 설정 위치:

```bash
python3 -m venv --system-site-packages ~/.local/share/nubi-documents/venv
~/.local/share/nubi-documents/venv/bin/pip install -r opencli-nubi/documents/requirements.txt
```

`NUBI_DOCUMENT_PYTHON`은 문서 작업 인터프리터 경로, `NUBI_DOCUMENT_CONFIG`는 호스트 전용 설정 파일 경로다. 기본값은 각각 `~/.local/share/nubi-documents/venv/bin/python`, `~/.config/nubi-documents/config.json`이다. 모델 인증은 기존 Azrael Qwen 연결의 bearer-file을 사용하고 모델에는 인증키를 전달하지 않는다.

설정 예시(실제 비밀정보·개인 문서는 Git에 보관하지 않는다):

```json
{
  "graph": {
    "client_id": "USER_OWNED_ENTRA_PUBLIC_CLIENT_ID",
    "tenant_id": "TENANT_ID",
    "account": "ACCOUNT_UPN",
    "cache_file": "/PRIVATE/PATH/graph-cache.json"
  },
  "profiles": {
    "lseries": {
      "mail_query": "L시리즈 소프트웨어",
      "allow_upload": true,
      "target": {
        "drive_id": "DISCOVERED_DRIVE_ID",
        "folder_id": "DISCOVERED_FOLDER_ID",
        "hostname": "TENANT.sharepoint.com"
      }
    },
    "uirp": {"mail_query": "UIRP 연구지원금", "allow_upload": false}
  }
}
```

조직에서 허용하는 Entra 공개 클라이언트 등록과 delegated `Mail.Read`, `Files.ReadWrite`가 필요하다. 최초 로그인은 다음 명령의 Microsoft device-code 화면에서 수행하며 토큰을 채팅에 붙여 넣지 않는다.

```bash
~/.local/share/nubi-documents/venv/bin/python opencli-nubi/document-auth.py --config ~/.config/nubi-documents/config.json
```

현재 연결된 Outlook 앱 인증과 호스트 Microsoft Graph 인증은 별개다. SharePoint 커넥터도 연결 후 쓰기 도구가 실제 제공되는지 확인해야 한다. 읽기 연결만으로 업로드 성공을 주장하지 않는다. 기관 정책상 쓰기 권한이 제한되면 실제 업로드 검증은 연결 해결 전 완료되지 않는다.

## 자료 가져오기 방식

Graph 인증이 있으면 메일과 첨부를 실행 때 조회한다. 초기 가져오기/재현에는 프로필별 `source_manifest`를 사용할 수 있다:

```json
{"sources":{"mail-1":{"title":"메일 제목","text":"실제 메일 본문","url":"원본 메일 링크"}},"template":"/PRIVATE/PATH/uirp-template.docx"}
```

`source_manifest`는 가져온 시점의 자료이며 이후 새 메일이 자동 반영되지 않는다. 이번 실기기 시험은 연결된 Outlook 도구로 실제 자료를 가져온 후 이 방식으로 실행했다. 누비 호스트에 Microsoft Graph 로그인은 아직 등록하지 않았다.

## MCP와 실행

`opencli-nubi/nubi-documents-mcp.py`는 `nubi_document_run(instruction, profile)`을 제공한다. `profile`은 `lseries`, `uirp`, `general`이다. 모델이 업로드 경로·인증파일·임의 실행 코드를 선택하지 못하고 서버 설정에만 목적지를 둔다. MCP 프로세스는 위 가상환경 Python으로 시작한다. 읽기 전용 브라우저 도구와 문서 작성/파일 전달 도구를 구분한다.

기존 `nubi-goal-chat.service`가 문서 실행기를 자동 시작한다. 앱에서는 별도 명령줄 실행이 필요 없다. 앱이 화면을 벗어나면 진행 중인 작업을 취소한다. 업로드가 시작된 뒤 취소/연결 중단이 발생한 경우 원격에 파일이 남을 수 있으므로 저장된 업로드 영수증으로 확인해야 한다. 다중 파일 전달은 원자적 트랜잭션이 아니다. 충돌 시 덮어쓰지 않고 실패한다.

## 검증

- `PYTHONPATH=opencli-nubi ~/.local/share/nubi-documents/venv/bin/python -m unittest documents.test_documents -v`
- `python3 opencli-nubi/test-document-jobs.py`
- `python3 opencli-nubi/test-chat-jobs.py`
- Android 실기기 instrumentation: 48개 검사.

Graph 업로드/원격 바이트 비교 자동 검사는 모의 전송이다. 실서비스 SharePoint 업로드 성공 증거와 구분한다. 실제 학교 메일·신청서·생성 문서·인증 캐시·캡처는 로컬에만 보관한다.

참고: [Microsoft Graph 업로드 세션](https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0), [python-hwpx 공식 사용법](https://github.com/airmang/python-hwpx/blob/main/docs/quickstart.md).
