package ai.decisionos.aside;
import android.app.AlertDialog;import org.json.*;import java.util.*;
/** Shared conversation helpers; the companion is the only rendering implementation. */
final class GoalWorkspaceUi {
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
  new AlertDialog.Builder(c.a).setTitle("내 에이전트 대화").setItems(labels,(d,w)->c.switchGoal(goals.get(w).optString("id"))).setNegativeButton("닫기",null).show();
 }
 static String stepText(JSONArray steps){StringBuilder out=new StringBuilder();for(int n=0;n<steps.length();n++)out.append(n+1).append(". ").append(steps.optString(n)).append('\n');return out.toString();}
}
