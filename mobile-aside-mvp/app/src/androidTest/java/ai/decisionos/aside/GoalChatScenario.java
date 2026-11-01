package ai.decisionos.aside;
import android.app.*;import android.content.*;import android.os.Bundle;import org.json.*;import java.io.*;
/** Live opt-in scenario: enter a native chat message and click the same Send button as a user. */
final class GoalChatScenario {
 static void run(Instrumentation i,Bundle args){Bundle result=new Bundle();GoalAgentActivity a=null;try(GoalStore store=new GoalStore(i.getTargetContext())){
  String character=args.getString("chatGoal"),task=args.getString("chatTask");GoalRules.preset(character);JSONObject goal=null;for(JSONObject g:store.goals())if(g.optString("character").equals(character)){goal=g;break;}if(goal==null)throw new AssertionError("Select/create the user goal first");String id=goal.getString("id");int before=goal.optJSONArray("chatMessages")==null?0:goal.getJSONArray("chatMessages").length();
  a=(GoalAgentActivity)i.startActivitySync(new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("goal_id",id).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));i.waitForIdleSync();final GoalAgentActivity activity=a;
  i.runOnMainSync(()->{activity.chat.input.setText(task);activity.chat.send.performClick();});
  boolean ended=false;for(int n=0;n<420;n++){Thread.sleep(1000);final boolean[] done={false};i.runOnMainSync(()->done[0]=!activity.chat.running&&!activity.chat.submitting&&activity.chat.history.length()>=Math.min(before+2,40));if(done[0]){ended=true;break;}}
  if(!ended){i.runOnMainSync(()->activity.chat.cancel());throw new AssertionError("live chat scenario timed out");}
  JSONObject saved=store.goal(id);JSONArray messages=saved.getJSONArray("chatMessages");JSONObject last=messages.getJSONObject(messages.length()-1);
  if(!last.optString("state").equals("completed"))throw new AssertionError(last.toString());boolean campus=java.util.regex.Pattern.compile("UNIST|유니스트|학사|장학|학교\\s*(공지|메일|포털)|수강|예비수강|COOP|인턴십|Outlook|아웃룩",java.util.regex.Pattern.CASE_INSENSITIVE).matcher(task).find();if(!campus&&!saved.optString("qwenSummary").equals(last.optString("text"))&&!saved.optString("qwenSummary").replace("\\n","\n").replace("\\\"","\"").equals(last.optString("text")))throw new AssertionError("Saved chat/goal summary mismatch");if(campus&&last.optString("text").trim().isEmpty())throw new AssertionError("Campus response missing");
  result.putString("stream","PASS app chat "+character+" goal="+id+"\n"+last.toString()+"\n");result.putString("goal_id",id);result.putString("state",last.optString("state"));
  try{android.graphics.Bitmap shot=i.getUiAutomation().takeScreenshot();try(OutputStream f=new FileOutputStream(new File(i.getTargetContext().getCacheDir(),"chat-"+character+".png"))){shot.compress(android.graphics.Bitmap.CompressFormat.PNG,100,f);}shot.recycle();}catch(Exception ignored){}
  i.finish(-1,result);
 }catch(Throwable e){result.putString("stream","FAIL "+e.getClass().getSimpleName()+": "+e.getMessage()+"\n");i.finish(0,result);}}
}
