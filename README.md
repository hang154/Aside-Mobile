# 누비 모바일 — 통합 비공개 저장소

현재 통합 버전은 **0.4.1-companion**이다. 0.3.2의 대화·캐릭터·사이드바·보관함 UI 안에서 기존 기능을 실행한다. 운동·연애·학점·집 사기와 기존 취업·여행 에이전트에 관련 기능을 연결했다.

- Android 앱: `mobile-aside-mvp/`
- OpenCLI/MCP·Qwen·HTTPS 릴레이: `opencli-nubi/`
- 최종 UI/목적 통합과 검증: [보고서](reports/NUBI_COMPANION_ONLY_041.md)
- 친구 계정 간 제안: [구현 범위](reports/NUBI_FRIENDS_IMPLEMENTATION.md)
- 문서 브라우저 전달: [연결 방법](docs/NUBI_CHATGPT_DOCUMENT_HANDOFF.md)
- 반응형 UI: [검증](reports/NUBI_RESPONSIVE_UI_032_VERIFICATION.md)

## 검증과 빌드

최종 실기기 목적/화면 통합 검사 132개와 기존 DB·구매 초안 등 회귀 검사 62개를 통과했다. 목표 규칙 90개와 보안 정적 검사도 통과했다. [재현 기록](reports/verification/companion-041/verification.json)에 검증 범위와 설치 APK 해시를 보관한다.

GitHub Actions의 `Build Aside Android debug APK`는 `main`과 `mobile-aside/**`의 앱 변경 시 실행되며 수동 실행도 가능하다. Java 17, Android SDK 35를 사용한다. 산출물 `Aside-Mobile-Debug-APK`에서 APK를 받는다. CI의 디버그 서명과 로컬 실기기 검증본의 서명·해시는 다를 수 있다.

## 보관 범위

소스·자동 검사·설정 예시·검증 보고서만 Git에 보관한다. 캡처·영상·계정·토큰·쿠키·메일·문서 원문·기기 DB는 로컬에 둔다. 모델 가중치와 네이티브 추론 엔진 바이너리도 Git에 포함하지 않는다. 실제 외부 서비스의 미완료 예약·결제·업로드 기능과 친구 기능의 제약은 각 보고서에 명시했다.

이 저장소는 `hang154/OpenCLI`의 `mobile-aside/mvp-android`에서 시작한 비공개 백업이다. 기존 이력과 이전 검증 보고서는 그대로 보존한다.
