package ai.decisionos.aside;
import android.app.*;import android.content.*;import org.json.*;
/** Isolated temporary goal. No live network or user goal edits. */
final class GoalAgentChecks {
 static int run(Instrumentation i)throws Exception{
  int checks=0;GoalAgentActivity activity=null;String id=null,otherId=null;
  boolean oldCompanion=i.getTargetContext().getSharedPreferences("nubi_display",0).getBoolean("companion_ui",true);i.getTargetContext().getSharedPreferences("nubi_display",0).edit().putBoolean("companion_ui",false).commit();
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
   final boolean oldStyle=a.chat.modern();
   i.runOnMainSync(()->{a.getPreferences(0).edit().putBoolean("coworker_ui",true).commit();a.chat.save();a.chat.build();a.chat.companion.libraryTab="실행 기록";a.chat.companion.select("작업");});
   if(!a.chat.input.getText().toString().equals("retained draft")||a.chat.companion==null)throw new AssertionError("workspace rebuild lost draft");checks++;
   i.runOnMainSync(()->{try{a.chat.steps=new JSONArray().put("actual fixture tool");a.chat.busy(true);a.chat.companion.refresh();}catch(Exception e){throw new RuntimeException(e);}});
   if(a.chat.companion.latestSteps().length()!=1)throw new AssertionError("running tool log missing");checks++;
   i.runOnMainSync(()->{a.chat.busy(false);a.chat.companion.libraryTab="아티팩트";a.chat.companion.select("작업");});
   if(!a.chat.companion.documents().isEmpty())throw new AssertionError("files leaked from another goal");checks++;
   if(!a.chat.previousUser("missing").equals("fixture instruction"))throw new AssertionError("retry does not use local user instruction");checks++;
   i.runOnMainSync(()->{a.getPreferences(0).edit().putBoolean("coworker_ui",false).commit();a.chat.save();a.chat.build();});
   if(a.chat.companion==null||!a.chat.input.getText().toString().equals("retained draft"))throw new AssertionError("classic layout loses draft");checks++;
   i.runOnMainSync(()->{a.getPreferences(0).edit().putBoolean("coworker_ui",oldStyle).commit();a.chat.save();a.chat.build();});
   if(store.goal(otherId).has("chatMessages"))throw new AssertionError("chat leaked to same-character goal");checks++;
   try(GoalStore reopened=new GoalStore(i.getTargetContext())){if(!reopened.goal(id).getJSONArray("chatMessages").getJSONObject(0).getString("text").equals("fixture instruction"))throw new AssertionError("chat history persistence");checks++;}
   i.runOnMainSync(()->{try{a.chat.job="document-fixture";a.chat.visible=true;a.chat.busy(true);a.runs.run=new JSONObject().put("id",java.util.UUID.randomUUID().toString()).put("goalId",gid).put("conversationId",a.chat.conversationId).put("character",a.chat.character).put("jobId","document-fixture").put("requestId","test-request").put("state","RUNNING");a.runs.accept(new JSONObject().put("job_id","document-fixture").put("goal_id",gid).put("state","completed").put("kind","document").put("answer","document fixture draft").put("document",new JSONObject().put("state","needs_information").put("manifest",new JSONObject().put("files",new JSONArray()))));}catch(Exception e){throw new RuntimeException(e);}});
   JSONObject savedDoc=store.goal(id);if(!savedDoc.getJSONObject("documentResult").optString("state").equals("needs_information"))throw new AssertionError("document draft state lost");checks++;
   if(!savedDoc.getJSONArray("chatMessages").getJSONObject(savedDoc.getJSONArray("chatMessages").length()-1).getJSONObject("document").optString("job_id").equals("document-fixture"))throw new AssertionError("document receipt not saved with goal chat");checks++;
   if(a.chat.companion!=null&&a.chat.companion.documents().size()!=1)throw new AssertionError("document not in goal workspace");checks++;
   if(store.goal(otherId).has("documentResult"))throw new AssertionError("document leaked across goals");checks++;
   i.runOnMainSync(()->{a.chat.busy(true);a.chat.pause();});if(!a.chat.running||a.chat.visible)throw new AssertionError("pause hides UI without falsely cancelling execution");checks++;
   if(!store.goal(id).optString("chatDraft").equals("retained draft"))throw new AssertionError("draft lost on stop");checks++;
   JSONObject prefs=new JSONObject().put("motivation",false).put("information",false);store.patchGoal(id,prefs);final boolean[] disabled={false};i.runOnMainSync(()->{try{a.command(new JSONObject().put("op","goal_search").put("goal_id",gid).put("provider","youtube").put("query","x"),r->{});}catch(IllegalArgumentException e){disabled[0]=true;}catch(Exception e){throw new RuntimeException(e);}});if(!disabled[0])throw new AssertionError("disabled discovery");checks++;
   final JSONObject[] result={null};i.runOnMainSync(()->{try{a.sources.add("https://www.youtube.com/watch?v=fixture");a.command(new JSONObject().put("op","goal_report").put("goal_id",gid).put("summary","fixture").put("source_urls",new JSONArray().put("https://www.youtube.com/watch?v=fixture")),r->result[0]=r);}catch(Exception e){throw new RuntimeException(e);}});if(result[0]==null||!"report_saved".equals(result[0].optString("state"))||!"fixture".equals(store.goal(id).optString("qwenSummary")))throw new AssertionError("report persistence");checks++;
   i.runOnMainSync(()->{a.getSharedPreferences("nubi_display",0).edit().putBoolean("companion_ui",true).commit();a.chat.save();a.chat.build();});
   if(a.chat.companion==null)throw new AssertionError("companion layout missing");checks++;
   if(!a.chat.input.getText().toString().equals("retained draft"))throw new AssertionError("companion layout lost draft");checks++;
   i.runOnMainSync(()->a.chat.companion.select("작업"));if(a.chat.companion.documents().size()!=1)throw new AssertionError("companion document scope");checks++;
   i.runOnMainSync(()->a.chat.companion.select("친구"));if(!a.chat.companion.page.equals("친구"))throw new AssertionError("friend page missing");checks++;
   i.runOnMainSync(()->a.chat.companion.select("탐색"));if(!a.chat.companion.page.equals("탐색"))throw new AssertionError("companion discovery missing");checks++;
   i.runOnMainSync(()->a.chat.companion.browser());if(a.web.getParent()==null||!a.chat.companion.page.equals("브라우저"))throw new AssertionError("companion browser unmounted");checks++;
   i.runOnMainSync(()->a.chat.companion.select("내 정보"));if(!a.chat.companion.page.equals("내 정보"))throw new AssertionError("companion settings missing");checks++;
   i.runOnMainSync(()->a.chat.companion.select("대화"));
   store.deleteGoal(id);id=null;i.runOnMainSync(()->a.chat.save());if(store.goals().stream().anyMatch(g->g.optString("id").equals(gid)))throw new AssertionError("deleted goal resurrected on pause save");checks++;
  }finally{i.getTargetContext().getSharedPreferences("nubi_display",0).edit().putBoolean("companion_ui",oldCompanion).commit();if(activity!=null){final Activity a=activity;i.runOnMainSync(a::finish);i.waitForIdleSync();}for(String clean:new String[]{id,otherId})if(clean!=null)try(GoalStore s=new GoalStore(i.getTargetContext())){s.deleteGoal(clean);}}
  return checks;
 }
}
