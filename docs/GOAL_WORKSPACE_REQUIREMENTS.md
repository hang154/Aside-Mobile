# 누비 목표 워크스페이스 요구사항

2026-10-31 Asia/Seoul. 입력: 사용자가 첨부한 목표형 캐릭터 기획과 운동·연애·학점·집 사기 필수 요구.

공통 계약: CharacterPreset은 재사용 템플릿, Goal은 기기 소유자의 개별 목표다. 네 영역(미디어, 구매·알림, 함께하는 사람들, 캘린더·도구)은 같은 goalId를 사용한다. 첫 탭은 미디어, 이후 마지막 탭 복원. 규칙 기반 계획은 규칙 기반으로 표시한다. PC stdio MCP와 앱 저장소는 서로 다른 실행 환경이다.

구현 순서: 저장소·규칙 → 목표 홈·워크스페이스 → 기기 내 HTTPS 탐색·정규화 → Need·오퍼·구매 초안 → 일정·외부 모임 → APK·실기기 검증. 브라우저는 단일 작업·요청 ID와 목적 URL을 확인한다. 독립 공급자 실패를 다른 결과와 분리한다.

변경 소유권: 이 작업은 새 목표 관련 Java, Manifest/빌드 설정, 테스트·문서만 수정한다. 진행 중 추가된 BrowserWorkspaceActivity.java/RemoteBrowserRelay.java 및 별도 relay 작업도 보존하며, 이번 패키지는 고정한 기준 브라우저 소스로 빌드한다. 시작 시 존재한 AsideAccessibilityService.java, opencli-nubi/portal.js, mcp-server.mjs 변경은 보존하고 커밋에서 제외한다.

사용자 요구: 네 필수 목적, 쇼핑/영상·글/목표 캘린더/매칭 탐색, 외부 디자인 참고, 실제 Android 실행·배포 검증. 구매·결제·외부 게시 실행은 첨부 기획에서 제외했다. 공개 이용자 없는 커뮤니티는 빈 상태로 제공한다.

설계 결정: Java 네이티브 UI·SQLite, 별도 서버/새 프레임워크 없이 앱 내 읽기 전용 사이트 실행기를 사용한다. 개발 서명 불일치로 기존 로그인 설치를 덮어쓰지 않도록 debug만 `.goals` 접미사로 병행 설치하며 release applicationId는 보존한다. 기존 tasks DB는 v2 비파괴 마이그레이션한다.

디자인 근거: Finch의 캐릭터·작은 목표 중심 홈 https://help.finchcare.com/hc/en-us/articles/37780000231309-Exploring-the-Finch-Home-Page , Habitica의 아바타·행동 목록 https://habitica.com/static/features , Android의 주 내비게이션과 형제 탭 https://developer.android.com/design/ui/mobile/guides/layout-and-content/layout-and-nav-patterns . 원본 자산을 복제하지 않고 네 색의 누비 캐릭터를 Canvas로 직접 그린다.

세부 요구→파일→검증 매핑과 실제 지원 범위는 구현 후 이 문서 및 reports/GOAL_WORKSPACE_IMPLEMENTATION_REPORT.md에 기록한다.

## 요구사항 추적

- T01/T15 · GoalStore / GoalHomeActivity / CharacterWorkspaceActivity: 운동·연애·학점·집 사기 및 취업·여행이 공통 저장소와 화면을 사용한다. 강제 종료 후 복원과 실기기 DB 격리를 검증한다.
- T02 · GoalRules / TestGoalRules / 워크스페이스 설정: 자극·정보가 검색어를 바꾸고 둘 다 OFF이면 탐색을 중지한다. 뉴스 최신성·언어는 공급자 파라미터에 반영한다.
- T03/T04 · MediaRepository / GoalDiscoveryActivity / goal_extract.js: 뉴스와 영상·채널을 구분하고 제목·출처·확인 시각·추천 이유를 저장한다. 링크 카드가 원문으로 이어진다. provider 실패는 다른 결과를 제거하지 않는다. 전체 영상 내용 분류·다중 플랫폼 API 권한 확보·무한 페이지네이션은 완료 범위가 아니다.
- T05 · CharacterWorkspaceActivity.needDraft/commerce/checkout: 콘텐츠 또는 직접 확인 → Need → 상품 후보 → 주문 초안 → 정확한 판매처 HTTPS 상품 페이지 → 같은 목표로 복귀. 옵션·총액 미확인 상태를 유지한다.
- T06/T07 · GoalRules 및 오퍼 카드: 배송비 미상/0원/옵션 차이/가격 overflow 테스트. 검증되지 않은 총액을 순위에 쓰지 않는다. 제품 동일성 판정과 두 판매처의 최종 조건 검증은 라이브로 완료하지 못했다. 모든 라이브 후보는 대체 후보로 구분한다.
- T08 · 구매 의도 저장: 멱등 키·오퍼 스냅샷·handed_off/self_reported 분리. 실제 주문 제출·결제 승인 실행 없음. 공식 주문 결과를 확인하는 provider가 없어 verified 구매는 생성하지 않는다. 가격 변경 재승인 규칙은 순수 로직 테스트이며 실제 주문 API E2E는 미실행이다.
- T09 · alerts: 기본 OFF, manual_only 조건 저장·삭제·목표 삭제 cascade. 자동 가격 감시·푸시·조용한 시간 실행은 미지원.
- T10 · people / profiles: 누비 이용자 목록은 빈 상태. 프로필은 본인 로컬 초안이고 외부 공개되지 않는다. 문토·Meetup 공개 모임 탐색을 제공한다. 서버 두 계정 권한·신고·실시간 매칭은 미구현이다.
- T11 · TaskStore / GoalInstrumentation: aside_tasks.db v1→v2 ALTER TABLE. 기존 ID·제목 보존 및 goal_id NULL 검증. 기존 학사·포털·메일 도구는 CampusToolsActivity로 보존한다. 메일 읽기·기차 예약을 새 완료 기능으로 주장하지 않는다.
- T12/T14 · 기본 Manifest에는 접근성/수집 서비스 없음. experimental Manifest에만 선언. 새 브라우저는 JS 네이티브 브리지 없음, HTTPS/도메인 제한, 페이지 세대와 쿼리·선택 스냅샷 검증. 기존 사용자 접근성 소스는 미수정.
- T13 · DiscoveryProviders.searchMatches / GoalDiscoveryActivity: 공급자와 검색어가 다르면 결과 읽기 거부. 세대가 달라진 목록 선택도 거부. URL·동일성 규칙과 추출기 계약 테스트를 분리해 실행한다.
- T16 · GoalUi: 작은 화면은 하단 내비게이션, 태블릿은 레일과 제한 폭 본문. 화면 회전·작은 화면·큰 글꼴 검사 범위는 최종 실행 보고서에 기록한다.

일반 사용자 런타임에는 ADB·PC MCP 설치가 필요 없다. ADB는 개발자의 설치·캡처·계약/실기기 검증에만 사용한다. 기존 PC MCP와 앱 저장소가 자동 동기화된다는 주장은 하지 않는다.
