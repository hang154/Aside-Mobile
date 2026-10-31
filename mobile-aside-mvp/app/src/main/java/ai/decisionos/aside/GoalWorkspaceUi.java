package ai.decisionos.aside;

import android.app.AlertDialog;
import android.graphics.Color;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.util.*;

/** Native interpretation of assistant-ui threads and OpenBot coworker workspaces.
 * Uses the existing Qwen relay, not either project's React/AG-UI runtime. */
final class GoalWorkspaceUi {
 final GoalChatUi c;
 final GoalAgentActivity a;
 LinearLayout browser, details, content;
 String tab="브라우저";
 final Map<String,Button> tabs=new LinkedHashMap<>();
 GoalWorkspaceUi(GoalChatUi c){this.c=c;a=c.a;}
 static String[] suggestions(String character){
  switch(character){
   case "fitness":return new String[]{"초보 스트레칭 영상 2개 찾아줘","운동용품 비교해줘"};
   case "love":return new String[]{"울산 실내 데이트 장소 2곳 찾아줘","부산 여행 코스 찾아줘"};
   case "grades":return new String[]{"파이썬 입문 강의 2개 찾아줘","UIRP 예산서 초안 작성해줘"};
   default:return new String[]{"내 집 마련 준비 영상 2개 찾아줘","가계부 쓰는 방법 찾아줘"};
  }
 }
 static void conversations(GoalChatUi c){
  List<JSONObject> goals=c.a.store.goals();String[] labels=new String[goals.size()];
  for(int n=0;n<goals.size();n++){JSONObject g=goals.get(n);GoalRules.Preset p=GoalRules.preset(g.optString("character"));labels[n]=(g.optString("id").equals(c.goalId)?"● ":"")+p.name+" · "+g.optString("title");}
  new AlertDialog.Builder(c.a).setTitle("내 에이전트 대화").setItems(labels,(d,w)->c.switchGoal(goals.get(w).optString("id"))).setNeutralButton("작업실로",(d,w)->c.a.finish()).setNegativeButton("닫기",null).show();
 }
 void mount(LinearLayout root,LinearLayout stage,LinearLayout chat,LinearLayout browser,boolean wide){
  this.browser=browser;
  LinearLayout desk=c.box(Color.WHITE,8);
  LinearLayout bar=new LinearLayout(a);
  for(String name:new String[]{"브라우저","실행 기록","파일"}){Button b=a.button(name,name.equals(tab));b.setOnClickListener(v->select(name));bar.addView(b,new LinearLayout.LayoutParams(0,c.dp(44),1));tabs.put(name,b);}
  desk.addView(bar);content=c.box(0xfff5f6f8,4);content.setBackground(Ui.bg(0xfff5f6f8,18,a));
  content.addView(browser,new LinearLayout.LayoutParams(-1,-1));
  ScrollView scroll=new ScrollView(a);details=c.box(0xfff5f6f8,14);scroll.addView(details);content.addView(scroll,new LinearLayout.LayoutParams(-1,-1));scroll.setTag("details");scroll.setVisibility(View.GONE);
  desk.addView(content,new LinearLayout.LayoutParams(-1,0,1));
  if(wide){stage.addView(chat,new LinearLayout.LayoutParams(0,-1,1));stage.addView(desk,new LinearLayout.LayoutParams(0,-1,1.15f));}
  else{stage.addView(chat,new LinearLayout.LayoutParams(-1,0,1.4f));stage.addView(desk,new LinearLayout.LayoutParams(-1,0,1));}
  root.addView(stage,new LinearLayout.LayoutParams(-1,0,1));refresh();
 }
 void select(String name){tab=name;for(Map.Entry<String,Button> e:tabs.entrySet()){boolean selected=e.getKey().equals(tab);e.getValue().setSelected(selected);e.getValue().setTextColor(selected?GoalUi.PURPLE:GoalUi.MUTED);e.getValue().setBackground(Ui.bg(selected?0xffe9e6ff:0xfff1f3f5,16,a));}refresh();}
 JSONArray latestSteps(){if(c.running||c.submitting)return c.steps;for(int n=c.history.length()-1;n>=0;n--){JSONObject m=c.history.optJSONObject(n);if(m!=null&&m.optString("role").equals("assistant")){JSONArray steps=m.optJSONArray("steps");return steps==null?new JSONArray():steps;}}return new JSONArray();}
 static String stepText(JSONArray steps){StringBuilder out=new StringBuilder();for(int n=0;n<steps.length();n++)out.append(n+1).append(". ").append(steps.optString(n)).append('\n');return out.toString();}
 List<JSONObject> documents(){List<JSONObject> docs=new ArrayList<>();for(int n=c.history.length()-1;n>=0;n--){JSONObject m=c.history.optJSONObject(n),doc=m==null?null:m.optJSONObject("document");if(doc!=null)docs.add(doc);}return docs;}
 void refresh(){
  if(content==null)return;boolean web=tab.equals("브라우저");browser.setVisibility(web?View.VISIBLE:View.GONE);content.findViewWithTag("details").setVisibility(web?View.GONE:View.VISIBLE);details.removeAllViews();if(web)return;
  if(tab.equals("실행 기록")){
   details.addView(a.txt(c.running?"Qwen이 작업하고 있어":"최근 작업 기록",18,GoalUi.INK,true));
   JSONArray steps=latestSteps();if(steps.length()==0)details.addView(a.txt("아직 실행 기록이 없어. 메시지를 보내면 실제 작업 단계가 여기에 쌓여.",14,GoalUi.MUTED,false),Ui.match(a,-2,12));
   for(int n=0;n<steps.length();n++){TextView line=a.txt(String.format(java.util.Locale.ROOT,"%02d  %s",n+1,steps.optString(n)),13,GoalUi.INK,false);line.setTextIsSelectable(true);details.addView(line,Ui.match(a,-2,12));}
  }else{
   details.addView(a.txt("이 대화에서 만든 파일",18,GoalUi.INK,true));int count=0;
   for(JSONObject doc:documents()){
    JSONObject manifest=doc.optJSONObject("manifest");JSONArray files=manifest==null?null:manifest.optJSONArray("files");
    for(int n=0;files!=null&&n<files.length();n++){JSONObject file=files.optJSONObject(n);if(file==null)continue;String name=file.optString("name");if(!name.endsWith(".docx")&&!name.endsWith(".hwpx"))continue;count++;
     LinearLayout card=c.box(Color.WHITE,12);card.setBackground(Ui.bg(Color.WHITE,14,a));card.addView(a.txt(name,14,GoalUi.INK,true));card.addView(a.txt(doc.optString("state").equals("uploaded")?"업로드 검증 완료":"생성된 초안 · 제출 상태는 답변에서 확인",12,GoalUi.MUTED,false));Button open=a.button("다운로드 · 열기",false);open.setOnClickListener(v->c.openDocument(doc,file));card.addView(open);details.addView(card,Ui.match(a,-2,12));
    }
   }
   if(count==0)details.addView(a.txt("아직 생성된 파일이 없어. 예산서 같은 문서를 요청하면 여기에 모아둘게.",14,GoalUi.MUTED,false),Ui.match(a,-2,12));
  }
 }
}
