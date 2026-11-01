# 누비 캐릭터 대화 UI 실기기 검증

검증일: 2026-11-01. 코드: 02beb6d. APK: versionCode 30 / 0.3.0-companion. 기기: Lenovo TB375FC / Android 16.

## 결과
- APK 빌드 및 태블릿 업데이트 설치 성공.
- 실기기 DB·화면 흐름 검사 61개 통과. 새 화면 초안 유지, 목표별 문서, 탭 전환, WebView 유지 포함.
- 명령·행동·콘서트·캠퍼스·목표 규칙 143개, 추출기 fixture 30개 통과. 정적 검사 3종 통과.
- 네 목표의 실제 입력창→전송 버튼→Qwen→MCP→태블릿 WebView→답변 저장 경로 모두 통과.
- 로컬 APK와 설치된 APK SHA-256 동일: `2bcc9854b904f4eb16c400efd718c5bf03f30686e69ff0006ebeece12a503bf0`.

## 실제 탐색
운동 29.1초: YouTube 초보자 스트레칭, 8개 선택지, 원문 제목 확인, 2개 출처 반환.

연애 26.2초: 네이버 공개 웹 부산 비 오는 날 실내 데이트, 8개 선택지, 원문 제목 확인, 2개 출처 반환.

학점 30.5초: 파이썬 입문 자료, 6개 선택지, 원문 2회 열기, 제목 확인, 2개 출처 반환.

집 사기 27.2초: YouTube 내 집 마련 준비, 8개 선택지, 원문 제목 확인, 2개 출처 반환.

네 실행의 요청 모델과 응답 reported_models 모두 `Qwen3.8-27B-abliterated-AWQ-W4A16`. 각 서버 trace의 completed=true 확인. 모델은 호스트에서 실행하며 태블릿 자체 27B 추론을 뜻하지 않는다. 영상 내용 해석, 투자 조언 정확성, 실제 구매·예약·계약 성공의 검증이 아니다.

## Pickle 조사
Aurora Store의 Google Play 경로에서 com.pickle.client 설치·실행 확인. 로그인 화면까지 직접 확인했고 로그인 이후 내부 화면은 미확인. Aurora REQUEST_INSTALL_PACKAGES는 설치 후 ignore로 복구했다. 공개 스토어 및 공식 사이트 UI를 참고하여 자체 Java/Canvas로 구현했다. assistant-ui React 실행환경이나 Pickle 앱 코드를 이식하지 않았다.

## 로컬 증거와 남은 확인
`/home/user-btc/다운로드/usf/nubi-pickle-ui-0.3.0/`에 APK, 빌드 로그, native-checks.log, live-runs.jsonl, verification/*-chat.png, flow-summary.json, model-summary.json, 서버 trace 보관. 캡처·영상·제삼자 APK는 GitHub에 올리지 않는다.

실기기 자동 탭 검사는 통과했다. 별도 수동 소개 투어는 기기가 Pickle 인증 화면으로 전환되어 중지했으며 인증 중 녹화도 중단했다. 기기 사용 가능 응답을 받은 뒤 수동 메뉴 투어와 소개 영상 촬영을 이어간다. 기존 가격 비교·결제·매칭 등의 미완료 기능은 이번 UI 업데이트의 완료 범위에 포함하지 않는다.
