package ai.decisionos.aside;
import android.content.*;import android.database.*;import android.database.sqlite.*;import org.json.*;import java.util.*;
/** Isolated durable work queue; existing goal, calendar and browser stores remain unchanged. */
final class CampusFlowStore extends SQLiteOpenHelper {
 CampusFlowStore(Context c){super(c,"nubi_campus_flows.db",null,1);}
 public void onCreate(SQLiteDatabase db){db.execSQL("CREATE TABLE records (id TEXT PRIMARY KEY,kind TEXT NOT NULL,body TEXT NOT NULL,updated INTEGER NOT NULL)");}
 public void onUpgrade(SQLiteDatabase db,int o,int n){throw new IllegalStateException("Unsupported migration");}
 String save(String kind,JSONObject j){String id=j.optString("id",UUID.randomUUID().toString());GoalStore.put(j,"id",id);GoalStore.put(j,"updated",System.currentTimeMillis());ContentValues v=new ContentValues();v.put("id",id);v.put("kind",kind);v.put("body",j.toString());v.put("updated",j.optLong("updated"));getWritableDatabase().insertWithOnConflict("records",null,v,SQLiteDatabase.CONFLICT_REPLACE);return id;}
 JSONObject get(String id){try(Cursor c=getReadableDatabase().rawQuery("SELECT body FROM records WHERE id=?",new String[]{id})){if(c.moveToFirst())try{return new JSONObject(c.getString(0));}catch(Exception e){throw new IllegalStateException(e);}}return new JSONObject();}
 java.util.List<JSONObject> list(String kind){List<JSONObject> out=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT body FROM records WHERE kind=? ORDER BY updated DESC",new String[]{kind})){while(c.moveToNext())try{out.add(new JSONObject(c.getString(0)));}catch(Exception e){throw new IllegalStateException(e);}}return out;}
 void remove(String id){getWritableDatabase().delete("records","id=?",new String[]{id});}
 static boolean verifiedConnection(String id,String url,boolean passwordVisible,boolean evidence){try{String expected=android.net.Uri.parse(CampusWorkflows.service(id)[2]).getHost(),host=android.net.Uri.parse(url).getHost();return host!=null&&host.equals(expected)&&url.startsWith("https://")&&!passwordVisible&&evidence;}catch(Exception e){return false;}}
 static String state(JSONObject job){String s=job.optString("state");if(s.equals("requested"))return "누비에게 요청함 · 작업 기록 확인";if(s.equals("review"))return "초안 검토 중";if(s.equals("approved"))return "검토 완료 · 서비스에서 실행 필요";return "요청 초안";}
}
