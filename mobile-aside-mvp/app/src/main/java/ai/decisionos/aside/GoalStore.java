package ai.decisionos.aside;
import android.content.*;
import android.database.Cursor;
import android.database.sqlite.*;
import org.json.*;
import java.util.*;

/** Device-owned repository. IDs are never trusted without goal ownership lookup. */
public final class GoalStore extends SQLiteOpenHelper {
 final boolean analytics;
 public GoalStore(Context c){super(c,"nubi_goals.db",null,2);analytics=c.getSharedPreferences("nubi_privacy",0).getBoolean("analytics",false);}
 @Override public void onConfigure(SQLiteDatabase d){d.setForeignKeyConstraintsEnabled(true);}
 public void onCreate(SQLiteDatabase d){
  d.execSQL("CREATE TABLE goals(id TEXT PRIMARY KEY,owner TEXT NOT NULL,character TEXT NOT NULL,title TEXT NOT NULL,data TEXT NOT NULL,updated INTEGER NOT NULL)");
  for(String t:new String[]{"contents","needs","products","offers","intents","profiles","alerts"})d.execSQL("CREATE TABLE "+t+"(id TEXT PRIMARY KEY,goal TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,data TEXT NOT NULL,updated INTEGER NOT NULL)");
  d.execSQL("CREATE TABLE events(id INTEGER PRIMARY KEY,goal TEXT,name TEXT NOT NULL,at INTEGER NOT NULL)");
 }
 public void onUpgrade(SQLiteDatabase d,int o,int n){if(o<2)d.execSQL("CREATE TABLE products(id TEXT PRIMARY KEY,goal TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,data TEXT NOT NULL,updated INTEGER NOT NULL)");}
 static JSONObject json(String text){try{return new JSONObject(text);}catch(Exception e){return new JSONObject();}}
 static JSONObject put(JSONObject j,String k,Object v){try{j.put(k,v);}catch(Exception e){throw new IllegalArgumentException(e);}return j;}
 public JSONObject create(String character,String title,String topic,long budget){GoalRules.preset(character);if(title==null||title.trim().isEmpty()||title.length()>100||budget<0)throw new IllegalArgumentException("Invalid goal");String id=UUID.randomUUID().toString();JSONObject j=new JSONObject();put(j,"id",id);put(j,"character",character);put(j,"title",title.trim());put(j,"topic",topic);put(j,"budget",budget);put(j,"motivation",true);put(j,"information",true);put(j,"language","ko");put(j,"tab",0);put(j,"status","active");put(j,"timezone","Asia/Seoul");put(j,"version",1);put(j,"public",false);put(j,"alerts",false);insertGoal(j);event(id,"goal_created");return j;}
 public JSONObject goal(String id){try(Cursor c=getReadableDatabase().rawQuery("SELECT data FROM goals WHERE id=? AND owner='device'",new String[]{id})){if(!c.moveToFirst())throw new IllegalArgumentException("Goal not owned by device");return json(c.getString(0));}}
 public List<JSONObject> goals(){List<JSONObject> a=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT data FROM goals WHERE owner='device' ORDER BY updated DESC",null)){while(c.moveToNext())a.add(json(c.getString(0)));}return a;}
 private ContentValues goalValues(JSONObject j){ContentValues v=new ContentValues();v.put("id",j.optString("id"));v.put("owner","device");v.put("character",j.optString("character"));v.put("title",j.optString("title"));v.put("data",j.toString());v.put("updated",System.currentTimeMillis());return v;}
 private void insertGoal(JSONObject j){getWritableDatabase().insertOrThrow("goals",null,goalValues(j));}
 public void saveGoal(JSONObject j){if(getWritableDatabase().update("goals",goalValues(j),"id=? AND owner='device'",new String[]{j.optString("id")})!=1)throw new IllegalArgumentException("Deleted or foreign goal");}
 public void patchGoal(String id,JSONObject patch){SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try{JSONObject current=goal(id);java.util.Iterator<String> keys=patch.keys();while(keys.hasNext()){String k=keys.next();if(!k.equals("id")&&!k.equals("owner"))put(current,k,patch.opt(k));}saveGoal(current);d.setTransactionSuccessful();}finally{d.endTransaction();}}
 private void table(String t){if(!Arrays.asList("contents","needs","products","offers","intents","profiles","alerts").contains(t))throw new IllegalArgumentException("Unknown table");}
 public String save(String table,String gid,JSONObject j){table(table);goal(gid);String id=j.optString("id");if(id.isEmpty())id=UUID.randomUUID().toString();put(j,"id",id);put(j,"goalId",gid);ContentValues v=new ContentValues();v.put("id",id);v.put("goal",gid);v.put("data",j.toString());v.put("updated",System.currentTimeMillis());SQLiteDatabase d=getWritableDatabase();try(Cursor c=d.rawQuery("SELECT goal FROM "+table+" WHERE id=?",new String[]{id})){if(c.moveToFirst()&&!gid.equals(c.getString(0)))throw new IllegalArgumentException("Foreign goal record");}if(d.update(table,v,"id=? AND goal=?",new String[]{id,gid})==0)d.insertOrThrow(table,null,v);return id;}
 public List<JSONObject> list(String t,String gid){table(t);goal(gid);List<JSONObject> a=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT data FROM "+t+" WHERE goal=? ORDER BY updated DESC LIMIT 200",new String[]{gid})){while(c.moveToNext())a.add(json(c.getString(0)));}return a;}
 /** Filter before the display cap: older saved rows remain reachable across searches. */
 public List<JSONObject> contents(String gid,String query,boolean savedOnly){goal(gid);List<JSONObject> out=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT data FROM contents WHERE goal=? ORDER BY updated DESC",new String[]{gid})){while(c.moveToNext()&&out.size()<200){JSONObject row=json(c.getString(0));if(row.optBoolean("hidden"))continue;if(savedOnly?!row.optBoolean("saved"):!query.equals(row.optString("query")))continue;out.add(row);}}return out;}
 public void remove(String t,String gid,String id){table(t);goal(gid);getWritableDatabase().delete(t,"id=? AND goal=?",new String[]{id,gid});}
 public void event(String gid,String name){if(!analytics)return;if(!Arrays.asList("goal_created","workspace_opened","media_saved","media_hidden","need_confirmed","comparison_started","offer_selected","checkout_handoff","purchase_self_reported","goal_deleted").contains(name))return;ContentValues v=new ContentValues();v.put("goal",gid);v.put("name",name);v.put("at",System.currentTimeMillis());getWritableDatabase().insert("events",null,v);getWritableDatabase().execSQL("DELETE FROM events WHERE id NOT IN (SELECT id FROM events ORDER BY id DESC LIMIT 2000)");}
 public void deleteGoal(String id){goal(id);getWritableDatabase().delete("events","goal=?",new String[]{id});getWritableDatabase().delete("goals","id=? AND owner='device'",new String[]{id});}
 public void clear(){SQLiteDatabase d=getWritableDatabase();d.delete("goals",null,null);d.delete("events",null,null);}
}
