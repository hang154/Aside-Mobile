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

로컬 MCP 클라이언트는 `node /ABSOLUTE/PATH/TO/opencli-nubi/mcp-server.mjs`를 stdio 서버로 실행하고 환경변수 `OPENCLI_BIN`에 OpenCLI의 `dist/src/main.js` 절대 경로, `OPENCLI_CDP_ENDPOINT`에 위 로컬 주소를 지정한다. `nubi_portal_status`, `nubi_academic_menu`, `nubi_naver_map_status`, `nubi_kakao_map_status`, `nubi_korail_status`를 제공한다. 각 지도·열차 명령은 해당 서비스 화면이 열린 경우 도메인·제목과 주요 표식 표시 여부를 조회한다. 지도 검색 결과 추출은 아래 조회 도구를 참고한다. 열차 예약, 인증·쓰기·메일 읽기 기능은 제공하지 않는다.

## 조회 도구

- `nubi_naver_search({"query":"UNIST"})`: 누비 WebView에서 네이버 지도를 열고 장소명·분류·주소 선택지를 반환한다. `nubi_naver_places({})`는 현재 결과를 다시 읽는다.
- `nubi_kakao_search({"query":"UNIST"})`: 모바일 카카오맵 결과 목록을 열어 장소 선택지를 반환한다. `nubi_kakao_places({})`는 현재 결과를 읽는다.
- `nubi_unist_calendar({})`: UNIST 공식 학사일정의 앞으로 60일을 읽는다. 브라우저는 필요 없다.
- `nubi_papers_search({"query":"machine learning"})`: OpenCLI arXiv 검색으로 논문의 제목·저자·날짜·원문을 반환한다. 브라우저는 필요 없다.
- `nubi_korail_options({})`: 열려 있는 코레일의 열차 행 또는 제한 상태를 읽는다. 2026-10-31 실기기 조회는 코레일이 `-8002` 제한을 반환했으며, 열차 행 추출은 실결과로 검증하지 못했다.

지도 결과는 페이지에서 현재 노출된 항목이며 공급자의 공식 API 결과가 아니다. 페이지 구조나 접속 제한으로 실패할 수 있고 반환 번호는 현재 목록의 순서로, 다른 검색 뒤에는 다시 사용하면 안 된다. 화면 선택·예약·결제는 구현되지 않았다. 검색어는 브라우저 화면과 해당 사이트로 전달된다. 날짜와 주소 등은 원문에서 재확인한다.
- `nubi_weather_forecast({"location":"Ulsan"})`: wttr.in의 최대 3일 예보와 요청 위치·조회 시각을 반환한다. 반환되는 위치는 사용자가 입력한 값이므로 정확한 지점의 예보인지는 원문에서 확인한다.
