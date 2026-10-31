package ai.decisionos.aside;
import android.app.*;import android.content.*;import org.json.*;
/** Isolated temporary goal. No live network or user goal edits. */
final class GoalAgentChecks {
 static int run(Instrumentation i)throws Exception{
  int checks=0;GoalAgentActivity activity=null;String id=null,otherId=null;
  try(GoalStore store=new GoalStore(i.getTargetContext())){
   id=store.create("fitness","QWEN_CONTRACT_FIXTURE","운동",0).getString("id");
   Intent intent=new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("goal_id",id).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
   activity=(GoalAgentActivity)i.startActivitySync(intent);i.waitForIdleSync();final GoalAgentActivity a=activity;final String gid=id;
   for(JSONObject cmd:new JSONObject[]{new JSONObject().put("op","goal_observe").put("goal_id","wrong"),new JSONObject().put("op","goal_search").put("goal_id",id).put("provider","arbitrary").put("query","x"),new JSONObject().put("op","goal_select").put("goal_id",id).put("observation_id","stale").put("index",0),new JSONObject().put("op","goal_report").put("goal_id",id).put("summary","unobserved").put("source_urls",new JSONArray().put("https://www.youtube.com/watch?v=x"))}){
    final boolean[] rejected={false};i.runOnMainSync(()->{try{a.command(cmd,r->{});}catch(IllegalArgumentException e){rejected[0]=true;}catch(Exception e){throw new RuntimeException(e);}});if(!rejected[0])throw new AssertionError("invalid command accepted");checks++;
   }
   if(!GoalAgentActivity.sameSource("https://m.youtube.com/watch?v=one","https://www.youtube.com/watch?v=one"))throw new AssertionError("canonical source");checks++;
   if(GoalAgentActivity.sameSource("https://m.youtube.com/watch?v=two","https://www.youtube.com/watch?v=one"))throw new AssertionError("source changed");checks++;
   otherId=store.create("fitness","QWEN_CHAT_ISOLATION_FIXTURE","다른 목표",0).getString("id");final String foreign=otherId;
   for(JSONObject cmd:new JSONObject[]{new JSONObject().put("op","goal_open").put("character","love"),new JSONObject().put("op","goal_open").put("character","fitness").put("goal_id",foreign)}){
    final boolean[] rejected={false};i.runOnMainSync(()->{try{a.command(cmd,r->{});}catch(IllegalArgumentException e){rejected[0]=true;}catch(Exception e){throw new RuntimeException(e);}});if(!rejected[0]||!gid.equals(a.gid))throw new AssertionError("chat goal crossing");checks++;
   }
   i.runOnMainSync(()->{a.chat.history.put(a.chat.message("user","fixture instruction"));a.chat.input.setText("retained draft");a.chat.save();});
   if(store.goal(otherId).has("chatMessages"))throw new AssertionError("chat leaked to same-character goal");checks++;
   try(GoalStore reopened=new GoalStore(i.getTargetContext())){if(!reopened.goal(id).getJSONArray("chatMessages").getJSONObject(0).getString("text").equals("fixture instruction"))throw new AssertionError("chat history persistence");checks++;}
   i.runOnMainSync(()->{a.chat.busy(true);a.chat.pause();});if(a.chat.running||a.chat.visible)throw new AssertionError("pause must stop chat");checks++;
   if(!store.goal(id).optString("chatDraft").equals("retained draft"))throw new AssertionError("draft lost on stop");checks++;
   JSONObject prefs=new JSONObject().put("motivation",false).put("information",false);store.patchGoal(id,prefs);final boolean[] disabled={false};i.runOnMainSync(()->{try{a.command(new JSONObject().put("op","goal_search").put("goal_id",gid).put("provider","youtube").put("query","x"),r->{});}catch(IllegalArgumentException e){disabled[0]=true;}catch(Exception e){throw new RuntimeException(e);}});if(!disabled[0])throw new AssertionError("disabled discovery");checks++;
   final JSONObject[] result={null};i.runOnMainSync(()->{try{a.sources.add("https://www.youtube.com/watch?v=fixture");a.command(new JSONObject().put("op","goal_report").put("goal_id",gid).put("summary","fixture").put("source_urls",new JSONArray().put("https://www.youtube.com/watch?v=fixture")),r->result[0]=r);}catch(Exception e){throw new RuntimeException(e);}});if(result[0]==null||!"report_saved".equals(result[0].optString("state"))||!"fixture".equals(store.goal(id).optString("qwenSummary")))throw new AssertionError("report persistence");checks++;
  }finally{if(activity!=null){final Activity a=activity;i.runOnMainSync(a::finish);i.waitForIdleSync();}for(String clean:new String[]{id,otherId})if(clean!=null)try(GoalStore s=new GoalStore(i.getTargetContext())){s.deleteGoal(clean);}}
  return checks;
 }
}
