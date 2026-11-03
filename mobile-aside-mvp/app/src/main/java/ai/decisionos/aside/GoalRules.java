package ai.decisionos.aside;
import java.net.URI;
import java.net.URLEncoder;
import java.util.*;

/** Pure, deterministic planning and commerce contracts. No model inference. */
public final class GoalRules {
 public static final class Preset {
  public final String id,name,title,topic,item,match,tool,emoji; public final int color;
  Preset(String i,String n,String t,String q,String p,String m,String u,String e,int c){id=i;name=n;title=t;topic=q;item=p;match=m;tool=u;emoji=e;color=c;}
 }
 public static final Preset[] PRESETS={
  new Preset("fitness","건강이","운동 습관 만들기","근력 운동","운동 매트","울산 러닝 모임","https://www.nhs.uk/live-well/exercise/","운동",0xff5ba78b),
  new Preset("love","다정이","연애와 좋은 관계","연애 관계","보드게임","울산 취미 모임","https://m.map.kakao.com/actions/searchView?q=%EC%9A%B8%EC%82%B0%20%EB%8D%B0%EC%9D%B4%ED%8A%B8&sort=0","연애",0xffd8879d),
  new Preset("grades","똑똑이","학점 챙기기","대학교 공부","스터디 플래너","울산 스터디 모임","https://www.kmooc.kr/","학점",0xff7c78cb),
  new Preset("home","차곡이","내 집 마련 준비","주택 청약","가계부","부동산 공부 모임","https://www.applyhome.co.kr/","집 사기",0xffba925b),
  new Preset("career","든든이","취업 준비하기","취업 면접 준비","면접 노트","취업 스터디","https://www.wanted.co.kr/","취업",0xff6696c2),
  new Preset("travel","떠남이","여행 준비하기","국내 여행 준비","여행 파우치","여행 모임","https://www.korail.com/ticket","여행",0xff6c9ca7)};
 public static Preset preset(String id){for(Preset p:PRESETS)if(p.id.equals(id))return p;throw new IllegalArgumentException("Unknown character");}
 public static String query(String id,boolean motivation,boolean information,String topic,String language){
  Preset p=preset(id);if(!motivation&&!information)return "";
  String t=topic==null||topic.trim().isEmpty()?p.topic:topic.trim();if(t.length()>80)throw new IllegalArgumentException("Topic too long");
  return t+ (motivation&&information?" (경험 OR 방법)":motivation?" (경험 OR 후기)":" (방법 OR 가이드)")+("en".equals(language)?" English":"");
 }
 public static String enc(String s){try{return URLEncoder.encode(s,"UTF-8");}catch(Exception e){throw new IllegalArgumentException(e);}}
 public static boolean safe(String url){try{URI u=new URI(url);String h=u.getHost();if(!"https".equals(u.getScheme())||h==null||u.getUserInfo()!=null||u.getPort()!=-1&&u.getPort()!=443)return false;
  h=h.toLowerCase(Locale.ROOT);if(h.matches("[0-9.]+")||h.contains(":")||h.equals("localhost")||h.endsWith(".local"))return false;
  for(String d:DOMAINS)if(h.equals(d)||h.endsWith("."+d))return true;return false;}catch(Exception e){return false;}}
 private static final String[] DOMAINS={"chatgpt.com","auth.openai.com","youtube.com","youtu.be","news.google.com","naver.com","kakao.com","11st.co.kr","coupang.com","munto.kr","meetup.com","kmooc.kr","inflearn.com","applyhome.co.kr","nhs.uk","unist.ac.kr","office.com","wanted.co.kr","saramin.co.kr","korail.com","openalex.org","arxiv.org","threads.net","threads.com","instagram.com","sm-hive.com","molit.go.kr","r-one.co.kr","kbland.kr"};
 public static Long total(Long price,Long shipping,Long fees,Long immediateDiscount){if(price==null||price<=0||shipping==null||shipping<0||fees==null||fees<0)return null;long d=immediateDiscount==null?0:immediateDiscount;if(d<0||d>price)return null;try{return Math.subtractExact(Math.addExact(Math.addExact(price,shipping),fees),d);}catch(ArithmeticException ex){return null;}}
 public static boolean sameProduct(String a,String b,String optionA,String optionB,String conditionA,String conditionB){return a!=null&&!a.trim().isEmpty()&&a.equals(b)&&optionA!=null&&!optionA.isEmpty()&&optionA.equals(optionB)&&conditionA!=null&&!conditionA.isEmpty()&&conditionA.equals(conditionB);}
 public static boolean approvalValid(String approved,String current,long at,long now){return approved!=null&&approved.equals(current)&&now>=at&&now-at<=300000;}
 public static String returnedState(String state){return "handed_off".equals(state)?"unknown":state;}
 private GoalRules(){}
}
