package ai.decisionos.aside;
import android.app.*;import android.content.*;import android.os.Bundle;import android.widget.*;import org.json.*;
public class GoalHomeActivity extends GoalUi {
 GoalStore store;
 public void onCreate(Bundle b){super.onCreate(b);store=new GoalStore(this);render();}
 protected void onResume(){super.onResume();if(store!=null)render();}
 void render(){String section=getIntent().getStringExtra("section");if(section==null)section="홈";frame("● 누비",section.equals("홈")?"내 목표 곁에, 나만의 작은 팀":"목표와 연결된 "+section);
  if(section.equals("프로필")){profile();return;}
  if(section.equals("내 활동")){LinearLayout p=card();p.addView(txt("기기에 남긴 활동",22,INK,true));action(p,"기존 할 일 보관함",()->startActivity(new Intent(this,TaskActivity.class)));for(JSONObject g:store.goals()){action(p,g.optString("title")+" · 일정·저장한 콘텐츠",()->workspace(g.optString("id"),3));}return;}
  if(section.equals("쇼핑·전문가")){LinearLayout p=card();p.addView(txt("어떤 목표의 준비물을 찾을까?",22,INK,true));note(p,"상품과 전문가를 목표 안에서 구분해 찾아요.");for(JSONObject g:store.goals())action(p,g.optString("title"),()->workspace(g.optString("id"),1));if(store.goals().isEmpty())note(p,"홈에서 목표를 먼저 만들어줘.");return;}
  body.addView(txt("무엇을 이루고 싶어?",32,INK,true),Ui.match(this,-2,20));body.addView(txt("탐색하고, 준비하고, 오늘 한 걸음.\n네 목표를 맡아줄 누비를 골라봐.",16,MUTED,false),Ui.match(this,-2,10));
  for(JSONObject g:store.goals()){GoalRules.Preset a=GoalRules.preset(g.optString("character"));LinearLayout p=card();hero(p,a,g.optString("title"));action(p,"이 목표 이어가기",()->workspace(g.optString("id"),-1));}
  body.addView(txt("추천 목표",20,INK,true),Ui.match(this,-2,24));
  for(GoalRules.Preset a:GoalRules.PRESETS){LinearLayout p=card();hero(p,a,a.title);note(p,a.topic+" · 미디어 / 준비물 / 사람 / 캘린더");action(p,a.name+"와 시작하기",()->create(a));}
  LinearLayout p=card();EditText free=edit(p,"직접 이루고 싶은 목표를 적어줘","");action(p,"나만의 목표 만들기",()->{String title=free.getText().toString().trim();if(title.isEmpty()||title.length()>100){toast("목표를 1~100자로 적어줘.");return;}new AlertDialog.Builder(this).setTitle("담당 누비 선택").setItems(new String[]{"건강이 · 운동","다정이 · 연애","똑똑이 · 학점","차곡이 · 집 사기","든든이 · 취업","떠남이 · 여행"},(d,i)->create(GoalRules.PRESETS[i],title)).show();});
  action(p,"대학생활 도구 모아보기",()->startActivity(new Intent(this,CampusToolsActivity.class)));
 }
 void create(GoalRules.Preset a){create(a,a.title);}
 void create(GoalRules.Preset a,String initial){LinearLayout p=Ui.vertical(this,BG,20);EditText title=edit(p,"목표",initial),topic=edit(p,"관심 주제 (민감정보 없이)",a.topic),budget=edit(p,"준비물 예산 (원, 선택)","");budget.setInputType(2);note(p,"주제는 외부 검색어로 사용해. 건강 기록이나 개인정보는 적지 말아줘. 구매 알림과 프로필 공개는 꺼진 상태로 시작해.");new AlertDialog.Builder(this).setTitle(a.name+"에게 맡길 목표").setView(p).setNegativeButton("취소",null).setPositiveButton("목표 시작",(d,w)->{try{String t=title.getText().toString().trim(),q=topic.getText().toString().trim(),n=budget.getText().toString();if(q.length()>80)throw new IllegalArgumentException();JSONObject g=store.create(a.id,t,q,n.isEmpty()?0:Long.parseLong(n));workspace(g.optString("id"),0);}catch(Exception ex){toast("목표·주제·예산을 확인해줘.");}}).show();}
 void workspace(String id,int tab){Intent i=new Intent(this,CharacterWorkspaceActivity.class);i.putExtra("goal_id",id);if(tab>=0)i.putExtra("tab",tab);startActivity(i);}
 void profile(){LinearLayout p=card();p.addView(txt("내 데이터와 연결",22,INK,true));note(p,"목표·저장 콘텐츠·준비물·일정은 이 기기에 저장해. 계정 연동이나 실시간 다중 사용자 매칭은 아직 제공하지 않아. 접근성 권한 없이 핵심 기능을 사용할 수 있어.");note(p,"YouTube·뉴스·쇼핑·모임은 공개 웹에서 탐색해. Threads/Instagram 개인 피드 API는 연결되지 않았어. 가격 알림은 자동 감시가 없는 수동 재조회야.");action(p,"기존 대학생활·포털 도구",()->startActivity(new Intent(this,CampusToolsActivity.class)));action(p,"모든 누비 기록 삭제",()->new AlertDialog.Builder(this).setTitle("목표·일정·웹 로그인 기록을 지울까?").setMessage("기존 할 일 보관함의 할 일도 함께 삭제해.").setNegativeButton("취소",null).setPositiveButton("모두 삭제",(d,w)->{store.clear();try(TaskStore t=new TaskStore(this)){t.getWritableDatabase().delete("tasks",null,null);}android.webkit.CookieManager.getInstance().removeAllCookies(null);android.webkit.WebStorage.getInstance().deleteAllData();getSharedPreferences("nubi_campus",0).edit().clear().apply();new android.webkit.WebView(this).clearCache(true);toast("기기 기록을 삭제했어.");render();}).show());}
 protected void onDestroy(){store.close();super.onDestroy();}
}
