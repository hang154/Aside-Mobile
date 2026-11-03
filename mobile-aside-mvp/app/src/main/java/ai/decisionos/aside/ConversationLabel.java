package ai.decisionos.aside;
import org.json.*;
/** Read-only history presentation; never renames or merges stored conversations. */
final class ConversationLabel {
 static String title(JSONObject row){
  String title=row.optString("title");
  if(GroupRooms.isGroup(row)&&title.equals("누비와 친구들")){
   JSONArray messages=row.optJSONArray("messages");
   for(int n=0;messages!=null&&n<messages.length();n++){
    JSONObject m=messages.optJSONObject(n);
    if(m!=null&&m.optString("role").equals("user")&&!m.optString("text").isBlank()){
     String text=m.optString("text").replaceAll("\\s+"," ").trim().replaceFirst("^\\d+\\s*(?:초|분|시간)\\s*(?:후|뒤)\\s*","");
     int count=text.codePointCount(0,text.length());
     return count>30?text.substring(0,text.offsetByCodePoints(0,30))+"…":text;
    }
   }
  }
  return title;
 }
 static String kind(JSONObject row){return GroupRooms.isGroup(row)?"누비와 친구들":"개별 누비";}
}
