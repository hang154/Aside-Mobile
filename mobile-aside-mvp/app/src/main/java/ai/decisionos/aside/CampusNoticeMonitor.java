package ai.decisionos.aside;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.job.JobInfo;
import android.app.job.JobParameters;
import android.app.job.JobScheduler;
import android.app.job.JobService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import org.json.JSONArray;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;

/** Best-effort periodic refresh of the selected portal home preview, using this app's WebView session. */
public final class CampusNoticeMonitor extends JobService {
 static final int JOB_ID=90145, NOW_JOB_ID=90146;
 static final String PREFS="campus_notice_monitor", CHANNEL="campus_notice_alerts";
 private WebView web;private JobParameters running;private Handler handler=new Handler(Looper.getMainLooper());private boolean done;private JSONArray combined=new JSONArray();
 static boolean schedule(Context c){
  JobScheduler scheduler=(JobScheduler)c.getSystemService(Context.JOB_SCHEDULER_SERVICE);
  JobInfo job=new JobInfo.Builder(JOB_ID,new ComponentName(c,CampusNoticeMonitor.class)).setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY).setPeriodic(6L*60*60*1000).setPersisted(true).build();
  boolean ok;try{ok=scheduler.schedule(job)==JobScheduler.RESULT_SUCCESS;}catch(SecurityException | IllegalStateException e){ok=false;}c.getSharedPreferences(PREFS,MODE_PRIVATE).edit().putBoolean("enabled",ok).apply();return ok;
 }
 static boolean scheduleNow(Context c){try{JobInfo j=new JobInfo.Builder(NOW_JOB_ID,new ComponentName(c,CampusNoticeMonitor.class)).setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY).setOverrideDeadline(10000).build();return ((JobScheduler)c.getSystemService(Context.JOB_SCHEDULER_SERVICE)).schedule(j)==JobScheduler.RESULT_SUCCESS;}catch(SecurityException | IllegalStateException e){return false;}}
 static void stop(Context c){((JobScheduler)c.getSystemService(Context.JOB_SCHEDULER_SERVICE)).cancel(JOB_ID);((JobScheduler)c.getSystemService(Context.JOB_SCHEDULER_SERVICE)).cancel(NOW_JOB_ID);c.getSharedPreferences(PREFS,MODE_PRIVATE).edit().putBoolean("enabled",false).apply();}
 static String category(String title){
  if(title.matches("(?is).*(장학|scholarship).*"))return "장학";
  if(title.matches("(?is).*(인턴|현장실습|intern).*"))return "인턴십";
  if(title.matches("(?is).*(학점\\s*교류|계절\\s*학기.*학점).*"))return "학점교류";
  if(title.matches("(?is).*(복학|휴학|중도포기).*"))return "학적";
  if(title.matches("(?is).*(수강|정원).*"))return "수강";
  if(title.matches("(?is).*(시험|기말).*"))return "시험";
  if(title.matches("(?is).*(졸업|학위논문).*"))return "졸업";
  if(title.matches("(?is).*(캠프|축제|축전|행사|강연|세미나).*"))return "행사";
  if(title.matches("(?is).*(화장실|사용\\s*불가).*"))return "시설";
  return "기타";
 }
 static String audience(String title){boolean ug=title.matches("(?is).*\\b(UG|undergraduate)\\b.*|.*\\[학부\\].*");boolean g=title.matches("(?is).*\\b(G|graduate)\\b.*|.*\\[대학원\\].*");if(ug&&g)return "전체";if(ug)return "학부";if(g)return "대학원";return "확인 필요";}
 static boolean relevant(String title,String level){String a=audience(title);return level.equals("전체")||a.equals("전체")||a.equals("확인 필요")||a.equals(level);}
 static String hash(String value){try{byte[] b=MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(java.util.Locale.US,"%02x",v&255));return s.toString();}catch(Exception e){throw new IllegalStateException(e);}}
 @Override public boolean onStartJob(JobParameters params){if(running!=null)return false;running=params;done=false;combined=new JSONArray();handler.post(()->startWeb());return true;}
 private void startWeb(){
  if(done)return;web=new WebView(this);web.measure(android.view.View.MeasureSpec.makeMeasureSpec(1080,android.view.View.MeasureSpec.EXACTLY),android.view.View.MeasureSpec.makeMeasureSpec(1600,android.view.View.MeasureSpec.EXACTLY));web.layout(0,0,1080,1600);web.getSettings().setJavaScriptEnabled(true);web.getSettings().setDomStorageEnabled(true);web.getSettings().setAllowFileAccess(false);web.getSettings().setAllowContentAccess(false);web.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  web.setWebViewClient(new WebViewClient(){@Override public void onPageFinished(WebView v,String url){if(url.startsWith("https://portal.unist.ac.kr/irj/"))handler.postDelayed(()->switchTab("전체공지",0),8000);}});
  handler.postDelayed(()->finish("시간 초과 · 포털을 열어 연결을 확인해 주세요.",true),45000);web.loadUrl("https://portal.unist.ac.kr/");
 }
 private void switchTab(String label,int phase){
  if(done||web==null)return;
  String js="(()=>{try{let f=document.querySelector('iframe[name=contentAreaFrame]');let d=f&&f.contentDocument;let a=d&&[...d.querySelectorAll('a')].find(x=>x.innerText.trim()==="+JSONObject.quote(label)+" && (x.getAttribute('href')||'').includes('go_board_switch'));if(!a)return false;a.click();return true}catch(e){return false}})()";
  web.evaluateJavascript(js,result->{if(done)return;if(!"true".equals(result)){finish("포털 공지 탭을 열지 못했어요. 로그인 상태를 확인해 주세요.",true);return;}handler.postDelayed(()->collect(0,phase),3500);});
 }
 private void collect(int attempt,int phase){
  if(done||web==null)return;
  String js="(()=>{try{if(location.hostname!=='portal.unist.ac.kr')return JSON.stringify({state:'signin'});let f=document.querySelector('iframe[name=contentAreaFrame]');let d=f&&f.contentDocument;if(!d)return JSON.stringify({state:'loading'});let rows=[...d.querySelectorAll('a[href*=go_board_view]')].filter(e=>e.getClientRects().length).map(e=>{let t=e.closest('tr'),c=t?[...t.querySelectorAll(':scope > td')]:[],m=(e.getAttribute('href')||'').match(/oid:(\\d+)\\^cabinetInstanceID:(\\d+)/);return m?{id:m[1],board:m[2],title:e.innerText.trim(),date:c.map(x=>x.innerText.trim()).find(x=>/^\\d{4}-\\d{2}-\\d{2}$/.test(x))||''}:null}).filter(x=>x&&x.title&&x.date&&x.board==='"+(phase==0?"1124":"1978")+"');return JSON.stringify({state:rows.length?'ok':'loading',rows:rows.slice(0,40)})}catch(e){return JSON.stringify({state:'error'})}})()";
  web.evaluateJavascript(js,answer->{try{if(done)return;JSONObject result=new JSONObject(new JSONArray("["+answer+"]").getString(0));if(!result.optString("state").equals("ok")){if(attempt<4){handler.postDelayed(()->collect(attempt+1,phase),3000);return;}finish("포털 공지를 읽지 못했어요. 로그인 상태를 확인해 주세요.",true);return;}JSONArray rows=result.getJSONArray("rows");String required=phase==0?"1124":"1978";for(int i=0;i<rows.length();i++)if(!required.equals(rows.getJSONObject(i).optString("board"))){if(attempt<4){handler.postDelayed(()->collect(attempt+1,phase),3000);return;}finish("포털 탭 전환을 확인하지 못했어요.",true);return;}for(int i=0;i<rows.length();i++)combined.put(rows.getJSONObject(i));if(phase==0){switchTab("학사공지",1);return;}saveRows(combined);}catch(Exception e){finish("포털 응답을 읽지 못했어요.",true);}});
 }
 private void saveRows(JSONArray rows){
  if(rows.length()==0){finish("공지 목록이 비어 있어 이전 기록을 유지했어요.",true);return;}
  SharedPreferences p=getSharedPreferences(PREFS,MODE_PRIVATE);SharedPreferences.Editor edit=p.edit();String level=p.getString("student_level","전체");boolean initial=!p.getBoolean("baseline_ready",false);int found=0;String first="";JSONArray shown=new JSONArray();
  for(int i=0;i<rows.length();i++){JSONObject r=rows.optJSONObject(i);if(r==null)continue;String id=r.optString("id"),board=r.optString("board"),title=r.optString("title"),date=r.optString("date");if(!id.matches("[0-9]{1,30}")||!board.matches("[0-9]{1,30}")||title.isEmpty())continue;if(relevant(title,level)){JSONObject item=new JSONObject();try{item.put("title",title);item.put("date",date);item.put("category",category(title));item.put("audience",audience(title));shown.put(item);}catch(Exception ignored){}}String key="notice_"+board+"_"+id,fingerprint=hash(title+"\n"+date);String previous=p.getString(key,"");edit.putString(key,fingerprint);if(!initial&&!fingerprint.equals(previous)&&relevant(title,level)&&!category(title).equals("기타")){found++;if(first.isEmpty())first=title;}}
  edit.putString("latest_rows",shown.toString()).putBoolean("baseline_ready",true).putLong("last_checked",System.currentTimeMillis()).putString("last_status","포털 홈의 전체·학사 공지 "+rows.length()+"행 확인 · 미리보기만");edit.apply();
  if(found>0)notifyChanges(this,found,first);finish(null,false);
 }
 static void notifyChanges(Context context,int count,String first){
  NotificationManager nm=(NotificationManager)context.getSystemService(NOTIFICATION_SERVICE);if(Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(new NotificationChannel(CHANNEL,"학교 공지",NotificationManager.IMPORTANCE_DEFAULT));
  Intent intent=new Intent(context,CampusToolsActivity.class);PendingIntent open=PendingIntent.getActivity(context,0,intent,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
  Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(context,CHANNEL):new Notification.Builder(context);b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle("누비가 학교 공지를 찾았어 · "+count+"건").setContentText(first).setStyle(new Notification.BigTextStyle().bigText(first+"\n포털 원문에서 대상과 기한을 확인해 줘." )).setContentIntent(open).setAutoCancel(true);
  try{nm.notify(90145,b.build());}catch(SecurityException ignored){}
 }
 private void finish(String error,boolean retry){if(done)return;done=true;if(error!=null)getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString("last_status",error).apply();handler.removeCallbacksAndMessages(null);if(web!=null){web.stopLoading();web.destroy();web=null;}if(running!=null)jobFinished(running,retry);running=null;}
 @Override public boolean onStopJob(JobParameters p){if(running==p)handler.post(()->{if(running==p)finish("운영체제가 조회를 중단했어요. 다음 실행 때 다시 확인해요.",false);});return true;}
}
