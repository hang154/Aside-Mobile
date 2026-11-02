package ai.decisionos.aside;
import android.content.*;import android.os.*;import org.json.*;
final class HtmlHomeChecks {
 static void waitReady(GoalInstrumentation i,NubiTossHomeUi h)throws Exception{for(int n=0;n<60;n++){if("true".equals(TossHomeChecks.js(i,h,"Boolean(window.homeHydrated&&document.querySelectorAll('.goal-tile').length===5)")))return;Thread.sleep(100);}throw new AssertionError("HTML home not hydrated");}
 static void run(GoalInstrumentation i){Bundle out=new Bundle();GoalAgentActivity a=null;try{
 a=(GoalAgentActivity)i.startActivitySync(new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("companion_page","홈").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));final GoalAgentActivity h=a;waitReady(i,h.chat.companion.tossHome);NubiTossHomeUi home=h.chat.companion.tossHome;
 if(BuildConfig.FLAVOR.equals("campushome")){
 for(String tab:new String[]{"academic","email","club"}){TossHomeChecks.js(i,home,"st.campusTab='"+tab+"';render()");i.check("2".equals(TossHomeChecks.js(i,home,"document.querySelectorAll('.campus-item').length")),tab+" exactly two rows");}
 TossHomeChecks.js(i,home,"st.campusTab='academic';render()");Thread.sleep(400);
 i.check("true".equals(TossHomeChecks.js(i,home,"document.querySelector('.hero').getBoundingClientRect().bottom<document.querySelector('.campus-today').getBoundingClientRect().top && document.querySelector('.campus-today').getBoundingClientRect().bottom<document.querySelector('.goals-peek').getBoundingClientRect().top")),"campus between banner and agents");
 i.check("true".equals(TossHomeChecks.js(i,home,"document.querySelector('.goal-tile').getBoundingClientRect().bottom <= document.querySelector('nav').getBoundingClientRect().top")),"agent cards fully visible on first screen");
 TossTouchChecks.tap(i,"새 학사 공지 살펴보기");i.check(h.chat.character.equals("grades"),"campus row opens school agent");i.check(!h.chat.running&&!h.chat.submitting,"campus request remains draft");i.runOnMainSync(()->h.chat.companion.select("홈"));waitReady(i,h.chat.companion.tossHome);home=h.chat.companion.tossHome;
 }
 i.check("5".equals(TossHomeChecks.js(i,home,"document.querySelectorAll('nav button').length")),"5 tabs");i.check("false".equals(TossHomeChecks.js(i,home,"document.querySelector('nav').innerText.includes('친구')")),"no friends tab");i.check("true".equals(TossHomeChecks.js(i,home,"Array.from(document.images).every(x=>x.complete&&x.naturalWidth>0)")),"bundled source characters");
 for(String ctx:new String[]{"first","ot","quiz","quiz-end","during","after","exam","deadline","change","grades","scholar","team","free"}){TossHomeChecks.js(i,home,"homeContext='"+ctx+"';render()");i.check("1".equals(TossHomeChecks.js(i,home,"document.querySelectorAll('.hero').length")),ctx+" one banner");i.check("true".equals(TossHomeChecks.js(i,home,"document.documentElement.scrollWidth<=innerWidth+1")),ctx+" no overflow");}
 TossHomeChecks.js(i,home,"homeContext='during';render()");HomeUiChecks.shot(i,"html-home.png");
 TossTouchChecks.tap(i,"몸 만들고 싶어");Thread.sleep(500);i.check(h.chat.character.equals("fitness"),"source goal opens native fitness");i.check(!h.chat.running&&!h.chat.submitting,"draft does not autosubmit");i.runOnMainSync(()->h.chat.companion.select("홈"));waitReady(i,h.chat.companion.tossHome);
 home=h.chat.companion.tossHome;
 for(String label:new String[]{"대화","둘러보기","보관함","나의 누비"}){String page=label.equals("둘러보기")?"탐색":label.equals("보관함")?"작업":label.equals("나의 누비")?"내 정보":label;final NubiTossHomeUi current=h.chat.companion.tossHome;TossHomeChecks.js(i,current,"document.querySelector('[data-action=nativeNav][data-page=\""+page+"\"]').click()");Thread.sleep(250);i.check(h.chat.companion.page.equals(page),"native route "+page);i.runOnMainSync(()->h.chat.companion.select("홈"));waitReady(i,h.chat.companion.tossHome);}
 i.runOnMainSync(()->h.chat.companion.tossHome.new Bridge().route("invalid"));i.check(h.chat.companion.page.equals("홈"),"unknown route rejected");
 out.putString("stream","PASS "+i.checks+" HTML home native checks\n");
 }catch(Throwable e){out.putString("stream","FAIL "+e+"\n");}finally{if(a!=null){GoalAgentActivity h=a;i.runOnMainSync(h::finish);}}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
