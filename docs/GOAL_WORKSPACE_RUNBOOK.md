# 목표형 누비 실행·빌드

Java 17 이상, Android SDK 35, Gradle 8.10.2 이상이 필요하다. 루트에서 작업할 때 `gradle -p mobile-aside-mvp`를 사용한다. 기존 워크플로는 Android ARM64 llama.cpp b12000 라이브러리와 체크섬을 내려받는다. GGUF 모델 파일은 APK에 포함하지 않는다. 새 핵심 워크스페이스는 모델 없이 규칙 기반으로 동작한다.

```sh
cd mobile-aside-mvp
bash scripts/test_parser.sh
bash scripts/test_actions.sh
bash scripts/test_concert.sh
bash scripts/test_campus.sh
bash scripts/test_goals.sh
node scripts/test_goal_extractors.mjs
python3 scripts/test_static.py
python3 scripts/test_collector.py
python3 scripts/test_goal_security.py
gradle --no-daemon :app:assembleDebug :app:assembleDebugAndroidTest :app:assembleRelease
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb shell am instrument -w ai.decisionos.nubi.travelpilot.goals.test/ai.decisionos.aside.GoalInstrumentation
adb shell am start -n ai.decisionos.nubi.travelpilot.goals/ai.decisionos.aside.CampusActivity
```

Debug는 ai.decisionos.nubi.travelpilot.goals에 병행 설치한다. 과거 GitHub Actions 서명으로 설치된 travelpilot의 로그인·데이터를 보존한다. Release는 기존 applicationId를 유지하며 현재 출력은 unsigned다. 안정적인 배포 서명은 별도로 관리해야 한다. production 서명 키를 저장소에 올리지 않는다. experimental 빌드만 개발용 접근성·수집 서비스를 포함한다.

사용 순서: 홈에서 누비 선택 → 제목·주제·선택 예산 → 미디어 기본 탭 → 실제 YouTube/뉴스 조회 → 콘텐츠 저장 또는 일정 초안 확인 → 준비물 필요 확인 → 11번가 등 공급자의 실제 목록 읽기 → 후보 담기 → 주문 초안 확인 → 원본 상품에서 구매 계속하기. 실제 구매·결제는 이번 검증에서 실행하지 않는다. 함께하는 사람들에서는 공개된 누비 사용자가 없다는 안내와 외부 모임 탐색을 제공한다.

TaskStore는 기존 aside_tasks.db를 비파괴 마이그레이션한다. DB는 앱별 Android sandbox 안에 있고, 서로 다른 applicationId 간에 로그인·기록을 임의 복사하지 않는다. 새 앱으로 기존 설치 데이터가 자동 이전됐다고 해석하지 않는다.

`verify_goal_artifacts.py --apk /abs/app.apk`는 소스·패키지의 byte hash 및 기준 커밋 비교를 생성한다. 이는 기능 테스트 결과를 대신하지 않는다. 테스트용 기기 화면 스크립트는 별도 로컬 캡처 폴더에서 실행하며 스크린샷·영상·실사용자 기록을 Git에 올리지 않는다.
