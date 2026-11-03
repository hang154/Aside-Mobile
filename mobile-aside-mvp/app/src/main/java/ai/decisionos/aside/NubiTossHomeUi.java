package ai.decisionos.aside;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.view.View;
import android.view.ViewGroup;
import android.view.Gravity;
import android.webkit.*;
import android.widget.*;
import org.json.*;
import java.util.*;

/** A/D home studies. Only bundled local content gets this draft/navigation bridge. */
final class NubiTossHomeUi {
 static final String HOME="file:///android_asset/nubi_home/index.html";
 final NubiCompanionUi u; final GoalAgentActivity a; final WebView web;
 final android.content.SharedPreferences prefs;
 final android.os.Handler groupHandler=new android.os.Handler(android.os.Looper.getMainLooper());String groupSnapshot="";boolean disposed;
 final Runnable groupRefresh=new Runnable(){public void run(){if(disposed)return;if(ready&&u.page.equals("누비톡"))sync();groupHandler.postDelayed(this,1500);}};
 BackgroundSchoolLogin schoolLogin;boolean ready; String groupLease="";JSONObject groupGoals=new JSONObject();LinearLayout groupPreview;ViewGroup browserParent;ViewGroup.LayoutParams browserParams;
 static boolean enabled(){return BuildConfig.HOME_STYLE==1||BuildConfig.HOME_STYLE==4||BuildConfig.HOME_STYLE==5||BuildConfig.HOME_STYLE==6;}
 @SuppressLint("SetJavaScriptEnabled") NubiTossHomeUi(NubiCompanionUi ui){
  u=ui;a=u.a;prefs=a.getSharedPreferences("home_studies",0);web=new WebView(a);WebSessionPolicy.attach(web);web.setContentDescription("누비 A·D 인터랙티브 홈");
  web.setBackgroundColor(0xfff2f4f6);web.setOverScrollMode(View.OVER_SCROLL_NEVER);
  WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setAllowFileAccessFromFileURLs(false);s.setAllowUniversalAccessFromFileURLs(false);s.setBlockNetworkLoads(true);s.setTextZoom(Math.round(a.getResources().getConfiguration().fontScale*100));
  web.addJavascriptInterface(new Bridge(),"NubiHome");
  web.setWebViewClient(new WebViewClient(){
   @Override public boolean shouldOverrideUrlLoading(WebView w,WebResourceRequest r){return true;}
   @Override public WebResourceResponse shouldInterceptRequest(WebView w,WebResourceRequest r){String v=r.getUrl().toString();if(v.startsWith("file:///android_asset/nubi_home/")||v.startsWith("data:image/jpeg;base64,"))return null;return new WebResourceResponse("text/plain","UTF-8",new java.io.ByteArrayInputStream(new byte[0]));}
   @Override public void onPageFinished(WebView w,String url){if(!ready){ready=true;sync();}}
  });
  String fallback=BuildConfig.HOME_STYLE==4?"D1":"A1";String variant=prefs.getString("variant",fallback);if(!variant.matches("[AD][1-5]"))variant=fallback;
  web.loadUrl(HOME+"?variant="+variant);groupHandler.postDelayed(groupRefresh,1500);
 }
 void mount(){if(web.getParent()==null)u.tossHomeHost.addView(web,new FrameLayout.LayoutParams(-1,-1));u.tossHomeHost.setVisibility(View.VISIBLE);web.getSettings().setTextZoom(Math.round(a.getResources().getConfiguration().fontScale*100));sync();}
 void sync(){publishBrowser();if(BuildConfig.HOME_STYLE==6&&ready)web.evaluateJavascript("window.openGroup&&window.openGroup("+u.page.equals("누비톡")+")",null);if(!ready||a.isDestroyed())return;try{JSONObject s=new JSONObject();String fallback=BuildConfig.HOME_STYLE==4?"D1":"A1";s.put("variant",prefs.getString("variant",fallback));s.put("focus",prefs.getString("focus","grades"));s.put("scenario",prefs.getString("scenario","now"));JSONArray goals=new JSONArray();for(JSONObject g:a.store.goals())if(!GoalStore.fixture(g)){JSONObject row=new JSONObject();row.put("title",g.optString("title"));row.put("character",g.optString("character"));goals.put(row);}if(BuildConfig.HOME_STYLE==6)s.put("groupRoom",GroupRooms.room(a));s.put("scheduledWork",ScheduledWorkUi.feed(a));s.put("goals",goals);web.evaluateJavascript("window.NubiHomeState("+s.toString()+")",null);}catch(JSONException e){a.toast("목표를 불러오지 못했어요.");}}
 void dispose(){disposed=true;if(schoolLogin!=null)schoolLogin.cancel();groupHandler.removeCallbacksAndMessages(null);closeGroupPreview();web.removeJavascriptInterface("NubiHome");web.stopLoading();web.destroy();}
 boolean trusted(){return ready&&web.getUrl()!=null&&web.getUrl().startsWith(HOME)&&!a.isDestroyed();}
 void groupResult(JSONObject result){if(trusted()){String state=result.optString("state");if(Arrays.asList("completed","failed","cancelled").contains(state)){groupLease="";a.gid=a.chat.goalId;}web.evaluateJavascript("window.NubiGroupResult&&window.NubiGroupResult("+result.toString()+")",null);}}
 boolean groupOwns(JSONObject cmd){if(cmd.optString("request_id").matches("[a-f0-9-]{36}")&&a.relay.session().equals(cmd.optString("device_session")))try(ScheduledWorkStore s=new ScheduledWorkStore(a)){JSONObject w=s.get(cmd.optString("request_id"));JSONObject goals=GoalStore.json(w.optString("group_goals"));Iterator<String> keys=goals.keys();boolean owns=false;while(keys.hasNext())owns|=cmd.optString("goal_id").equals(goals.optString(keys.next()));if(w.optString("room_type").equals("group")&&w.optString("state").equals("CHAT_RUNNING")&&cmd.optString("group_job_id").equals(w.optString("job_id"))&&owns)return true;}return !groupLease.isEmpty()&&groupLease.equals(cmd.optString("request_id"))&&a.relay.session().equals(cmd.optString("device_session"))&&cmd.optString("group_job_id").matches("[a-f0-9]{32}")&&ownsGroupGoal(cmd.optString("goal_id"));}
 boolean ownsGroupGoal(String id){if(!id.matches("[a-f0-9-]{36}"))return false;Iterator<String> it=groupGoals.keys();while(it.hasNext())if(id.equals(groupGoals.optString(it.next())))return true;return false;}
 void parkGroupBrowser(){if(groupPreview==null)return;a.web.setLayerType(View.LAYER_TYPE_SOFTWARE,null);int w=Math.max(Ui.dp(a,360),u.tossHomeHost.getWidth()),h=Math.max(Ui.dp(a,640),u.tossHomeHost.getHeight());FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(w,h);lp.leftMargin=-2*w;groupPreview.setLayoutParams(lp);groupPreview.setClipBounds(null);groupPreview.setVisibility(View.VISIBLE);}
 void showGroupPreview(){if(groupPreview!=null)return;a.web.getSettings().setOffscreenPreRaster(true);browserParent=(ViewGroup)a.web.getParent();browserParams=a.web.getLayoutParams();if(browserParent!=null)browserParent.removeView(a.web);groupPreview=new LinearLayout(a);groupPreview.setOrientation(LinearLayout.VERTICAL);groupPreview.setBackgroundColor(Color.WHITE);groupPreview.addView(a.web,new LinearLayout.LayoutParams(-1,-1));u.tossHomeHost.addView(groupPreview,new FrameLayout.LayoutParams(1,1));parkGroupBrowser();publishBrowser();}
 void publishBrowser(){if(groupPreview==null||!trusted())return;String url=a.web.getUrl();if(url==null||url.equals("about:blank"))return;String host=android.net.Uri.parse(url).getHost();boolean sensitive="portal.unist.ac.kr".equals(host)||"login.microsoftonline.com".equals(host)||"login.live.com".equals(host)||"auth.openai.com".equals(host);String safe=android.net.Uri.parse(url).buildUpon().clearQuery().fragment(null).build().toString(),snapshot="";
  if(!sensitive&&a.web.getWidth()>0&&a.web.getHeight()>0){android.graphics.Bitmap b=android.graphics.Bitmap.createBitmap(480,Math.max(180,Math.min(960,Math.round(480f*a.web.getHeight()/a.web.getWidth()))),android.graphics.Bitmap.Config.RGB_565);android.graphics.Canvas canvas=new android.graphics.Canvas(b);canvas.drawColor(Color.WHITE);canvas.scale(480f/a.web.getWidth(),480f/a.web.getWidth());a.web.draw(canvas);java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();b.compress(android.graphics.Bitmap.CompressFormat.JPEG,65,bytes);b.recycle();snapshot="data:image/jpeg;base64,"+android.util.Base64.encodeToString(bytes.toByteArray(),android.util.Base64.NO_WRAP);}
  web.evaluateJavascript("window.NubiBrowserPreview&&window.NubiBrowserPreview("+JSONObject.quote(safe)+","+JSONObject.quote(a.web.getTitle()==null?"브라우저":a.web.getTitle())+","+JSONObject.quote(snapshot)+","+sensitive+")",null);
 }
 void expandGroupPreview(){showGroupPreview();publishBrowser();}
 void closeGroupPreview(){if(groupPreview==null)return;groupPreview.removeView(a.web);u.tossHomeHost.removeView(groupPreview);groupPreview=null;if(browserParent!=null&&a.web.getParent()==null)browserParent.addView(a.web,browserParams);if(trusted())web.evaluateJavascript("window.NubiBrowserClose&&window.NubiBrowserClose()",null);}
 void openGroupRoom(String id){closeGroupPreview();GroupRooms.select(a,id);groupSnapshot="";u.select("누비톡");sync();}
 void newGroupRoom(){closeGroupPreview();GroupRooms.latest(a,true);groupSnapshot="";u.select("누비톡");sync();}

