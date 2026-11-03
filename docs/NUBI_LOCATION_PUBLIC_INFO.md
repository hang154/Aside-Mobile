# 누비 위치·택시·공공정보 연동

교통 MCP와 HTTP 서버에서 카카오 장소 검색·길찾기, 한국관광공사 관광검색, 기상청 초단기실황, 에어코리아 대기질을 조회한다. 키는 모바일 앱이나 응답에 포함하지 않고 서버의 권한 600 파일에서 읽는다. 기본 경로는 `~/.local/state/nubi-transit/kakao.key`, `tago.key`이며 `NUBI_KAKAO_KEY_FILE`, `NUBI_TAGO_KEY_FILE`로 변경할 수 있다. 컨테이너는 비밀 파일을 읽기 전용으로 마운트하고 비루트 사용자에게 읽기 권한을 제공해야 한다.

HTTP는 `/v1/places/search`, `/v1/taxi/estimate`, `/v1/tourism/search`, `/v1/weather/now`, `/v1/air/quality`; MCP는 `nubi_transit_place_search`, `nubi_transit_taxi_estimate`, `nubi_transit_tourism_search`, `nubi_transit_weather_now`, `nubi_transit_air_quality`를 제공한다. 장소가 정확히 확인되지 않으면 후보를 반환한다. 지정된 학교 입구·건물을 학교 중심으로 임의 변환하지 않는다.

택시 경로는 카카오의 현재 도로 경로 및 예상요금이며 예약이나 미래 특정 시각의 확정 금액이 아니다. 통행료는 별도다. 울산의 중형 택시 기본 4,500원/2km, 거리 125m당 100원과 저속 30초당 100원, 22–04시 20% 및 시계외 30% 할증은 [울산시 요금표](https://www.ulsan.go.kr/u/traffic/contents.ulsan?mId=001003006001000000)를 기준으로 한다. 양 끝이 울산인 경우 표시되는 계산은 시계 내, 정차 0분 또는 5분이라는 조건부 예시다. 저속·호출료·시계외·통행료가 추가될 수 있고 최솟값·최댓값이나 통계적 신뢰구간을 뜻하지 않는다. 실제 할증 적용 범위와 요금표 변경은 별도 확인한다. 다른 지역은 카카오 제공 예상 요금을 표시하며 울산 요금표를 적용하지 않는다.

공공정보는 10분 캐시와 서버별 일일 보수적 호출 상한을 사용한다. 관광정보는 등록 자료이지 영업·예약 여부가 아니며, 기상청 자료는 발표 기준시각의 격자 실황이고, 대기질은 각 측정소의 관측시각을 따른다. 요청 지점과 측정소의 위치가 같다고 가정하지 않는다.

공식 자료: [카카오 장소](https://developers.kakao.com/docs/ko/local/dev-guide), [카카오 길찾기](https://developers.kakaomobility.com/guide/navi-api/directions), [관광정보](https://www.data.go.kr/data/15101578/openapi.do), [기상청 초단기실황](https://www.data.go.kr/data/15084084/openapi.do), [대기질](https://www.data.go.kr/data/15073861/openapi.do).
