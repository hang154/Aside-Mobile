package ai.decisionos.aside;
import android.content.Intent;import android.os.Bundle;import org.json.JSONObject;
/** Public launcher retains old deep links while opening the companion conversation by default. */
public class CampusActivity extends GoalHomeActivity {
 @Override public void onCreate(Bundle b){super.onCreate(b);if(b==null&&!getIntent().hasExtra("section")){JSONObject goal=null;for(JSONObject row:store.goals())if(!row.optString("title").startsWith("QWEN_")&&!row.optString("title").startsWith("INSTRUMENTATION")){goal=row;break;}if(goal==null){GoalRules.Preset p=GoalRules.preset("fitness");goal=store.create(p.id,p.title,p.topic,0);}startActivity(new Intent(this,GoalAgentActivity.class).putExtra("goal_id",goal.optString("id")));}}
}
