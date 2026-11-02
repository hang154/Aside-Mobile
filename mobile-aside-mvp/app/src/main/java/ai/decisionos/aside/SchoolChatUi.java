package ai.decisionos.aside;
import android.app.*;import android.graphics.Color;import android.view.*;import android.widget.*;import org.json.*;
/** School tools are owned by a school conversation, not a separate feature home. */
final class SchoolChatUi {
 static void open(GoalChatUi c,String section){
  if(!c.character.equals("grades")||c.goalId.isEmpty()){JSONObject goal=null;for(JSONObject g:c.a.store.goals())if(!GoalStore.fixture(g)&&g.optString("character").equals("grades")){goal=g;break;}if(goal==null)goal=c.a.store.create("grades","내 학교생활","학교생활",0);c.switchConversation(goal.optString("id"),"");}
  c.companion.select("대화");c.render();
  if(section.equals("학교 알림"))tools(c,"inbox");else if(section.equals("학교 작업"))tools(c,"jobs");else if(section.equals("AI 답변 비교"))tools(c,"compare");
 }
 static Button secondary(GoalChatUi c,String text){Button b=c.a.button(text,false);b.setBackground(Ui.bg(NubiCompanionUi.COMPOSER,14,c.a));b.setTextColor(NubiCompanionUi.INK);return b;}
 static void card(GoalChatUi c){
  LinearLayout box=c.box(NubiCompanionUi.PANEL,16);box.setBackground(Ui.bg(NubiCompanionUi.PANEL,22,c.a));
  box.addView(c.a.txt("학교생활은 내가 챙길게",21,NubiCompanionUi.INK,true));
  box.addView(c.a.txt("학교 계정을 연결하면 공지와 과제, 메일을 함께 살펴볼 수 있어. 필요한 일은 아래 채팅에 말해 줘.",15,NubiCompanionUi.MUTED,false),Ui.match(c.a,-2,10));
  try(CampusFlowStore store=new CampusFlowStore(c.a)){for(String id:new String[]{"portal","blackboard","mail","everytime","gpt"}){JSONObject r=store.get("connection-"+id);box.addView(c.a.txt((r.optString("state").equals("verified")?"✓ ":"○ ")+CampusWorkflows.service(id)[1]+" · "+(r.optString("state").equals("verified")?"연결 확인됨":"연결 확인 필요"),14,NubiCompanionUi.INK,false),Ui.match(c.a,-2,10));}}
  LinearLayout extra=new LinearLayout(c.a);for(String id:new String[]{"everytime","gpt"}){Button link=secondary(c,CampusWorkflows.service(id)[1]+" 연결");link.setOnClickListener(v->new CampusHubUi(c.companion).openService(id));extra.addView(link,new LinearLayout.LayoutParams(0,-2,1));}box.addView(extra,Ui.match(c.a,-2,8));
  Button connect=c.a.button("학교 계정으로 한 번에 연결",true);connect.setOnClickListener(v->new SchoolSignIn(c).show());box.addView(connect,Ui.match(c.a,52,14));
  LinearLayout actions=new LinearLayout(c.a);for(String[] item:new String[][]{{"학교 소식","inbox"},{"진행 중인 일","jobs"}}){Button b=secondary(c,item[0]);b.setOnClickListener(v->tools(c,item[1]));actions.addView(b,new LinearLayout.LayoutParams(0,-2,1));}box.addView(actions,Ui.match(c.a,-2,8));
  Button watch=secondary(c,"새 학교 소식, 채팅으로 알려줘");watch.setOnClickListener(v->{SchoolChatWork.watch(c);c.a.toast("주기 확인을 요청했어. 실제 조회 결과를 이 채팅에 남길게.");});box.addView(watch,Ui.match(c.a,-2,8));
  Button vault=secondary(c,"기기 내 인증정보 보관함");vault.setOnClickListener(v->c.a.startActivity(new android.content.Intent(c.a,CredentialVaultActivity.class)));box.addView(vault,Ui.match(c.a,-2,8));
  Button mail=secondary(c,"작성된 메일 검토·발송");mail.setOnClickListener(v->CampusMailReview.show(c));box.addView(mail,Ui.match(c.a,-2,8));
  c.messages.addView(box,Ui.match(c.a,-2,8));
 }
 static void tools(GoalChatUi c,String section){
  // Existing receipts and editors remain available without leaving the school conversation.
  LinearLayout content=c.box(NubiCompanionUi.WHITE,14);ScrollView scroll=new ScrollView(c.a);scroll.addView(content);
  NubiCompanionUi u=c.companion;LinearLayout old=u.sideBody;u.sideBody=content;
  try{CampusHubUi hub=new CampusHubUi(u);if(section.equals("inbox"))hub.inbox();else if(section.equals("compare"))hub.compare();else hub.jobs();}finally{u.sideBody=old;}
  new AlertDialog.Builder(c.a).setTitle("똑똑이 · "+(section.equals("inbox")?"학교 소식":section.equals("compare")?"답장 비교":"진행 중인 일")).setView(scroll).setPositiveButton("대화로 돌아가기",null).show();
 }
}