 final class Bridge {
  @JavascriptInterface public void browserBounds(double x,double y,double width,double height,double top,double bottom){a.runOnUiThread(()->{if(!trusted()||groupPreview==null)return;double d=a.getResources().getDisplayMetrics().density;if(!Double.isFinite(x+y+width+height+top+bottom)||width<1||height<1||width>4000||height>4000){parkGroupBrowser();return;}int left=(int)Math.round(x*d),pos=(int)Math.round(y*d),w=(int)Math.round(width*d),h=(int)Math.round(height*d);FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(w,h);lp.leftMargin=left;lp.topMargin=pos;groupPreview.setLayoutParams(lp);int clipTop=Math.max(0,(int)Math.ceil((top-y)*d)),clipBottom=Math.min(h,(int)Math.floor((bottom-y)*d));groupPreview.setVisibility(u.page.equals("누비톡")&&clipBottom>clipTop?View.VISIBLE:View.INVISIBLE);groupPreview.setClipBounds(new android.graphics.Rect(0,clipTop,w,Math.max(clipTop,clipBottom)));});}

  @JavascriptInterface public void schoolBackgroundLogin(){a.runOnUiThread(()->{if(trusted()){showGroupPreview();if(schoolLogin==null)schoolLogin=new BackgroundSchoolLogin(a,a.web);a.web.evaluateJavascript("location.origin==='https://portal.unist.ac.kr'&&/로그아웃|log.?out/i.test(document.body.innerText)&&!document.querySelector('input[type=password]')",r->{if("true".equals(r)){schoolLogin.status("포털 연결 완료 · 로그인 세션을 유지하고 있어요");}else schoolLogin.show();});}});}

