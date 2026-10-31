# 누비 0.2.1 · 재현 결함 세 건 수정

2026-10-31 Asia/Seoul. 수정 기준 f7d78f6084e204ece367285460343d2ea6c35574. 기존 검토의 결함 재현은 ../nubi-implementation-review/REVIEW.md에 보존했다. 이번 변경은 그 세 건을 해결하며 통합 가격 비교·실시간 매칭·자동 가격 감시의 신규 구현을 포함하지 않는다.

## 수정

R1 구매 초안: draft/awaiting_confirmation 상태는 같은 레코드·멱등 키로 다시 확인한다. 취소·뒤로·바깥 터치 닫기는 dismiss 처리에서 draft로 복원한다. 초안 카드에 다시 확인 동작을 제공하고, 이미 판매처로 이동한 상태와 확인창이 열려 있는 동안의 중복 입력은 차단한다. 저장된 awaiting_confirmation 상태도 Activity를 다시 열어 재개하는 것을 검증했다. 실제 프로세스 강제 종료 E2E를 수행했다는 의미는 아니다. 상품 조건을 다시 읽었으면 현재 오퍼의 확인창을 새로 연다. 실제 주문은 실행하지 않는다.

R2 상품 식별: 모든 쿼리를 삭제하던 코드를 제거했다. 쿠팡 itemId/vendorItemId 및 그 밖의 옵션 파라미터를 보존하고 알려진 추적 키만 제거한다. 같은 productId의 서로 다른 옵션은 별도 URL/후보로 남는다. 11번가 prdNo 형식은 정확한 HTTPS 상품 경로로 변환하며 상품 ID가 없는 항목은 제외한다. 외부 호스트를 공급자 상품으로 읽지 않는다. 이 경로는 DOM fixture 검사이며 쿠팡의 라이브 옵션·결제 검증은 아니다.

R3 저장 목록: 목표 전체 저장 콘텐츠는 검색어에 상관없이 조회한다. 발견 피드는 기존 검색어를 유지한다. 저장/숨김 필터를 표시 상한 200개보다 먼저 적용해 최근 조회 항목 205개보다 오래된 저장 콘텐츠도 표시되는 것을 검증했다. 전체 무한 페이지네이션이나 검색 인덱스 추가는 범위가 아니다.

## 검증

- 기존 파서 17 / 행동 13 / 콘서트 6 / 캠퍼스 17 / 목표 규칙 90: 143개 통과.
- 추출기 계약: 기존 14 + 추가 10 = 24개 통과. 옵션 분리·판매자 식별·추적 URL 중복 제거·11번가 쿼리 ID 복원·식별자 미상/외부 호스트 거부를 포함한다.
- 실기기 DB·화면 흐름: 기존 15 + 추가 16 = 31개 통과. 취소 재시도·뒤로 재시도·같은 멱등 키 재사용·중복 입력·Activity 재시작 후 초안 재개·다른 검색의 저장 콘텐츠 표시·숨김·상한 이전 필터를 포함한다.
- 총 개별 검사 198개 통과. 정적 보안·수집 경계·일반 Manifest 검사 3종도 통과.
- debug / androidTest / unsigned release 빌드 통과. CI에 테스트 APK 컴파일을 추가했다. 실기기 검사는 USB Lenovo Android 16 ARM64에서 수행했다.
- 패키징한 Manifest에 service가 없고 native 라이브러리 22개가 이전 배포본과 byte 단위로 동일하다. APK 엔트리 증감 없이 Manifest·classes2.dex·goal_extract.js만 바뀌었다.
- 실제 설치된 base.apk와 배포용 파일의 byte 동일성을 확인했다. 기존 목표·로그인 데이터는 유지했으며, 테스트 APK와 테스트 목표는 제거했다.

로컬 로그는 ../nubi-goal-workspace-release-0.2.1/regression-tests.log 및 device-flow-tests.log다. 로그 사본은 reports/goal-workspace-0.2.1/test-results.txt에도 둔다. 영상은 ../nubi-goal-fix-captures/purchase-saved-regression.mp4에 로컬로만 보관했다. 영상은 검증 중 실제 화면 녹화이며 연출·기능 소개 편집본은 아니다. 사용자 세션·캡처·영상을 GitHub에 업로드하지 않는다.

## 패키지

로컬: ../nubi-goal-workspace-release-0.2.1/nubi-goals-0.2.1.apk

package ai.decisionos.nubi.travelpilot.goals / versionCode 20 / versionName 0.2.1-goal-workspace.

83,671,747 bytes. SHA-256: 0521a8456a89a30a64e89ab7636b111565408c511bc2618b3860eae9dc497e57.

비공개 테스트 릴리스 nubi-goals-v0.2.1에 동일 APK와 SHA256SUMS를 제공한다. 개발 서명이며 Play 운영 출시·심사 완료가 아니다. 0.2.0 APK는 덮어쓰지 않고 보존했다.

기존 배포와 동일하게 8d6871e의 브라우저/접근성 소스와 이번 소유 입력 24개를 별도 frozen-source에 고정했다. 공유 작업 트리에서 진행 중인 브라우저 relay·접근성·OpenCLI 변경은 보존하며 패키지에서 제외했다. 고정 입력과 현재 소유 소스의 해시는 일치한다. 신규 해시 JSON·CSV는 verify_goal_artifacts.py --base f7d78f6 --out reports/goal-workspace-0.2.1로 생성했다. byte 해시는 기능 검증을 대신하지 않는다.

미검증 범위: 쿠팡 라이브 옵션, 실제 주문·결제, 작은 휴대폰/큰 글꼴/회전/오프라인 전체 E2E, 모든 외부 공급자의 네 목표 전체 재실행. 이번 변경의 영향받지 않은 외부 사이트 검증은 이전 실행 근거와 구분한다. 여러 판매처의 확정 총액 비교, 누비 다중 사용자 매칭, 자동 가격 감시는 기존 미완료 상태를 유지한다.
