package ai.decisionos.aside;
import android.os.Bundle;import org.json.*;
final class CampusPriorityChecks {
 static void run(GoalInstrumentation i){Bundle b=new Bundle();try{
 long now=java.time.Instant.parse("2026-11-02T00:00:00Z").toEpochMilli();
 JSONObject s=CampusSignal.extract("장학생 모집","신청 마감: 2026-11-13까지\n지원금 400만원","https://portal.unist.ac.kr/","2026-10-15",now);
 i.check(s.getJSONArray("categories").toString().contains("장학"),"scholarship classification");i.check(s.getJSONArray("deadlines").getJSONObject(0).getString("date").equals("2026-11-13"),"explicit source deadline");i.check(s.getJSONArray("amount_mentions").getString(0).equals("400만원"),"amount mention preserved without invented eligibility");
 i.check(CampusSignal.extract("공지","게시일 2026-11-02","", "",now).getJSONArray("deadlines").length()==0,"posting date not deadline");
 i.check(CampusSignal.extract("작년 일정","작년 마감: 2025-11-13","","",now).getJSONArray("deadlines").length()==0,"historical example not current deadline");
 i.check(CampusSignal.extract("과제","기한 11월 3일","","",now).getJSONArray("deadlines").length()==0,"missing year remains unknown");
 i.check(CampusSignal.extract("시험","시험일 2026-02-30","","",now).getJSONArray("deadlines").length()==0,"invalid calendar date rejected");
 i.check(CampusSignal.extract("과제","기한 2026-10-01","","",now).getJSONArray("deadlines").getJSONObject(0).getBoolean("expired"),"past deadline marked expired");
 i.check(!SchoolSignIn.interactive("mail")&&!SchoolSignIn.interactive("blackboard")&&SchoolSignIn.interactive("portal"),"portal only interactive authentication");
 i.check(SchoolChatWork.campusExecutor("assignment")&&SchoolChatWork.campusExecutor("bb_alerts")&&SchoolChatWork.campusExecutor("pdf"),"Blackboard requests reach campus execution");
 i.check(!SchoolSignIn.verified("blackboard","https://blackboard.unist.ac.kr/",true,true),"credential screen never equals connected");
 b.putString("stream","PASS "+i.checks+" priority campus checks (local fixtures, no external submissions)\n");
 }catch(Throwable t){b.putString("stream","FAIL "+t+"\n");}i.finish(b.getString("stream").startsWith("PASS")?-1:0,b);}
}
