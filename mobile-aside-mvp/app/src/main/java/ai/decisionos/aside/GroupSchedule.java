package ai.decisionos.aside;
import android.content.*;import org.json.*;import java.time.*;import java.time.format.*;import java.util.*;
/** Device-owned schedules use the same group conversation as manual requests. */
final class GroupSchedule {
 static JSONObject reply(String request,String text)throws JSONException{return new JSONObject().put("request_id",request).put("state","completed").put("messages",new JSONArray().put(new JSONObject().put("role","nubi").put("text",text).put("actual",false).put("model","기기 예약")));}
 static JSONObject handle(Context c,String roomId,String request,String input)throws Exception {
  android.content.SharedPreferences drafts=c.getSharedPreferences("group_schedule",0);String previous=drafts.getString("draft-"+roomId,"");
  boolean list=input.matches("(?s).*(예약한 일|예약 작업|예약 알림|맡긴 일).*(목록|보여|확인).*"),cancel=input.matches("(?s).*(알림|맡긴 일|예약한 일|반복 예약|자동 실행).*(취소).*")||input.matches("예약\\s*(전부|모두)?\\s*취소"),schedule=input.matches("(?is).*(알림\\s*예약|자동\\s*실행\\s*예약|마감.*(?:1시간 전|한 시간 전)|(?:줌|Zoom).*(?:15분 전)|깨워\\s*줘|(?:매일|매주|평일마다).*(?:알려|확인|조회)|(?:분 후|초 후|시간 후|[0-9]+\\s*시에|[0-9]+\\s*분에|[0-9]:[0-9]{2}에).*(?:알려줘|확인해줘|실행해줘)).*");
  if(input.matches("(?s).*(몇\\s*시|언제).*(나오|나가|출발|도착|타면).*" )&&!input.matches("(?s).*(알림\\s*예약|자동\\s*실행\\s*예약|깨워\\s*줘).*"))schedule=false;
  if(list||cancel){ArrayList<JSONObject> rows=new ArrayList<>();try(ScheduledWorkStore s=new ScheduledWorkStore(c)){for(JSONObject r:s.list())if(roomId.equals(r.optString("conversation_id"))&&r.optString("state").equals("SCHEDULED"))rows.add(r);}
   if(list){StringBuilder text=new StringBuilder(rows.isEmpty()?"지금 이 방에 예약한 일은 없어.":"이 방에 맡긴 일이야.");for(JSONObject r:rows)text.append("\n").append(label(r.optLong("due_at"))).append(" · ").append(r.optString("title"));return reply(request,text.toString());}
   List<JSONObject> selected=new ArrayList<>();for(JSONObject r:rows)if(input.contains(r.optString("title"))||rows.size()==1||input.contains("전부")||input.contains("모두"))selected.add(r);if(selected.isEmpty())return reply(request,"어떤 예약을 취소할까? ‘예약한 일 목록 보여줘’로 확인할 수 있어.");for(JSONObject r:selected)ScheduledWork.cancel(c,r.optString("id"));return reply(request,selected.size()+"개 예약을 취소했어.");
  }
  long now=System.currentTimeMillis(),parsed=0;try{parsed=ChatTime.parse(input,now);}catch(Exception ignored){}
  boolean continuation=!previous.isEmpty()&&parsed>0;if(!schedule&&!continuation)return null;String prompt=continuation?previous+" "+input:input;
  long due;try{due=ChatTime.parse(prompt,now);}catch(Exception e){return reply(request,"날짜와 시각을 다시 알려줘. 예를 들면 ‘내일 오전 11시 20분’처럼 보내면 돼.");}
  String repeat=ChatTime.repeat(prompt);
  if(due==0){drafts.edit().putString("draft-"+roomId,prompt).apply();return reply(request,"언제 시작할까? ‘내일 오전 11시 20분’처럼 알려줘.");}
  if(prompt.contains("1시간 전")||prompt.contains("한 시간 전"))due-=3600000;else if(prompt.contains("15분 전"))due-=900000;
  if(!repeat.isEmpty()&&(due<=now||(repeat.equals("weekdays")&&Instant.ofEpochMilli(due).atZone(ChatTime.SEOUL).getDayOfWeek().getValue()>5)))due=ChatTime.next(due,repeat,now);
  if(due<=now)return reply(request,"시작할 시간이 지났어. 다음 날짜와 시각을 알려줘.");
  JSONObject room;try(GoalStore s=new GoalStore(c)){room=s.workspaceRow("conversations",roomId);if(!GroupRooms.isGroup(room))throw new IllegalArgumentException();}
  String task=prompt.replaceFirst("\\d+\\s*(?:분|초|시간)\\s*(?:후|뒤)","").replace("알림 예약","").replace("알림예약","").replace("자동 실행 예약","").trim(),id=drafts.getString("request-"+request,"");
  try(ScheduledWorkStore s=new ScheduledWorkStore(c)){if(id.isEmpty()){id=s.create(room.optJSONObject("goals").optString("grades"),task.substring(0,Math.min(120,task.length())),task,"reminder","",due,now);s.metadata(id,"conversation_id",roomId);s.metadata(id,"room_type","group");s.metadata(id,"group_goals",room.optJSONObject("goals").toString());s.metadata(id,"repeat_rule",repeat);s.metadata(id,"series_id",id);drafts.edit().putString("request-"+request,id).apply();}}
  ScheduledWork.arm(c,id);drafts.edit().remove("draft-"+roomId).apply();return reply(request,label(due)+(repeat.isEmpty()?"에":"부터 "+(repeat.equals("daily")?"매일":repeat.equals("weekly")?"매주":"평일마다"))+" 이 방에서 시작할게. 진행과 결과도 여기 남겨둘게.");
 }
 static String label(long due){return DateTimeFormatter.ofPattern("M월 d일 HH:mm").withZone(ChatTime.SEOUL).format(Instant.ofEpochMilli(due));}
}
