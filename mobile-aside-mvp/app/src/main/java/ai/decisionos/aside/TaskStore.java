package ai.decisionos.aside;
import android.content.Context;
import android.database.sqlite.*;
/** v2 preserves all existing tasks; legacy rows remain in the unassigned inbox. */
public final class TaskStore extends SQLiteOpenHelper {
 public TaskStore(Context c){super(c,"aside_tasks.db",null,3);}
 public void onCreate(SQLiteDatabase d){d.execSQL("CREATE TABLE tasks (_id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,kind TEXT NOT NULL,state TEXT NOT NULL,updated INTEGER NOT NULL,goal_id TEXT,source_url TEXT,due TEXT,start_at TEXT,end_at TEXT,timezone TEXT,is_all_day INTEGER NOT NULL DEFAULT 1,source_run TEXT)");}
 public void onUpgrade(SQLiteDatabase d,int o,int n){if(o<2){d.execSQL("ALTER TABLE tasks ADD COLUMN goal_id TEXT");d.execSQL("ALTER TABLE tasks ADD COLUMN source_url TEXT");d.execSQL("ALTER TABLE tasks ADD COLUMN due TEXT");}if(o<3){d.execSQL("ALTER TABLE tasks ADD COLUMN start_at TEXT");d.execSQL("ALTER TABLE tasks ADD COLUMN end_at TEXT");d.execSQL("ALTER TABLE tasks ADD COLUMN timezone TEXT");d.execSQL("ALTER TABLE tasks ADD COLUMN is_all_day INTEGER NOT NULL DEFAULT 1");d.execSQL("ALTER TABLE tasks ADD COLUMN source_run TEXT");}}
}
