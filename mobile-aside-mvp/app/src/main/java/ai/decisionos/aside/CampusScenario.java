package ai.decisionos.aside;

/** Campus scenario catalogue. Searches lead to current results; no data is fabricated. */
public final class CampusScenario {
    public final String group,title,description,query; public final boolean requiresSchool;
    private CampusScenario(String group,String title,String description,String query,boolean requiresSchool){this.group=group;this.title=title;this.description=description;this.query=query;this.requiresSchool=requiresSchool;}
    public String queryFor(String school){String s=school==null?"":school.trim();if(requiresSchool&&s.isEmpty())return "";return (requiresSchool?s+" ":"")+query;}
    public static final CampusScenario[] ALL={
        new CampusScenario("오늘의 학교","학사 공지 챙기기","학교 게시판에서 일정과 마감 공지를 찾아요.","학사 공지 일정",true),
        new CampusScenario("오늘의 학교","오늘 학식 살펴보기","학교 식당의 최신 메뉴를 찾아요.","학생식당 오늘 식단",true),
        new CampusScenario("오늘의 학교","시험·방학 일정","시험과 방학 날짜를 공식 안내에서 확인해요.","학사일정 시험 방학",true),
        new CampusScenario("친구와 함께","밥 약속 장소 찾기","친구와 만날 식당 후보를 찾아요.","학교 주변 식당 맛집",true),
        new CampusScenario("친구와 함께","동아리 모집·행사","동아리 공지와 행사 소식을 찾아요.","동아리 모집 행사 공지",true),
        new CampusScenario("친구와 함께","동아리 일정 준비","모임 준비를 할 일에 저장해 정리해요.","동아리 행사 준비 체크리스트",false),
        new CampusScenario("성장과 연구","취업·인턴·대외활동","학교 공지에서 내게 맞는 기회를 찾아요.","취업 인턴 대외활동 공지",true),
        new CampusScenario("성장과 연구","관심 논문 찾기","주제별 최신 논문을 검색해요.","arxiv 최신 논문 연구",false),
        new CampusScenario("성장과 연구","자격증 일정","시험 일정과 접수 안내를 찾아요.","자격증 시험 일정 접수",false),
        new CampusScenario("생활과 주말","과외·알바 찾기","과외와 아르바이트 공고를 찾아요.","대학생 과외 아르바이트 공고",false),
        new CampusScenario("생활과 주말","KTX 시간표","귀가나 여행에 맞는 열차 정보를 확인해요.","KTX 시간표 예매 코레일",false),
        new CampusScenario("생활과 주말","데이트·나들이","주말에 갈 만한 코스와 행사를 찾아요.","울산 데이트 코스 주말 행사",false),
        new CampusScenario("생활과 주말","초콜릿·선물 고르기","빼빼로데이 선물과 가격을 찾아요.","빼빼로데이 초콜릿 선물 가격 비교",false),
        new CampusScenario("생활과 주말","크리스마스·연말","연말에 갈 만한 이벤트를 찾아요.","울산 크리스마스 행사 연말 데이트",false),
        new CampusScenario("생활과 주말","과일·식품 찾기","원하는 식품과 가격 정보를 찾아요.","신선 과일 온라인 구매 가격 비교",false),
        new CampusScenario("생활과 주말","축제에 입을 옷","행사에 어울리는 옷을 찾아요.","대학생 축제 코디 옷",false),
        new CampusScenario("성장과 연구","학교 메일 정리","메일 연동 전, 사용자가 직접 메일을 확인해요.","학교 이메일 로그인",true)
    };
    private CampusScenario() {this("","","","",false);}
}
