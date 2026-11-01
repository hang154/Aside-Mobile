package ai.decisionos.aside;
import android.app.Instrumentation;import android.os.Bundle;import android.content.*;import android.database.*;import android.database.sqlite.*;import org.json.*;import java.io.*;
/** Run on a real device: migrations, ownership, deletion and persistence. Never touches browser sessions. */
public class GoalInstrumentation extends Instrumentation {
 Bundle scenario;
 int checks=0; void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
 public void onCreate(Bundle args){super.onCreate(args);scenario=args;start();}
 public void onStart(){if(scenario!=null&&scenario.containsKey("campusChecks")){Bundle b=new Bundle();try{if(scenario.containsKey("notifyTest"))CampusNoticeMonitor.notifyChanges(getTargetContext(),1,"누비 공지 알림 검증");if(!CampusNoticeMonitor.category("[학부] 장학생 선발").equals("장학"))throw new AssertionError("scholarship");if(!CampusNoticeMonitor.category("경북대 학점교류").equals("학점교류"))throw new AssertionError("exchange");if(!CampusNoticeMonitor.relevant("[UG, G] 공지","학부"))throw new AssertionError("mixed audience");if(CampusNoticeMonitor.relevant("[학부] 장학생 선발","대학원"))throw new AssertionError("audience filter");if(!CampusNoticeMonitor.relevant("장학 공지","대학원"))throw new AssertionError("unknown audience retained");b.putString("stream","PASS 5 campus categorization and audience checks\n");finish(-1,b);}catch(Throwable t){b.putString("stream","FAIL "+t+"\n");finish(0,b);}return;}if(scenario!=null&&scenario.containsKey("chatTask")){GoalChatScenario.run(this,scenario);return;}Bundle result=new Bundle();String error="";try{
  Context target=getTargetContext();
  try(GoalStore s=new GoalStore(target)){
   JSONObject a=s.create("fitness","INSTRUMENTATION_A","초보 운동",50000),b=s.create("home","INSTRUMENTATION_B","내 집 마련",0);String aid=a.optString("id"),bid=b.optString("id");
   try{
    check(!aid.equals(bid),"distinct goal IDs");check(s.goal(aid).optString("character").equals("fitness"),"same preset contract");check(!a.optBoolean("alerts")&&!a.optBoolean("public"),"private defaults");
    JSONObject row=new JSONObject();GoalStore.put(row,"id","instrumentation-row");GoalStore.put(row,"title","explicit selection");s.save("needs",aid,row);check(s.list("needs",aid).size()==1,"need persisted");boolean blocked=false;try{s.save("needs",bid,row);}catch(IllegalArgumentException e){blocked=true;}check(blocked,"cannot reassign a record to another goal");
    try(GoalStore reopened=new GoalStore(target)){check(reopened.goal(aid).optString("title").equals("INSTRUMENTATION_A"),"reopen persistence");check(reopened.list("needs",bid).isEmpty(),"goal isolation");}
    JSONObject profile=new JSONObject();GoalStore.put(profile,"consent",false);GoalStore.put(profile,"published",false);s.save("profiles",aid,profile);check(!s.list("profiles",aid).get(0).optBoolean("published"),"no public profile without server");s.deleteGoal(aid);check(s.getReadableDatabase().rawQuery("SELECT count(*) FROM needs WHERE goal=?",new String[]{aid}).moveToFirst(),"cascade query");try(Cursor c=s.getReadableDatabase().rawQuery("SELECT count(*) FROM needs WHERE goal=?",new String[]{aid})){c.moveToFirst();check(c.getInt(0)==0,"delete cascades");}
   }finally{for(String id:new String[]{aid,bid})try{s.deleteGoal(id);}catch(Exception ignored){}}
  }
  final File testDir=new File(target.getCacheDir(),"migration-test-"+System.nanoTime());testDir.mkdirs();
  Context scoped=new ContextWrapper(target){@Override public File getDatabasePath(String name){return new File(testDir,name);}@Override public SQLiteDatabase openOrCreateDatabase(String n,int mode,SQLiteDatabase.CursorFactory factory){return SQLiteDatabase.openOrCreateDatabase(getDatabasePath(n),factory);}@Override public SQLiteDatabase openOrCreateDatabase(String n,int mode,SQLiteDatabase.CursorFactory factory,DatabaseErrorHandler handler){return SQLiteDatabase.openOrCreateDatabase(getDatabasePath(n).getPath(),factory,handler);}};
  SQLiteDatabase old=SQLiteDatabase.openOrCreateDatabase(new File(testDir,"aside_tasks.db"),null);old.execSQL("CREATE TABLE tasks (_id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,kind TEXT NOT NULL,state TEXT NOT NULL,updated INTEGER NOT NULL)");old.execSQL("INSERT INTO tasks VALUES (42,'legacy task','검색·비교','대기',12345)");old.setVersion(1);old.close();
  try(TaskStore migrated=new TaskStore(scoped)){try(Cursor c=migrated.getReadableDatabase().rawQuery("SELECT _id,title,goal_id,source_url,due FROM tasks",null)){check(c.moveToFirst(),"legacy record preserved");check(c.getLong(0)==42&&c.getString(1).equals("legacy task"),"legacy fields preserved");check(c.isNull(2),"legacy goal stays unassigned");check(migrated.getReadableDatabase().getVersion()==2,"schema version 2");}ContentValues v=new ContentValues();v.put("title","goal task");v.put("kind","目标");v.put("state","대기");v.put("updated",1);v.put("goal_id","goal-a");migrated.getWritableDatabase().insertOrThrow("tasks",null,v);try(Cursor c=migrated.getReadableDatabase().rawQuery("SELECT count(*) FROM tasks",null)){c.moveToFirst();check(c.getInt(0)==2,"old and new coexist");}}
  for(File f:testDir.listFiles())f.delete();testDir.delete();
  checks+=GoalFlowChecks.run(this);
  checks+=GoalAgentChecks.run(this);
 }catch(Throwable t){error=t.getClass().getSimpleName()+": "+t.getMessage();}
 result.putString("stream",error.isEmpty()?"PASS "+checks+" real-device database and flow checks\n":"FAIL "+error+"\n");result.putInt("checks",checks);result.putString("error",error);finish(error.isEmpty()?-1:0,result);
 }
}
