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

## 추가 시나리오: 선택과 저장

- `nubi_jobs_list({})`는 UNIST 인공지능대학원 채용 게시판의 현재 첫 페이지를 반환한다. `nubi_jobs_detail({"index":1,"title":"목록에서 받은 정확한 제목"})`는 목록을 다시 불러와 순서와 제목이 일치할 때만 본문을 반환한다. 마감과 지원 조건은 원문에서 확인한다.
- `nubi_dining_list({})`는 UNIST 공식 편의시설 페이지의 세 식당 위치·게시된 운영시간을 제공한다. 당일 메뉴·임시 휴무·오늘 실제 영업 상태는 제공하지 않는다.
- `nubi_clubs_list({})`는 UNIST 컴퓨터공학과 공식 동아리 소개를 제공한다. 전체 동아리나 현재 모집 여부는 제공하지 않는다.
- `nubi_shopping_search({"query":"초콜릿"})`는 누비 WebView의 네이버 모바일 가격비교에서 상품명·표시 가격·배송비·광고 여부를 읽는다. `nubi_shopping_select({"index":1,"title":"목록에서 받은 정확한 상품명"})`는 현재 목록과 일치할 때만 해당 상품을 반환한다. 표시 가격은 최종 결제금액이 아니며 회원·옵션·쿠폰·배송 조건을 원문에서 확인한다. 상품 상세 페이지 이동과 주문은 구현되지 않았다.
- `nubi_save_choice({"kind":"job","title":"선택한 공고 제목","url":"선택한 공식 출처 URL"})`와 `nubi_saved_choices({})`는 PC의 `~/.local/share/nubi-mcp/choices.json`에 선택 결과를 저장·조회한다. 테스트에서는 `NUBI_CHOICES_FILE`로 경로를 바꿀 수 있다. 이 저장소는 안드로이드 앱의 할 일 DB와 별개다. 저장은 원문을 보내거나 신청하지 않는다.

2026-10-31 실기기에서 네이버 쇼핑 10개 항목과 선택 결과, 공개 채용 공고 10건과 첫 공고 본문, 식당 3곳, 컴퓨터공학과 동아리 1건을 조회했다. 각 종류의 선택 저장과 재조회 및 변경된 공고 제목 거절을 시험했다. 로그인·메일 본문은 이 저장소에 저장하지 않았다.

## 외부 채용 플랫폼

- `nubi_saramin_search({"query":"데이터 분석 인턴"})`는 사람인 웹 검색 결과의 공고 ID·제목·기업·조건·마감을 반환한다. `nubi_saramin_detail({"id":"목록 ID","title":"목록 제목"})`은 선택 공고를 열고 핵심 정보를 읽는다. 상세 요강이 이미지나 별도 프레임에 있으면 빠질 수 있으므로 원문을 확인한다.
- `nubi_wanted_search({"query":"데이터 분석"})`와 `nubi_wanted_detail({"id":"목록 ID","title":"목록 제목"})`은 원티드 검색·상세를 연다. 원티드 검색 화면에는 검색어와 관련된 추천 공고가 섞여 있어 반환 행에 이를 표시한다.
- 두 서비스 모두 사용자가 선택한 공고를 `nubi_save_choice`에 `kind: "job"`과 반환된 URL로 넘겨 PC 로컬 저장소에 보관할 수 있다. 제출·지원은 하지 않는다. 브라우저 DOM이 바뀌거나 서비스의 접속 제한이 있으면 동작하지 않을 수 있다. 공식 API를 사용한 연동은 아니다.
- 2026-10-31 실기기 MCP 시험에서 사람인 검색 20건·선택 공고의 핵심 정보, 원티드 검색 12건·선택 공고의 본문을 확인했고 각 선택의 저장·재조회를 통과했다. 표시된 정보의 적합성·마감은 원문에서 다시 확인한다.

## 숙소와 연구 외부 플랫폼

- `nubi_booking_search({"destination":"Busan","checkin":"2026-11-14","checkout":"2026-11-15","adults":2})`는 Booking.com 모바일 결과에서 숙소·위치·표시 요금·세금 안내·후기·광고 여부를 반환한다. 객실 1개, 아동 0명 기준이다. `nubi_booking_select({"index":1,"title":"목록의 숙소명"})`은 현재 목록과 이름이 일치할 때만 선택한다. `nubi_save_choice`에 `kind: "hotel"`과 반환 URL을 넘겨 PC에 저장할 수 있다. 예약·결제는 수행하지 않는다.
- `nubi_openalex_search({"query":"battery recycling"})`는 OpenAlex 저작물 10건을 반환한다. `nubi_openalex_detail({"id":"W..."})`은 해당 저작물의 서지 정보와 제공되는 초록을 읽는다. 논문·리뷰·책 등이 섞일 수 있으며 동료심사 여부는 원문에서 확인한다. `kind: "paper"`로 선택을 저장할 수 있다.
- 2026-10-31 MCP 경유 태블릿에서 부산 11/14~15 성인 2명 숙소 20건, 서울 11/21~22 성인 1명 숙소 20건을 각각 확인했다. 부산 숙소 선택과 저장·재조회도 확인했다. 요금은 조건·조회 시각에 따라 달라지며 세금·취소·최종 결제액은 원문에서 확인한다. 숙소는 공개 웹 화면을 읽으므로 구조 변경과 접근 제한에 영향을 받는다.
- OpenAlex 배터리 재활용 검색 10건, 첫 항목 상세·초록과 저장·재조회를 확인했다. 공지·축제·공연 등의 모든 외부 연동을 완료한 것은 아니다.

