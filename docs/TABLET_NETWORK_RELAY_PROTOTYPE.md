# 태블릿 네트워크 브라우저 제어 시험

이 코드는 실험용이다. PC에서 MCP 서버를 실행하고, 태블릿이 HTTPS로 중계 서버에 접속해 브라우저를 제어한다. USB 포워딩·CDP는 명령 전달에 쓰지 않는다. 외부 LLM은 이 MCP 서버를 실행하는 환경에서 도구 호출을 할 수 있다. MCP 컨트롤러와 중계 서버는 현재 같은 컴퓨터여야 한다. 앱은 포그라운드에 있어야 하며, 현재는 공개 영어 위키백과의 검색·문서 열기·관찰만 허용한다. 임의 사이트 탐색, 버튼 클릭, 입력, 백그라운드 동작, 외부 서비스 호스팅은 아직 구현하지 않았다.

## 실행 원리

MCP stdio → 로컬 HTTPS 제어 API → 메모리 명령 큐 → 태블릿의 HTTPS 폴링 → Android WebView. WebView 실행은 태블릿에서 한다. 명령 식별자는 임의로 생성되며 만료된 큐 항목은 전달하지 않는다. TLS 인증서는 앱에서 SHA-256으로 고정 검증하고, API는 무작위 공유 키를 확인한다. 키와 인증서는 신뢰하는 사용자끼리 안전하게 전달해야 한다. 시범 코드는 단일 기기·단일 사용자 실험용이며 다중 사용자 격리, 키 교체, 배포 운영, 장기 연결을 제공하지 않는다.

## 설치와 연결

1. 이 브랜치에서 Android 앱을 빌드한다. 사용한 검증용 빌드는 다른 패키지 `ai.decisionos.nubi.travelpilot.networktest`로 설치했다. 기존 앱과 세션을 덮어쓰지 않는다.
2. 신뢰할 수 있는 네트워크에 중계 서버를 실행한다. `nubi-relay.py --cert <인증서 PEM> --key <개인키 PEM> --token-file <무작위 토큰 파일>`을 사용한다. 토큰은 32자 이상 영숫자·`_`·`-`여야 한다. 개인키와 토큰 파일은 소유자만 읽도록 설정한다.
3. 누비 브라우저의 **원격 연결**에 `https://서버주소:포트|토큰|인증서의 DER SHA-256 지문(소문자 64자리)`을 입력한다. PC와 태블릿이 서로 통신할 수 있어야 하며 웹뷰가 전면에 있어야 한다. 화면을 벗어나거나 연결 끊기를 누르면 수신을 중지한다.
4. 같은 서버 호스트에서 `NUBI_RELAY_URL=https://127.0.0.1:18443`, `NUBI_RELAY_TOKEN_FILE`, `NUBI_RELAY_CA_FILE`을 지정하고 `python3 opencli-nubi/nubi-relay-mcp.py`를 MCP stdio 서버로 실행한다. `nubi_remote_search`, `nubi_remote_navigate`, `nubi_remote_observe`를 호출한다. 네트워크 브라우징 자체에는 ADB가 필요하지 않다.

열기는 실제 로딩 완료가 아닌 `navigation_requested`를 반환하므로 이후 페이지가 준비된 것을 확인하고 관찰해야 한다. 앱이 중지됐거나 다른 화면으로 전환된 경우 도구는 시간 초과로 끝난다. 도메인 밖, HTTPS가 아닌 주소와 특수 문서 경로는 앱에서 거부한다. 검색 URL은 앱이 직접 생성한다. HTTPS 릴레이 외부에 공개되는 동작, WebView 페이지 신뢰성, 로그인·민감정보 및 쓰기 작업을 제품 수준에서 다루기 전에는 일반 배포하지 않는다.

## 이번 검증 상태

2026-10-31 태블릿 `HA263Q91`의 `ai.decisionos.nubi.travelpilot.networktest`에서 ADB 포워딩이 없는 상태로 MCP → TLS 중계 → 태블릿 WebView 실제 왕복을 확인했다. 설치와 페어링 화면 입력에는 ADB를 사용했다. MCP 검색어 `South Korean universities engineering`의 결과 목록에서 `Korea University` 경로를 읽고 선택한 뒤 해당 문서 본문을 관찰했다. 허용되지 않은 `https://example.com/` 이동은 거부했다. 결과 기록은 저장소 밖 `nubi-tablet-platform-audit/network-mcp-verification.json`에 있다. 현재 중계 서버는 임시 PC 프로세스이며 외부 LLM 실행이나 상시 운영을 뜻하지 않는다. Qwen의 모델 자체 MCP 호출은 별도 검증이 필요하다.

## Qwen 에이전트 연결과 실기기 검증

`opencli-nubi/qwen-tablet-agent.py`는 Azrael의 기존 Qwen 연결을 사용해 서버에 도구 목록을 전달하고, 모델이 반환한 함수 호출을 실제 MCP stdio 호출로 실행한 뒤 결과를 모델에 넘긴다. 공개 웹 콘텐츠는 비신뢰 데이터로 취급하도록 모델에 지시하며, 호출 횟수와 응답 시간을 제한한다. 실제 웹 데이터는 모델 서버에도 전송되므로 현재는 공개 위키백과로만 한정한다.

페어링된 태블릿과 TLS 중계 서버가 준비된 상태에서 다음과 같이 실행한다. 인증키와 인증서 값은 출력하거나 인자로 직접 적지 않는다.

```sh
export NUBI_RELAY_TOKEN_FILE=/안전한/경로/token
export NUBI_RELAY_CA_FILE=/안전한/경로/cert.pem
python3 opencli-nubi/qwen-tablet-agent.py '위키백과에서 대학교를 검색하고 한 문서를 읽어 요약해 줘.' --trace-file /안전한/경로/trace.json
```

2026-10-31 실기기 검증: `Qwen3.8-27B-abliterated-AWQ-W4A16`이 `nubi_remote_search` → `nubi_remote_observe` → `nubi_remote_navigate` → `nubi_remote_observe`를 직접 호출했고, 태블릿 웹뷰의 Korea University 문서를 읽어 한국어 답변과 출처 주소를 반환했다. USB 포워딩을 사용하지 않았다. 전체 응답은 모델 부하와 화면 로딩에 따라 달라진다. 전체 실행 기록은 저장소 밖 `nubi-tablet-platform-audit/qwen-tablet-mcp-trace.json`에 보관했다. 위키백과 외 사이트, 로그인·구매·발송·버튼 클릭 및 앱 백그라운드 실행은 이 실험의 지원 범위가 아니다.
