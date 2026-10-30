package ai.decisionos.aside;

import android.app.KeyguardManager;
import android.content.ContentValues;
import android.content.Context;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.os.PowerManager;
import android.view.accessibility.AccessibilityManager;
import android.accessibilityservice.AccessibilityServiceInfo;
import java.util.HashSet;
import java.util.Set;

/** Metadata-only local collection; callers never pass content, labels or URLs. */
public final class CollectorStore {
    static final String PREFS="engagement_collection", ACTIVE="active", APPS="apps";
    private static final long RETAIN_MS=24L*60*60*1000;
    public static SharedPreferences prefs(Context c){return c.getSharedPreferences(PREFS,Context.MODE_PRIVATE);}
    public static boolean serviceEnabled(Context c){AccessibilityManager a=(AccessibilityManager)c.getSystemService(Context.ACCESSIBILITY_SERVICE);if(a==null)return false;for(AccessibilityServiceInfo i:a.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK)){android.content.pm.ServiceInfo s=i.getResolveInfo().serviceInfo;if(s!=null && c.getPackageName().equals(s.packageName) && EngagementService.class.getName().equals(s.name))return true;}return false;}
    public static boolean allowed(Context c,String pkg){
        if(pkg==null || !serviceEnabled(c) || !prefs(c).getBoolean(ACTIVE,false) || !prefs(c).getStringSet(APPS,new HashSet<>()).contains(pkg))return false;
        PowerManager p=(PowerManager)c.getSystemService(Context.POWER_SERVICE);KeyguardManager k=(KeyguardManager)c.getSystemService(Context.KEYGUARD_SERVICE);
        return p!=null && p.isInteractive() && k!=null && !k.isKeyguardLocked();
    }
    public static synchronized void record(Context c,String pkg,String kind,long duration){
        if(!allowed(c,pkg))return;
        if(!("window_open".equals(kind)||"window_end".equals(kind)||"click".equals(kind)||"scroll".equals(kind)||"web_page_open".equals(kind)||"web_page_end".equals(kind)||"web_touch".equals(kind)))return;
        long now=System.currentTimeMillis();try(Db db=new Db(c)){SQLiteDatabase sql=db.getWritableDatabase();sql.beginTransaction();try{
            sql.delete("events","wall_ms < ?",new String[]{Long.toString(now-RETAIN_MS)});
            ContentValues row=new ContentValues();row.put("wall_ms",now);row.put("pkg",pkg);row.put("kind",kind);row.put("duration_ms",Math.max(0,Math.min(duration,86400000L)));sql.insertOrThrow("events",null,row);
            sql.execSQL("DELETE FROM events WHERE _id NOT IN (SELECT _id FROM events ORDER BY _id DESC LIMIT 5000)");sql.setTransactionSuccessful();
        }finally{sql.endTransaction();}}
    }
    public static synchronized String summary(Context c){try(Db db=new Db(c)){SQLiteDatabase sql=db.getWritableDatabase();sql.delete("events","wall_ms < ?",new String[]{Long.toString(System.currentTimeMillis()-RETAIN_MS)});StringBuilder out=new StringBuilder();try(Cursor rows=sql.rawQuery("SELECT kind,COUNT(*) FROM events GROUP BY kind ORDER BY kind",null)){while(rows.moveToNext())out.append(rows.getString(0)).append(": ").append(rows.getInt(1)).append("건\n");}return out.length()==0?"저장된 기록 없음":out.toString();}}
    public static synchronized void clear(Context c){try(Db db=new Db(c)){db.getWritableDatabase().delete("events",null,null);}}
    public static Set<String> apps(Context c){return new HashSet<>(prefs(c).getStringSet(APPS,new HashSet<>()));}
    private static final class Db extends SQLiteOpenHelper {Db(Context c){super(c,"engagement_events.db",null,1);}public void onCreate(SQLiteDatabase db){db.execSQL("CREATE TABLE events (_id INTEGER PRIMARY KEY AUTOINCREMENT,wall_ms INTEGER NOT NULL,pkg TEXT NOT NULL,kind TEXT NOT NULL,duration_ms INTEGER NOT NULL)");}public void onUpgrade(SQLiteDatabase db,int o,int n){}}
    private CollectorStore(){}
}