## 상위 웹사이트 목록과 공개 탐색

- `nubi_top_sites({"country":"KR"})`, `nubi_top_sites({"country":"US"})`: Semrush의 **2026년 9월 스냅샷** 각 20개. 자동 갱신되지 않는다.
- `nubi_platform_probe({"domain":"youtube.com"})`: 스냅샷에 있는 도메인의 HTTPS HEAD 응답과 설치된 OpenCLI 읽기 명령을 반환한다. 읽기 명령 목록은 설치 여부만 나타내며 실행 성공을 뜻하지 않는다.
- `nubi_platform_preview({"domain":"youtube.com"})`: 공개 홈페이지 GET 상태, 제한된 HTML의 제목과 같은 사이트의 링크 최대 5개를 반환한다. 등록된 33개 도메인만 허용하고 외부 도메인으로의 리디렉션은 따라가지 않는다. 개인 세션을 사용하지 않으며 성인 사이트의 본문 미리보기는 제외한다.
- `nubi_web_discover({"provider":"wikipedia","query":"UNIST"})`: Wikipedia 문서 검색. 제공자는 `wikipedia`, `google_news`, `google_suggest`, `duckduckgo_suggest`다. 두 suggest는 자동완성 제안이며 문서 검색이 아니다.

각국 순위·33개 도메인의 실제 응답 및 명령 목록은 [점검 보고서](../docs/TOP_WEB_PLATFORMS_2026_09.md)를 참조한다. 국가별 방문량은 국적별 사용자 수나 앱 사용량이 아니다. 공개 페이지의 200 응답은 로그인, 검색, 해당 플랫폼의 서비스 기능이 정상 동작한다는 의미가 아니다.


### 0.6.13 campus execution boundaries

- Group chat can delegate public research to the existing Qwen/MCP foreground browser. Commands carry device, request and job ownership; cancellation revokes that lease. Observed result links return to the group thread. This is not authenticated school-account automation.
- First launcher entry offers portal sign-in. App WebViews preserve the same cookie profile. Blackboard and UNIST's email SSO gateway are probed silently; separate Blackboard/mail credential forms are not shown. A school session can expire or require MFA, so one initial login cannot guarantee permanent authentication. Other APK package profiles are not imported.
- Campus tasks now use the current groupchat package and installed ADB rather than a deleted build path. `NUBI_ANDROID_PACKAGE` and `NUBI_ADB` can override these. Exactly one non-home WebView must be selected; ambiguous targets fail closed.
- `campus-blackboard-mcp.py` reads visible authenticated courses/activity/attachment links and downloads a currently observed same-origin PDF. It never submits assignments, reads hidden grades, or assumes an empty DOM means no assignments.
- `nubi_lecture_pdf_translate` creates local PDF + DOCX using actual Qwen translations. Original PDF visual pages are retained and compared, followed by Korean pages. Scans require OCR; Drive upload and semantic correctness still need separate verification. Source file must be in the configured lecture folder.
- `nubi_campus_mail_prepare_send` stages an existing Graph draft. Only the native school chat review dialog can request send after human confirmation. Approval binds recipients, body and attachment bytes. Changed content invalidates approval; ambiguous send is never automatically retried. Graph `202` means accepted, not delivered. Requires configured delegated Graph credentials with Mail.ReadWrite and Mail.Send; a WebView login alone does not grant Graph permissions.
- Four-answer comparison uses actual configured provider slots. Missing GPT/Claude/Gemini accounts remain `not_connected`, never substituted with Qwen. Optional provider mapping: `~/.local/state/nubi-ai-compare/providers.json` contains service keys with existing Azrael `connection_id` and exact `model` values, never inline credentials.
- Install tested Python dependencies with `requirements-campus.txt` in an isolated environment; the existing document venv is preferred for campus jobs. Backend mail OAuth also requires MSAL. Do not commit tokens, job contents from real accounts, captures or videos.

The 414 source checklist entries and current limitations are tracked in `reports/checklist/requirements.json`. Code/fixture success is not a claim of live school-account or booking completion.
