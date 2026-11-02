package ai.decisionos.aside;
import android.app.*;import android.os.*;import android.content.*;import org.json.*;
/** Read-only reuse of existing school sessions. No credential input, submission or sending. */
final class SchoolLiveSsoChecks {
 static void run(GoalInstrumentation i){Bundle out=new Bundle();try{
 String id="";try(GoalStore s=new GoalStore(i.getTargetContext())){for(JSONObject g:s.goals())if(!GoalStore.fixture(g)&&g.optString("character").equals("grades")){id=g.optString("id");break;}}
 if(id.isEmpty())throw new IllegalStateException("Existing school agent required");
 GoalAgentActivity a=(GoalAgentActivity)i.startActivitySync(new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("goal_id",id).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));long began=System.currentTimeMillis();final SchoolSignIn[] flow={null};i.runOnMainSync(()->{flow[0]=new SchoolSignIn(a.chat);flow[0].show();flow[0].load();});
 long end=System.currentTimeMillis()+80000;boolean done=false;while(System.currentTimeMillis()<end){try(CampusFlowStore s=new CampusFlowStore(a)){done=true;for(String service:new String[]{"portal","blackboard","mail"}){JSONObject r=s.get("connection-"+service);done&=r.optLong("updated")>=began&&r.optString("state").equals("verified");}}if(done)break;Thread.sleep(1000);}
 for(String service:new String[]{"portal","blackboard","mail"})try(CampusFlowStore s=new CampusFlowStore(a)){JSONObject r=s.get("connection-"+service);i.check(r.optLong("updated")>=began&&r.optString("state").equals("verified"),"live silent session "+service);}
 out.putString("stream","PASS "+i.checks+" live portal/Blackboard/Outlook native session reuse checks; no credentials entered\n");
 }catch(Throwable t){out.putString("stream","FAIL "+t+"\n");}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
