# Qwen과 누비의 네 목표 탐색

운동(fitness), 연애(love), 학점(grades), 집 사기(home)는 같은 목표 저장소와 네이티브 작업실을 사용한다. 작업실의 **Qwen에게 이 목표 탐색 맡기기**를 눌러 전용 브라우저를 열고 **Qwen 원격 연결**로 페어링한다.

Qwen은 연결된 모델 서버에서 실행된다. 태블릿 내 로컬 모델 추론이 아니다. 목표 주제와 공개 검색 결과 메타데이터가 모델 서버로 전달된다. 로그인 정보, 메일 본문, 계정 화면을 읽는 기능은 제공하지 않는다.

흐름: Qwen → stdio MCP → 로컬 HTTPS 제어 요청 → 인증·인증서 고정 HTTPS 중계 → 실제 태블릿의 전경 WebView → 고정 DOM 추출기 → Qwen → 목표별 요약 저장.

## 도구

- `nubi_goal_open`: 네 목표 중 하나를 열고 실제 목표 ID와 주제 반환.
- `nubi_goal_search`: 허용한 공급자에서 검색 시작. 결과 수신은 별도 observe가 필요하다.
- `nubi_goal_observe`: 최대 8개 실제 결과 메타데이터 또는 선택한 원문의 제목과 주소 반환.
- `nubi_goal_select`: 현재 목표의 최신 observation_id와 인덱스로 원문 탐색. 오래된 목록은 거부.
- `nubi_goal_report`: 관측한 출처만 포함하는 한국어 요약을 해당 목표에 저장.

공급자는 YouTube, 네이버 웹, 11번가, 문토, 카카오맵, 부동산 관련 네이버 검색, K-MOOC, 인프런이다. 실제 지원 범위는 기존 고정 추출기의 범위를 따른다. K-MOOC는 홈페이지 탐색이며 강좌 검색 API가 아니다. 문토는 공개 목록의 단어 필터이며 실시간 매칭·참가 확정이 아니다. 동영상·상품 본문 분석, 구매·결제·신청·메시지 전송과 백그라운드 탐색은 제공하지 않는다.

## 실행

기존 `nubi-relay*`, `qwen-tablet-agent.py`와 독립된 포트 18444를 사용한다. 인증키는 권한 600인 로컬 파일에 보관하고 Git·캡처·로그에 넣지 않는다. 중계 서버는 `nubi-goal-relay.py --cert ... --key ... --token-file ...`로 실행한다. 태블릿의 주소는 태블릿에서 접근 가능한 호스트의 네트워크 주소여야 한다. 컨트롤러 명령은 localhost만 받는다.

호스트에서 환경변수 `NUBI_GOAL_RELAY_TOKEN_FILE`, `NUBI_GOAL_RELAY_CA_FILE`을 설정한다. 필요시 `NUBI_GOAL_RELAY_URL`을 설정한다(기본 `https://127.0.0.1:18444`).

`python3 opencli-nubi/qwen-goal-agent.py --goal fitness --trace-file /absolute/local/fitness.json`

나머지는 `--goal love`, `grades`, `home`으로 순차 실행한다. 실제 브라우저는 하나이므로 병렬 실행하지 않는다. 모델은 기존 Azrael bearer-file 연결을 사용해 `Qwen3.8-27B-abliterated-AWQ-W4A16`을 요청하고 응답 모델 ID가 다른 경우 중지한다. 로그인 비밀을 채팅에 입력할 필요가 없다.

앱 화면을 벗어나거나 연결 끊기를 누르면 폴링과 늦게 도착한 결과 전달을 중단한다. 앱 재실행 후에는 명시적으로 다시 연결한다. 중계 프로세스 종료와 임시 인증키 폐기는 실행자가 담당한다. 캡처·영상·전체 모델 추적은 로컬에만 보관한다.
