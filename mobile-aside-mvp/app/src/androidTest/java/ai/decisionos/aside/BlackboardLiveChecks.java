package ai.decisionos.aside;
import android.os.*;import android.content.*;import org.json.*;
final class BlackboardLiveChecks {
 static void run(GoalInstrumentation i){Bundle out=new Bundle();try{
 String id="";try(GoalStore s=new GoalStore(i.getTargetContext())){for(JSONObject g:s.goals())if(!GoalStore.fixture(g)&&g.optString("character").equals("grades")){id=g.optString("id");break;}}
 if(id.isEmpty())throw new IllegalStateException("Existing school agent required");
 GoalAgentActivity a=(GoalAgentActivity)i.startActivitySync(new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("goal_id",id).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));final BlackboardTools[] tool={null};i.runOnMainSync(()->{tool[0]=new BlackboardTools(a.chat);tool[0].request("calendar");});Thread.sleep(18000);
 final String[] result={null};i.runOnMainSync(()->tool[0].web.evaluateJavascript("NubiBBTools.run({mode:'calendar'}).then(r=>window.__bbLive=JSON.stringify({state:r.state,count:r.items.length})).catch(e=>window.__bbLive=JSON.stringify({error:String(e)}))",v->{}));Thread.sleep(6000);
 java.util.concurrent.CountDownLatch latch=new java.util.concurrent.CountDownLatch(1);i.runOnMainSync(()->tool[0].web.evaluateJavascript("window.__bbLive||null",v->{result[0]=v;latch.countDown();}));latch.await(5,java.util.concurrent.TimeUnit.SECONDS);if(result[0]==null||result[0].equals("null"))throw new AssertionError("Calendar response missing");String decoded=new JSONArray("["+result[0]+"]").getString(0);JSONObject r=new JSONObject(decoded);i.check(r.optString("state").equals("observed"),"authenticated real calendar API");i.check(r.optInt("count",-1)>=0,"actual calendar schema");
 i.runOnMainSync(()->tool[0].run("calendar",null,true));Thread.sleep(2500);
 try(java.io.FileOutputStream f=new java.io.FileOutputStream(new java.io.File(i.getTargetContext().getCacheDir(),"blackboard-live.png"))){i.getUiAutomation().takeScreenshot().compress(android.graphics.Bitmap.CompressFormat.PNG,100,f);}
 out.putString("stream","PASS "+i.checks+" actual Blackboard native calendar checks; source events="+r.optInt("count")+"\n");
 }catch(Throwable e){out.putString("stream","FAIL "+e+"\n");}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