  @JavascriptInterface public void groupSave(String payload){a.runOnUiThread(()->{if(!trusted()||payload==null||payload.length()>350000)return;try{JSONObject b=new JSONObject(payload);if(!b.getString("id").equals(GroupRooms.room(a).optString("id")))return;GroupRooms.save(a,b.getString("id"),b.getJSONArray("messages"),b.optJSONObject("pending"));}catch(Exception e){a.toast("대화 저장 상태를 확인해 주세요.");}});}
  @JavascriptInterface public void newGroup(){a.runOnUiThread(()->{if(trusted())newGroupRoom();});}
  @JavascriptInterface public void scheduled(String id){a.runOnUiThread(()->{if(!trusted()||id==null)return;if(id.equals("new")){if(BuildConfig.HOME_STYLE==6){u.select("누비톡");web.evaluateJavascript("groupSend("+JSONObject.quote("새 알림 예약")+")",null);}else ScheduledWorkUi.show(a.chat,"새 알림 예약");}else ScheduledWorkUi.openFromHome(a.chat,id);});}

  @JavascriptInterface public void groupRequest(String payload){a.runOnUiThread(()->{if(!trusted()||BuildConfig.HOME_STYLE!=6||payload==null||payload.length()>20000)return;try{JSONObject body=new JSONObject(payload);String request=body.optString("request_id"),text=body.optString("text");JSONArray history=body.optJSONArray("history");if(!request.matches("[a-f0-9-]{36}")||text.isBlank()||text.length()>1500||history==null||history.length()>12)return;JSONObject scheduling=GroupSchedule.handle(a,GroupRooms.room(a).optString("id"),request,text);if(scheduling!=null){groupResult(scheduling);return;}body.put("device_session",a.relay.session());if(a.runs.active()!=null||ChatWork.busy(a)){groupResult(new GoalChatUi.JSONObjectSafe("request_id",request).put("error","다른 탐색을 먼저 마치거나 중지해 주세요."));return;}groupLease=request;groupGoals=new JSONObject();for(GoalRules.Preset p:GoalRules.PRESETS){JSONObject chosen=null;for(JSONObject g:a.store.goals())if(!GoalStore.fixture(g)&&p.id.equals(g.optString("character"))){chosen=g;break;}if(chosen==null)chosen=a.store.create(p.id,p.title,p.topic,0);groupGoals.put(p.id,chosen.optString("id"));}body.put("goals",groupGoals);if(!a.relay.connected()){JSONObject error=new JSONObject();error.put("error","Qwen 연결이 필요해요. 연결 후 다시 보내주세요.");error.put("request_id",request);groupResult(error);a.pair();return;}a.relay.chat("/group-submit",body,r->{GoalStore.put(r,"request_id",request);groupResult(r);});}catch(Exception e){a.toast("그룹 요청을 확인해 주세요.");}});}
  @JavascriptInterface public void groupStatus(String job,String request){a.runOnUiThread(()->{if(!trusted()||BuildConfig.HOME_STYLE!=6||job==null||request==null||!job.matches("[a-f0-9]{32}")||!request.matches("[a-f0-9-]{36}"))return;JSONObject b=new JSONObject();GoalStore.put(b,"job_id",job);GoalStore.put(b,"device_session",a.relay.session());a.relay.chat("/group-status",b,r->{GoalStore.put(r,"request_id",request);groupResult(r);});});}

