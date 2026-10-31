import ai.decisionos.aside.GoalRules;
import ai.decisionos.aside.DiscoveryProviders;
public class TestGoalRules {
 static int checks=0;
 static void check(boolean b,String m){checks++;if(!b)throw new AssertionError(m);}
 public static void main(String[] args){
  check(GoalRules.PRESETS.length>=4,"four mandatory presets");
  for(String id:new String[]{"fitness","love","grades","home"}){String a=GoalRules.query(id,true,false,"","ko"),b=GoalRules.query(id,false,true,"","ko");check(!a.equals(b),"purpose alters query "+id);check(GoalRules.query(id,false,false,"","ko").isEmpty(),"both off "+id);check(GoalRules.query(id,true,true,"","en").endsWith("English"),"language alters query");}
  check(GoalRules.safe("https://m.youtube.com/results?search_query=test"),"allow HTTPS provider");
  for(String u:new String[]{"http://youtube.com","https://127.0.0.1","https://localhost/","https://youtube.com.evil.org/","https://evil.org/?a=youtube.com","https://user:pass@youtube.com/","javascript:alert(1)","https://[::1]/","https://m.youtube.com:8000/"})check(!GoalRules.safe(u),"reject "+u);
  check(GoalRules.total(100L,null,0L,0L)==null,"unknown shipping isn't free");check(GoalRules.total(0L,0L,0L,0L)==null,"zero price invalid");check(GoalRules.total(100L,10L,5L,20L)==95,"verified total");check(GoalRules.total(100L,0L,0L,101L)==null,"impossible discount");check(GoalRules.total(Long.MAX_VALUE,5L,0L,0L)==null,"overflow");
  check(GoalRules.sameProduct("model1","model1","black 1","black 1","new","new"),"same exact variant");check(!GoalRules.sameProduct("model1","model1","black 1","black 2","new","new"),"different quantity");check(!GoalRules.sameProduct("model1","model1","black 1","black 1","new","used"),"used differs");check(!GoalRules.sameProduct("","","","","",""),"missing identity never match");
  check(GoalRules.approvalValid("v1","v1",1000,2000),"approval version");check(!GoalRules.approvalValid("v1","v2",1000,2000),"changed price approval");check(!GoalRules.approvalValid("v1","v1",1000,302000),"expired approval");check(GoalRules.returnedState("handed_off").equals("unknown"),"return isn't verified");
  for(String p:new String[]{"youtube","naverweb","navershop","11st","coupang","munto","meetup","inflearn","kmooc","kakaomap","realestate"}){String u=DiscoveryProviders.url(p,"초보 운동 & test");check(GoalRules.safe(u),"generated URL "+p);check(DiscoveryProviders.sameOrigin(p,u),"origin "+p);check(!DiscoveryProviders.sameOrigin(p,"https://evil.org/"),"foreign origin "+p);check(DiscoveryProviders.searchMatches(p,u,"초보 운동 & test"),"query matches "+p);if(!p.equals("munto")&&!p.equals("kmooc"))check(!DiscoveryProviders.searchMatches(p,u,"unrelated"),"stale query rejected "+p);}
  check(!DiscoveryProviders.url("youtube","a&evil=1").contains("&evil="),"query injection");
  System.out.println("PASS "+checks+" goal planning, URL, offer and purchase rule checks");
 }
}
