# 태블릿 상위 플랫폼 MCP 실험 — 2026-10-31

- 대상: Semrush 2026년 9월 국가별 웹 방문 추정 상위 20개씩의 중복 제거 33개 도메인. 국적별 이용자나 앱 이용 순위가 아니다.
- 실행: PC의 MCP stdio 서버 → OpenCLI → USB ADB 포워딩 → 태블릿 누비 WebView의 CDP. MCP 서버 자체가 태블릿 네이티브에서 실행되는 것은 아니다.
- `loaded`는 페이지가 열렸다는 뜻이며 기능이나 로그인 성공은 아니다. 아래 검색 결과는 고정된 공개 검색어를 사용한 실험이며, `opened`는 URL 경로와 본문 길이 확인만으로 판정하므로 실제 상세 콘텐츠의 품질을 보장하지 않는다. 위키백과처럼 검색어와 무관한 링크를 고를 수 있다.
- 일부 플랫폼은 선택자가 없거나 공개 검색이 제한되어 있고, 목록과 본문을 안정적으로 추출하는 서비스 전용 어댑터가 추가로 필요하다. 결제·발송·가입은 실행하지 않았다. 전체 33개 서비스의 핵심 기능이 구현된 상태가 아니다.
- 기록에는 게시물 원문이나 성인 콘텐츠를 포함하지 않았다. 로컬 실행 상세: `nubi-tablet-platform-audit/results.json`, `feature-results.json`, `feature-retest.json` (저장소 밖).

| 도메인 | 첫 접속 | 검색·탐색 실험 | 결과 후보 | 상세 경로 진입* |
|---|---|---|---:|---|
| youtube.com | loaded | results_found | 5 | 예 |
| google.com | loaded | no_results | 0 | 미확인 |
| naver.com | navigation_error | no_results | 0 | 미확인 |
| chatgpt.com | loaded | unsupported | 0 | 미확인 |
| x.com | loaded | no_results | 0 | 미확인 |
| instagram.com | loaded | no_results | 0 | 미확인 |
| missav123.com | navigation_error | unsupported | 0 | 미확인 |
| facebook.com | loaded | no_results | 0 | 미확인 |
| yasyadong02.tv | navigation_error | unsupported | 0 | 미확인 |
| weather.com | loaded | no_results | 0 | 미확인 |
| msn.com | loaded | no_results | 0 | 미확인 |
| newtoki1.org | loaded | unsupported | 0 | 미확인 |
| tistory.com | loaded | no_results | 0 | 미확인 |
| av19t.com | loaded | unsupported | 0 | 미확인 |
| inven.co.kr | loaded | results_found | 4 | 미확인 |
| kissjav.li | navigation_error | unsupported | 0 | 미확인 |
| abr.ge | timeout_or_external_redirect | unsupported | 0 | 미확인 |
| avsee.is | navigation_error | unsupported | 0 | 미확인 |
| tvmon1.com | loaded | unsupported | 0 | 미확인 |
| aliexpress.com | loaded | results_found | 5 | 예 |
| reddit.com | loaded | results_found | 5 | 예 |
| amazon.com | loaded | results_found | 5 | 예 |
| yahoo.com | loaded | no_results | 0 | 미확인 |
| wikipedia.org | loaded | results_found | 5 | 예 |
| duckduckgo.com | loaded | no_results | 0 | 미확인 |
| xvideos.com | navigation_error | unsupported | 0 | 미확인 |
| pornhub.com | navigation_error | unsupported | 0 | 미확인 |
| bing.com | loaded | results_found | 1 | 미확인 |
| tiktok.com | loaded | no_results | 0 | 미확인 |
| walmart.com | loaded | results_found | 5 | 예 |
| temu.com | loaded | timeout_or_external_redirect | 0 | 미확인 |
| espn.com | loaded | results_found | 5 | 예 |
| linkedin.com | loaded | no_results | 0 | 미확인 |

* 상세 경로 진입은 관련성과 내용의 정확성을 검증한 결과가 아니다. `no_results`는 검색 결과가 실제로 없다는 뜻이 아니라 현재 선택자·로딩·접근 조건에서 추출하지 못했다는 뜻이다. `unsupported`는 탐색 명령을 아직 구현하지 않은 도메인이다.

## 다음 구현 과제

- 검색 플랫폼별 DOM을 실제 화면과 대조해 관련 결과를 추출하고, 외부 결과 링크와 로그인 상태를 안전하게 처리한다.
- 결과 제목·식별자와 상세 페이지를 대조해 메뉴나 관계없는 글이 성공으로 계산되지 않도록 한다.
- SNS별 검색·게시물 상세 조회, 뉴스 기사 조회, 쇼핑 상품 상세, 날씨 예보, 구인 공고 상세를 각각 검증한다.
- 지원하지 않는 서비스와 접근 오류는 사용자에게 그대로 표시한다.
