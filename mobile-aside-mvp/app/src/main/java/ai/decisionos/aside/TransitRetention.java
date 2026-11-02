package ai.decisionos.aside;
import org.json.*;import java.util.*;
/** TMAP results are never reused after their server supplied expiry (23h, below the 24h provider limit). */
final class TransitRetention {
 static void clean(Object value,long now){if(value instanceof JSONArray){JSONArray a=(JSONArray)value;for(int n=0;n<a.length();n++)clean(a.opt(n),now);}else if(value instanceof JSONObject){JSONObject o=(JSONObject)value;long expiry=o.optLong("expiresAt");if(expiry>0&&now>=expiry){for(String key:new String[]{"text","answer","task"})if(o.has(key))GoalStore.put(o,key,"경로 결과의 보관 시간이 지났어요. 새로 조회해 주세요.");for(String key:new String[]{"items","steps"})if(o.has(key))GoalStore.put(o,key,new JSONArray());}Iterator<String> keys=o.keys();List<String> list=new ArrayList<>();while(keys.hasNext())list.add(keys.next());for(String k:list)clean(o.opt(k),now);}}
 static long next(JSONArray history,long now){long next=Long.MAX_VALUE;for(int n=0;n<history.length();n++){JSONObject m=history.optJSONObject(n);long expiry=m==null?0:m.optLong("expiresAt");if(expiry>now)next=Math.min(next,expiry);}return next;}
}
