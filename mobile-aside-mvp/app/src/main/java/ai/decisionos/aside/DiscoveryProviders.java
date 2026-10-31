package ai.decisionos.aside;
/** Fixed providers; user text can change query values, never an execution script. */
public final class DiscoveryProviders {
 public static String url(String p,String query){String q=GoalRules.enc(query);switch(p){
 case "youtube":return "https://m.youtube.com/results?search_query="+q;
 case "naverweb":return "https://m.search.naver.com/search.naver?query="+q;
 case "navershop":return "https://msearch.shopping.naver.com/search/all?query="+q;
 case "11st":return "https://search.11st.co.kr/MW/search?searchKeyword="+q;
 case "coupang":return "https://www.coupang.com/np/search?q="+q;
 case "munto":return "https://www.munto.kr/ko";
 case "meetup":return "https://www.meetup.com/find/?keywords="+q+"&source=EVENTS";
 case "inflearn":return "https://www.inflearn.com/courses?s="+q;
 case "kmooc":return "https://www.kmooc.kr/";
 case "kakaomap":return "https://m.map.kakao.com/actions/searchView?q="+q+"&sort=0&fromAppLink=true";
 case "realestate":return "https://m.search.naver.com/search.naver?query="+q;
 default:throw new IllegalArgumentException("Unknown provider");}}
 public static boolean sameOrigin(String p,String url){if(!GoalRules.safe(url))return false;try{String h=new java.net.URI(url).getHost();switch(p){case "youtube":return h.equals("m.youtube.com")||h.equals("www.youtube.com");case "naverweb":return h.equals("m.search.naver.com")||h.equals("search.naver.com");case "navershop":return h.equals("msearch.shopping.naver.com");case "11st":return h.equals("search.11st.co.kr");case "coupang":return h.equals("www.coupang.com");case "munto":return h.equals("www.munto.kr")||h.equals("munto.kr");case "meetup":return h.equals("www.meetup.com");case "inflearn":return h.equals("www.inflearn.com");case "kmooc":return h.equals("www.kmooc.kr");case "kakaomap":return h.equals("m.map.kakao.com");case "realestate":return h.equals("m.search.naver.com");default:return false;}}catch(Exception e){return false;}}
 public static boolean searchMatches(String p,String url,String query){
  if(!sameOrigin(p,url))return false;if(p.equals("munto")||p.equals("kmooc"))return true;
  try{java.net.URI u=new java.net.URI(url);String raw=u.getRawQuery();if(raw!=null)for(String pair:raw.split("&")){String[] kv=pair.split("=",2);if(kv.length==2&&java.util.Arrays.asList("search_query","query","searchKeyword","q","keywords","s").contains(kv[0])&&java.net.URLDecoder.decode(kv[1],"UTF-8").equals(query))return true;}
   return false;
  }catch(Exception e){return false;}
 }
 public static boolean shop(String p){return p.equals("navershop")||p.equals("11st")||p.equals("coupang");}
 public static String kind(String p){if(p.equals("youtube"))return "영상";if(p.equals("meetup")||p.equals("munto"))return "모임";if(p.equals("kakaomap")||p.equals("realestate"))return "장소";return "글";}
 private DiscoveryProviders(){}
}
