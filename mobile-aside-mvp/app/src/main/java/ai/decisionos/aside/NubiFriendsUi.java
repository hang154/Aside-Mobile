package ai.decisionos.aside;
import android.app.*;import android.content.*;import android.widget.*;import org.json.*;import java.util.UUID;
/** User-approved companion proposals, encrypted persistent account identity. */
final class NubiFriendsUi {
 final NubiCompanionUi u;JSONObject identity;
 NubiFriendsUi(NubiCompanionUi u){this.u=u;}
 void show(){
  u.sideBody.addView(u.text("친구 · 누비끼리 대화",22,true));
  u.muted("초대 코드로 연결한 친구에게 약속을 제안하고, 받은 제안에 응답해요.");
  try{String s=FriendIdentity.load(u.a);identity=s==null?null:new JSONObject(s);}catch(Exception e){u.muted("계정 정보를 열지 못했어요.");return;}
  if(identity==null){u.add("내 친구 계정 만들기","친구에게 표시할 이름을 정해요.",()->input("내 이름",name->{JSONObject b=new JSONObject();GoalStore.put(b,"action","register");GoalStore.put(b,"name",name);u.a.relay.friends(b,out->{if(error(out))return;try{FriendIdentity.save(u.a,out.toString());u.refresh();}catch(Exception e){u.a.toast("계정 저장 실패");}});}));return;}
  u.muted(identity.optString("name"));
  u.add("친구 초대 코드 만들기","10분 동안 유효하고 한 번만 사용할 수 있어요.",()->call("invite",new JSONObject(),out->{if(error(out))return;String code=out.optString("invite");new AlertDialog.Builder(u.a).setTitle("친구에게 초대 코드 전달").setMessage(code).setPositiveButton("복사",(d,w)->{android.content.ClipboardManager cb=(android.content.ClipboardManager)u.a.getSystemService(Context.CLIPBOARD_SERVICE);cb.setPrimaryClip(ClipData.newPlainText("누비 초대",code));}).setNegativeButton("닫기",null).show();}));
  u.add("받은 초대 코드로 연결","상대가 만든 초대 코드를 입력해요.",()->input("초대 코드",code->{JSONObject b=new JSONObject();GoalStore.put(b,"invite",code.trim());call("accept",b,out->{if(!error(out))u.refresh();});}));
  call("list",new JSONObject(),out->{if(error(out)||!u.page.equals("친구"))return;JSONArray friends=out.optJSONArray("friends"),messages=out.optJSONArray("messages");
   if(friends!=null&&friends.length()==0)u.muted("아직 연결된 친구가 없어요.");
   for(int i=0;friends!=null&&i<friends.length();i++){JSONObject f=friends.optJSONObject(i);if(f==null)continue;u.add(f.optString("name"),"연결된 친구 · 약속과 모임 제안",()->input("친구 누비에게 부탁할 일",instruction->{JSONObject req=new JSONObject();GoalStore.put(req,"instruction",instruction);u.a.toast("Qwen이 제안을 작성하고 있어요");call("draft",req,draft->{if(error(draft))return;String text=draft.optString("draft");JSONObject b=new JSONObject();GoalStore.put(b,"recipient",f.optString("id"));GoalStore.put(b,"text",text);GoalStore.put(b,"message_id",UUID.randomUUID().toString());new AlertDialog.Builder(u.a).setTitle("Qwen 제안 · 전송 전 확인").setMessage(text).setPositiveButton("보내기",(d,w)->call("send",b,r->{if(!error(r))u.refresh();})).setNegativeButton("취소",null).show();});}));}
   for(int i=0;messages!=null&&i<messages.length();i++){JSONObject m=messages.optJSONObject(i);if(m==null)continue;boolean incoming=m.optString("recipient").equals(identity.optString("account_id"));String state=m.optString("state");u.add((incoming?"받은 제안":"보낸 제안")+" · "+(state.equals("accepted")?"수락":state.equals("declined")?"거절":"응답 대기"),m.optString("text"),incoming&&state.equals("proposed")?()->new AlertDialog.Builder(u.a).setTitle("제안에 응답하기").setMessage(m.optString("text")).setPositiveButton("수락",(d,w)->respond(m,"accepted")).setNegativeButton("거절",(d,w)->respond(m,"declined")).setNeutralButton("나중에",null).show():null);}
  });
 }
 boolean error(JSONObject o){if(!o.has("error"))return false;u.a.toast(o.optString("error"));return true;}
 void respond(JSONObject m,String state){JSONObject b=new JSONObject();GoalStore.put(b,"message_id",m.optString("id"));GoalStore.put(b,"state",state);call("respond",b,r->{if(!error(r))u.refresh();});}
 void call(String action,JSONObject b,GoalAgentRelay.Response callback){GoalStore.put(b,"action",action);GoalStore.put(b,"account_id",identity.optString("account_id"));GoalStore.put(b,"account_key",identity.optString("account_key"));u.a.relay.friends(b,callback);}
 interface Input{void value(String s);}
 void input(String title,Input callback){EditText e=new EditText(u.a);e.setMaxLines(6);new AlertDialog.Builder(u.a).setTitle(title).setView(e).setPositiveButton("확인",(d,w)->{String s=e.getText().toString().trim();if(!s.isEmpty())callback.value(s);}).setNegativeButton("취소",null).show();}
}
