# 누비 0.3.1 로그인 후 UI 반영과 검증

2026-11-01, 코드 2becd7e. Lenovo TB375FC Android 16 USB 실기기. Pickle은 설치된 com.pickle.client를 사용했고 사용자가 로그인했다. 기본 채팅·둘러보기·보관함·나의 피클의 화면을 직접 확인하여 로컬 reference에 기록했다.

## 변경
태블릿 왼쪽 고정 메뉴, 중앙 캐릭터와 작은 이름 선택, 넓은 입력창, 말풍선, 카테고리 필터와 추천 목록, 보관함 세그먼트를 구현했다. 네 목적별 누비, 검색/문서/저장 콘텐츠/학교 도구와 실제 연결했다. 테스트 목적이 기본 대화로 선택되는 문제를 피하도록 QWEN_/INSTRUMENTATION 제목을 기본 선택에서 제외했다. 캐릭터·문구는 누비 자체 자산이다. assistant-ui의 대화·도구·파일 구성을 네이티브로 구현하며 해당 React 패키지나 Pickle 코드는 포함하지 않는다.

## 검증 결과
- 최종 APK assembleDebug 및 assembleDebugAndroidTest 성공.
- 실기기 데이터와 흐름 검사 61개 통과.
- 정적 검사 3종 통과. GitHub CI에서 규칙/fixture 173개와 APK 빌드 통과: https://github.com/hang154/Aside-Mobile-Backup/actions/runs/41281022304
- 실기기 UI 조작 11개 경로 통과: 둘러보기, 학점 필터, 보관함, 미디어, 실행 기록, 나의 누비, 목적별 누비, 기본 채팅 복귀, 운동 선택, 메뉴 접기/펼치기.
- 답변 출처 카드 전체를 눌러 앱 내부 YouTube 원문 브라우저가 열리는 것 확인.
- 네 목표의 실제 입력창/전송 버튼 → Qwen → MCP → 실제 기기 WebView → 원문 제목 확인 → 답변 저장 통과. 운동 32.4초, 연애 26.3초, 학점 32.5초, 집 사기 24.2초.
- 네 실행 trace completed=true 및 reported_models 전부 Qwen3.8-27B-abliterated-AWQ-W4A16 확인. 27B는 호스트에서 실행하며 기기 내 추론이 아니다.
- versionCode 31 / 0.3.1-companion. 로컬/설치 APK SHA-256: a492783edf6b3b678aafe886d7184ca624697d015ea7cba994ccacd45e822689.

## 증거
로컬 `/home/user-btc/다운로드/usf/nubi-pickle-ui-0.3.1/`: reference(원본 앱 화면), build-final.log, native.log, live.jsonl, tour.log, verification(목적별 결과, 메뉴 화면, flow-summary.json, model-summary.json, 원본 모델 trace).

`verification/누비_태블릿_UI_조작.mp4`: 약 76.6초 조작 녹화 원본. 컷 편집본이 아니다. 이 영상과 캡처·제삼자 APK는 GitHub에 올리지 않는다.

## 완료 범위와 차이
관찰한 주요 화면 배치와 누비의 목적별 탐색 사용 흐름을 구현·검증했다. 모든 Pickle 기능이나 픽셀 단위 동일성의 검증이 아니다. 친구 간 에이전트 대화·초대·전화·결제·사용량 티켓·모든 서비스 로그인 연결은 동등하게 구현되지 않았다. 친구 메뉴 대신 목적별 누비를 배치했다. 답변은 Qwen의 실제 탐색 결과이며 Pickle의 응답 내용·추천 품질·지연 시간과 같음을 보장하지 않는다. 전체 사용자 경험 동등성은 미달이다.
