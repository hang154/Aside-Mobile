package ai.decisionos.aside;
import android.content.*;import android.os.*;
final class GroupRoomChecks {
 static void run(GoalInstrumentation i){Bundle out=new Bundle();GoalAgentActivity a=null;try{
 a=(GoalAgentActivity)i.startActivitySync(new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("companion_page","ホーム").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));final GoalAgentActivity h=a;i.runOnMainSync(()->h.chat.companion.select("홈"));HtmlHomeChecks.waitReady(i,h.chat.companion.tossHome);NubiTossHomeUi home=h.chat.companion.tossHome;
 TossTouchChecks.tap(i,"대화");Thread.sleep(500);i.check("1".equals(TossHomeChecks.js(i,home,"document.querySelectorAll('.group-room').length")),"bottom tab opens group");HomeUiChecks.shot(i,"group-empty.png");
 for(String request:new String[]{"연애 고민 도와줘","블랙보드 연결 도와줘","시험 끝나고 데이트 여행 예산 KTX 같이"}){TossHomeChecks.js(i,home,"groupSend("+org.json.JSONObject.quote(request)+")");i.check("true".equals(TossHomeChecks.js(i,home,"document.querySelectorAll('.group-avatar img').length>1")),"left character avatars");}
 i.check("true".equals(TossHomeChecks.js(i,home,"['love','grades','home','travel'].every(id=>groupHistory.some(m=>m.role===id))")),"complex role composition");HomeUiChecks.shot(i,"group-multi.png");
 TossHomeChecks.js(i,home,"document.querySelector('[data-action=groupRun][data-agent=love]').click()");Thread.sleep(500);i.check(h.chat.character.equals("love"),"handoff to native love");i.check(h.chat.companion.page.equals("대화"),"individual chat preserved");i.check(!h.chat.running&&!h.chat.submitting,"no auto execution");i.runOnMainSync(()->h.chat.companion.select("누비톡"));Thread.sleep(1000);i.check("true".equals(TossHomeChecks.js(i,h.chat.companion.tossHome,"groupHistory.length>5")),"group retained after individual chat");HomeUiChecks.shot(i,"group-final.png");
 out.putString("stream","PASS "+i.checks+" group room checks\n");}catch(Throwable e){out.putString("stream","FAIL "+e+"\n");}finally{if(a!=null){GoalAgentActivity h=a;i.runOnMainSync(h::finish);}}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
