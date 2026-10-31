# Nubi UNIST OpenCLI 개발 연결

태블릿의 기존 누비 WebView에 로그인한 사용자가 포털을 연 상태에서 실행하는 읽기 전용 플러그인이다. 앱에 설치되는 MCP 서버나 UNIST 공식 API는 아니다. Android WebView 디버깅 및 ADB 권한이 필요하며 디버그 연결은 세션을 제어할 수 있으므로 신뢰하는 개발 PC에서만 일시적으로 사용한다.

```sh
opencli plugin install file:///ABSOLUTE/PATH/TO/opencli-nubi
adb shell pidof ai.decisionos.nubi.unistlive
# 출력된 PID가 예를 들어 20356일 때 (매번 확인)
adb forward tcp:19333 localabstract:webview_devtools_remote_20356
OPENCLI_CDP_ENDPOINT=http://127.0.0.1:19333 opencli nubi-unist portal-status -f json
# 앱에서 먼저 학사 메뉴를 연다
OPENCLI_CDP_ENDPOINT=http://127.0.0.1:19333 opencli nubi-unist academic-menu -f json
adb forward --remove tcp:19333
```

기기의 WebView 디버깅이 꺼져 있으면 연결되지 않는다. 세션은 기기에 남으며 새로 설치한 앱과는 공유되지 않는다. 메뉴 목록은 현재 보이는 항목만 반환한다. 사이트 레이아웃 변경, 인증 만료 또는 추가 인증은 별도 처리가 필요하다. 이 출력은 웹 UI에서 읽은 값이며 학교의 공식 데이터 API가 아니다.

로컬 MCP 클라이언트는 `node /ABSOLUTE/PATH/TO/opencli-nubi/mcp-server.mjs`를 stdio 서버로 실행하고 환경변수 `OPENCLI_BIN`에 OpenCLI의 `dist/src/main.js` 절대 경로, `OPENCLI_CDP_ENDPOINT`에 위 로컬 주소를 지정한다. `nubi_portal_status`, `nubi_academic_menu`, `nubi_naver_map_status`, `nubi_kakao_map_status`, `nubi_korail_status`를 제공한다. 각 지도·열차 명령은 해당 서비스 화면이 열린 경우 도메인·제목과 주요 표식 표시 여부를 조회한다. 장소 검색 결과 추출, 열차 조회·예약, 인증·쓰기·메일 읽기 기능은 제공하지 않는다.