  @JavascriptInterface public void groupCancel(String job,String request){a.runOnUiThread(()->{if(!trusted()||job==null||request==null||!job.matches("[a-f0-9]{32}")||!request.equals(groupLease))return;JSONObject b=new JSONObject();GoalStore.put(b,"job_id",job);GoalStore.put(b,"device_session",a.relay.session());a.relay.chat("/group-cancel",b,r->{GoalStore.put(r,"request_id",request);groupResult(r);});});}
  @JavascriptInterface public void openKorail(){a.runOnUiThread(()->{if(!trusted())return;Intent launch=a.getPackageManager().getLaunchIntentForPackage("com.korail.talk");try{if(launch!=null){a.startActivity(launch);return;}a.startActivity(new Intent(Intent.ACTION_VIEW,android.net.Uri.parse("https://play.google.com/store/apps/details?id=com.korail.talk")));}catch(android.content.ActivityNotFoundException e){a.toast("코레일+ 설치 페이지를 열 수 없어요.");}});}
  @JavascriptInterface public void openKorailWeb(){a.runOnUiThread(()->{if(!trusted())return;showGroupPreview();a.web.loadUrl("https://www.korail.com/ticket");});}
  @JavascriptInterface public void ready(){a.runOnUiThread(()->{if(!a.isDestroyed()){if(!ready){ready=true;sync();}}});}
  @JavascriptInterface public void preference(String variant,String scenario,String focus){a.runOnUiThread(()->{if(!trusted()||variant==null||scenario==null||focus==null||!variant.matches("[AD][1-5]")||!Arrays.asList("now","morning","lunch","travel","school","night","invest").contains(scenario))return;try{GoalRules.preset(focus);}catch(IllegalArgumentException e){return;}prefs.edit().putString("variant",variant).putString("scenario",scenario).putString("focus",focus).apply();});}
  @JavascriptInterface public void contentChanged(){a.runOnUiThread(()->{if(trusted()&&web.isShown()){web.clearFocus();web.requestFocus();web.sendAccessibilityEvent(android.view.accessibility.AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED);}});}
  @JavascriptInterface public void menu(){a.runOnUiThread(()->{if(trusted())u.toggleSidebar();});}
  @JavascriptInterface public void route(String page){a.runOnUiThread(()->{if(trusted()&&Arrays.asList("홈","대화","친구","탐색","작업","내 정보","학교 시작하기").contains(page)){if(BuildConfig.HOME_STYLE==6&&page.equals("학교 시작하기")){u.select("누비톡");showGroupPreview();a.web.loadUrl("https://portal.unist.ac.kr/");return;}u.select(BuildConfig.HOME_STYLE==6&&page.equals("대화")?"누비톡":page);}});}
  @JavascriptInterface public void chat(String agent,String prompt){a.runOnUiThread(()->{if(!trusted()||agent==null||prompt==null||prompt.isBlank()||prompt.length()>1500)return;try{GoalRules.preset(agent);}catch(IllegalArgumentException e){return;}new NubiHomeUi(u).chat(agent,prompt);});}
 }
}
