package ai.decisionos.aside;
import android.content.*;import android.os.*;import org.json.*;
final class GroupContractChecks {
 static void run(GoalInstrumentation i){Bundle out=new Bundle();Context c=i.getTargetContext();String old=c.getSharedPreferences("group_rooms",0).getString("selected","");String id="";try(GoalStore s=new GoalStore(c)){
 JSONObject room=GroupRooms.latest(c,true);id=room.optString("id");i.check(GroupRooms.isGroup(room),"group room typed");String gid=room.optString("goalId");JSONObject individual=s.defaultConversation(gid);i.check(!GroupRooms.isGroup(individual)&&!id.equals(individual.optString("id")),"individual goal context isolated");
 JSONArray manual=new JSONArray();manual.put(new JSONObject().put("id","manual-user").put("role","user").put("text","단체방 컨텍스트"));GroupRooms.save(c,id,manual,null);
 JSONObject work=new JSONObject().put("id",java.util.UUID.randomUUID().toString()).put("conversation_id",id).put("prompt","자동 입력 테스트");GroupRooms.append(c,work,null);GroupRooms.append(c,work,null);i.check(s.workspaceRow("conversations",id).getJSONArray("messages").length()==3,"duplicate automatic input idempotent");
 GroupRooms.save(c,id,manual,null);i.check(s.workspaceRow("conversations",id).getJSONArray("messages").length()==3,"stale UI save preserves automatic work");
 JSONArray replies=new JSONArray().put(new JSONObject().put("role","grades").put("text","실제 모델 결과 자리").put("model","fixture"));JSONObject result=new JSONObject().put("state","completed").put("messages",replies);GroupRooms.append(c,work,result);GroupRooms.append(c,work,result);i.check(s.workspaceRow("conversations",id).getJSONArray("messages").length()==3,"result retries do not duplicate messages");
 i.check(!s.workspaceRow("conversations",individual.optString("id")).optString("messages").contains("자동 입력 테스트"),"group messages never leak into individual history");try{GroupRooms.save(c,individual.optString("id"),manual,null);throw new AssertionError("individual write accepted");}catch(IllegalArgumentException expected){i.check(true,"group bridge rejects individual room");}
 try(ScheduledWorkStore w=new ScheduledWorkStore(c)){i.check(w.getReadableDatabase().getVersion()==4,"durable group schema migrated");}
 String req=java.util.UUID.randomUUID().toString();String stamp=java.time.LocalDateTime.now(java.time.ZoneId.of("Asia/Seoul")).plusDays(1).withSecond(0).withNano(0).toString();JSONObject scheduled=GroupSchedule.handle(c,id,req,stamp+"에 학식 메뉴 조회해줘. 알림 예약");i.check(!scheduled.getJSONArray("messages").getJSONObject(0).getBoolean("actual"),"device acknowledgement not mislabeled model output");String wid=c.getSharedPreferences("group_schedule",0).getString("request-"+req,"");try(ScheduledWorkStore w=new ScheduledWorkStore(c)){try{i.check(!wid.isEmpty()&&w.get(wid).optString("room_type").equals("group")&&w.get(wid).optString("conversation_id").equals(id),"chat schedule retains group ownership");GroupSchedule.handle(c,id,req,stamp+"에 학식 메뉴 조회해줘. 알림 예약");i.check(c.getSharedPreferences("group_schedule",0).getString("request-"+req,"").equals(wid),"schedule request deduplicated");i.check(GroupSchedule.handle(c,id,java.util.UUID.randomUUID().toString(),"학식 조회해줘")==null,"ordinary request proceeds to real Qwen");i.check(GroupSchedule.handle(c,id,java.util.UUID.randomUUID().toString(),"수업이 15:40에 끝나. 버스에 맞춰 몇 시에 나오면 되는지 알려줘")==null,"travel timing question is immediate, not scheduled");}finally{ScheduledWork.cancel(c,wid);w.getWritableDatabase().delete("work","id=?",new String[]{wid});c.getSharedPreferences("group_schedule",0).edit().remove("request-"+req).apply();}}
 i.check(GroupSchedule.handle(c,id,java.util.UUID.randomUUID().toString(),"내일 화요일 15:40 수업 끝나. 울산 KTX 시간 확인해줘")==null,"future travel query executes now rather than becoming reminder");i.check(GroupSchedule.handle(c,id,java.util.UUID.randomUUID().toString(),"기존 KTX 예약 취소해줘")==null,"train cancellation is not local reminder cancellation");
 String repeatRequest=java.util.UUID.randomUUID().toString();GroupSchedule.handle(c,id,repeatRequest,"매일 오전 11시 20분에 UNIST 점심 메뉴 확인해줘");String repeatId=c.getSharedPreferences("group_schedule",0).getString("request-"+repeatRequest,"");try(ScheduledWorkStore w=new ScheduledWorkStore(c)){String next="";try{JSONObject first=w.get(repeatId);i.check(first.optString("repeat_rule").equals("daily"),"natural daily schedule persisted");next=w.repeatNext(repeatId,System.currentTimeMillis());i.check(!next.isEmpty()&&w.repeatNext(repeatId,System.currentTimeMillis()).equals(next),"repeat generation idempotent");i.check(w.get(next).optLong("due_at")>first.optLong("due_at")&&id.equals(w.get(next).optString("conversation_id")),"next occurrence preserves time and group");JSONObject listed=GroupSchedule.handle(c,id,java.util.UUID.randomUUID().toString(),"예약한 일 목록 보여줘");i.check(listed.toString().contains("점심 메뉴"),"list stays in chat");GroupSchedule.handle(c,id,java.util.UUID.randomUUID().toString(),"예약 전부 취소");i.check(w.get(repeatId).optString("state").equals("CANCELLED")&&w.get(next).optString("state").equals("CANCELLED"),"cancel stops future recurrence");}finally{for(String x:new String[]{repeatId,next})if(!x.isEmpty()){ScheduledWork.cancel(c,x);w.getWritableDatabase().delete("work","id=?",new String[]{x});}c.getSharedPreferences("group_schedule",0).edit().remove("request-"+repeatRequest).apply();}}

 JSONObject labelRow=new JSONObject().put("roomType","group").put("title","누비와 친구들").put("messages",new JSONArray().put(new JSONObject().put("role","user").put("text","513번과 KTX 시간을 맞춰줘")));
 i.check(ConversationLabel.title(labelRow).equals("513번과 KTX 시간을 맞춰줘")&&ConversationLabel.kind(labelRow).equals("누비와 친구들"),"group history shows its actual topic and room type");
 labelRow.put("title","내가 정한 이름");i.check(ConversationLabel.title(labelRow).equals("내가 정한 이름"),"custom conversation title preserved");
 i.check(!GroupRooms.isGroup(individual)&&ConversationLabel.kind(individual).equals("개별 누비"),"individual history visibly distinguished");
 long timeNow=System.currentTimeMillis();
 long sameInstant=java.time.Instant.parse("2026-11-04T09:00:30Z").toEpochMilli();
 i.check(ChatTime.parse("2026-11-04T09:00:30Z 알림 예약",timeNow)==sameInstant,"UTC event preserves instant and seconds");
 i.check(ChatTime.parse("2026-11-04T18:00:30+09:00 알림 예약",timeNow)==sameInstant,"Korean offset event preserves instant");
 i.check(ChatTime.parse("2026-11-04T04:00:30-0500 알림 예약",timeNow)==sameInstant,"compact negative offset event preserves instant");
 i.check(ChatTime.parse("2026-11-04 18:00 알림 예약",timeNow)==java.time.Instant.parse("2026-11-04T09:00:00Z").toEpochMilli(),"local calendar timestamps remain Korean time");
 try{ChatTime.parse("2026-11-04T18:00+25:00 알림 예약",timeNow);throw new AssertionError("invalid offset accepted");}catch(java.time.DateTimeException expected){i.check(true,"invalid event offset rejected");}
 String utcRequest=java.util.UUID.randomUUID().toString();
 String utcEvent=java.time.Instant.ofEpochMilli(timeNow).plusSeconds(172800).toString();
 GroupSchedule.handle(c,id,utcRequest,utcEvent+" 과제 마감 1시간 전에 테스트 과제 확인해줘");
 String utcId=c.getSharedPreferences("group_schedule",0).getString("request-"+utcRequest,"");
 try(ScheduledWorkStore w=new ScheduledWorkStore(c)){try{
  i.check(!utcId.isEmpty()&&w.get(utcId).optLong("due_at")==java.time.Instant.parse(utcEvent).toEpochMilli()-3600000,"UTC deadline stored at true T minus one hour");
  i.check(w.get(utcId).optString("conversation_id").equals(id),"imported calendar event retains original chat");
 }finally{ScheduledWork.cancel(c,utcId);w.getWritableDatabase().delete("work","id=?",new String[]{utcId});c.getSharedPreferences("group_schedule",0).edit().remove("request-"+utcRequest).apply();}}
 for(String timing:new String[]{"과제 마감 1시간 전에 테스트 과제 확인해줘","Zoom 수업 15분 전에 깨워줘"}){
  String offsetRequest=java.util.UUID.randomUUID().toString();String absolute=java.time.LocalDateTime.now(ChatTime.SEOUL).plusDays(2).withHour(18).withMinute(0).withSecond(0).withNano(0).toString();
  GroupSchedule.handle(c,id,offsetRequest,absolute+" "+timing);
  String offsetId=c.getSharedPreferences("group_schedule",0).getString("request-"+offsetRequest,"");
  try(ScheduledWorkStore w=new ScheduledWorkStore(c)){try{
   long base=java.time.LocalDateTime.parse(absolute).atZone(ChatTime.SEOUL).toInstant().toEpochMilli();long offset=timing.startsWith("과제")?3600000:900000;
   i.check(!offsetId.isEmpty()&&w.get(offsetId).optLong("due_at")==base-offset,"exact deadline offset "+offset);
   i.check(w.get(offsetId).optString("conversation_id").equals(id),"deadline keeps original group conversation");
  }finally{ScheduledWork.cancel(c,offsetId);w.getWritableDatabase().delete("work","id=?",new String[]{offsetId});c.getSharedPreferences("group_schedule",0).edit().remove("request-"+offsetRequest).apply();}}
 }
 out.putString("stream","PASS "+i.checks+" group ownership and persistence checks\n");
 }catch(Throwable e){out.putString("stream","FAIL "+e+"\n");}finally{if(!id.isEmpty())try(GoalStore s=new GoalStore(c)){s.getWritableDatabase().delete("conversations","id=?",new String[]{id});}c.getSharedPreferences("group_rooms",0).edit().putString("selected",old).commit();}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
