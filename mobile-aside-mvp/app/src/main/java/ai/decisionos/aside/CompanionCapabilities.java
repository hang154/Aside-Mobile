package ai.decisionos.aside;
/** Purpose-specific entry points; all destinations remain inside the companion shell. */
final class CompanionCapabilities {
 static String[][] forAgent(String id){
  switch(id){
   case "fitness":return new String[][]{{"운동 영상·자료","미디어"},{"운동 용품 비교","준비물"},{"운동 모임","모임"},{"운동 일정","일정"},{"운동 시설·이동","장소·이동"}};
   case "love":return new String[][]{{"관계·데이트 자료","미디어"},{"선물·준비물 비교","준비물"},{"취미 모임","모임"},{"데이트 일정","일정"},{"데이트 장소·이동","장소·이동"},{"여행·숙소 비교","여행 비교"},{"함께할 생활 계획","생활 계획"}};
   case "grades":return new String[][]{{"학습 영상·논문 자료","미디어"},{"학습 준비물","준비물"},{"스터디 모임","모임"},{"학습 일정","일정"},{"학교 메일·포털·공고","캠퍼스"},{"학사일정","학사일정"},{"문서·과제 보관함","작업"},{"학교 주변·이동","장소·이동"}};
   case "home":return new String[][]{{"주거·청약 자료","미디어"},{"내 집 준비물 비교","준비물"},{"부동산 공부 모임","모임"},{"청약·주거 일정","일정"},{"관심 지역 탐색","장소·이동"},{"주거 준비 계획","생활 계획"}};
   case "career":return new String[][]{{"취업·면접 자료","미디어"},{"면접 준비물","준비물"},{"취업 스터디","모임"},{"지원·면접 일정","일정"},{"학교·외부 채용 공고","캠퍼스"},{"지원 문서 보관함","작업"},{"면접 장소·이동","장소·이동"}};
   case "travel":return new String[][]{{"여행 영상·자료","미디어"},{"여행 준비물","준비물"},{"여행 모임","모임"},{"여행 일정","일정"},{"교통·숙소 비교","여행 비교"},{"여행 장소·이동","장소·이동"},{"여행 계획","생활 계획"}};
   default:throw new IllegalArgumentException("Unknown agent: "+id);
  }
 }
 static String placeQuery(String id){switch(id){case "fitness":return "울산 운동 시설";case "love":return "울산 데이트";case "grades":return "UNIST 주변 스터디 카페";case "home":return "울산 아파트";case "career":return "울산 취업 지원 센터";case "travel":return "부산 여행";default:return "UNIST";}}
}
