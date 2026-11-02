package ai.decisionos.aside;

import android.annotation.SuppressLint;
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
 boolean ready; String groupLease="";JSONObject groupGoals=new JSONObject();LinearLayout groupPreview;ViewGroup browserParent;ViewGroup.LayoutParams browserParams;
 static boolean enabled(){return BuildConfig.HOME_STYLE==1||BuildConfig.HOME_STYLE==4||BuildConfig.HOME_STYLE==5||BuildConfig.HOME_STYLE==6;}
 @SuppressLint("SetJavaScriptEnabled") NubiTossHomeUi(NubiCompanionUi ui){
  u=ui;a=u.a;prefs=a.getSharedPreferences("home_studies",0);web=new WebView(a);WebSessionPolicy.attach(web);web.setContentDescription("누비 A·D 인터랙티브 홈");
  web.setBackgroundColor(0xfff2f4f6);web.setOverScrollMode(View.OVER_SCROLL_NEVER);
  WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setAllowFileAccessFromFileURLs(false);s.setAllowUniversalAccessFromFileURLs(false);s.setBlockNetworkLoads(true);s.setTextZoom(Math.round(a.getResources().getConfiguration().fontScale*100));
  web.addJavascriptInterface(new Bridge(),"NubiHome");
  web.setWebViewClient(new WebViewClient(){
   @Override public boolean shouldOverrideUrlLoading(WebView w,WebResourceRequest r){return true;}
   @Override public WebResourceResponse shouldInterceptRequest(WebView w,WebResourceRequest r){String v=r.getUrl().toString();if(v.startsWith("file:///android_asset/nubi_home/"))return null;return new WebResourceResponse("text/plain","UTF-8",new java.io.ByteArrayInputStream(new byte[0]));}
   @Override public void onPageFinished(WebView w,String url){if(!ready){ready=true;sync();}}
  });
  String fallback=BuildConfig.HOME_STYLE==4?"D1":"A1";String variant=prefs.getString("variant",fallback);if(!variant.matches("[AD][1-5]"))variant=fallback;
  web.loadUrl(HOME+"?variant="+variant);
 }
 void mount(){if(web.getParent()==null)u.tossHomeHost.addView(web,new FrameLayout.LayoutParams(-1,-1));u.tossHomeHost.setVisibility(View.VISIBLE);web.getSettings().setTextZoom(Math.round(a.getResources().getConfiguration().fontScale*100));sync();}
 void sync(){if(BuildConfig.HOME_STYLE==6&&ready)web.evaluateJavascript("window.openGroup&&window.openGroup("+u.page.equals("누비톡")+")",null);if(!ready||a.isDestroyed())return;try{JSONObject s=new JSONObject();String fallback=BuildConfig.HOME_STYLE==4?"D1":"A1";s.put("variant",prefs.getString("variant",fallback));s.put("focus",prefs.getString("focus","grades"));s.put("scenario",prefs.getString("scenario","now"));JSONArray goals=new JSONArray();for(JSONObject g:a.store.goals())if(!GoalStore.fixture(g)){JSONObject row=new JSONObject();row.put("title",g.optString("title"));row.put("character",g.optString("character"));goals.put(row);}s.put("goals",goals);web.evaluateJavascript("window.NubiHomeState("+s.toString()+")",null);}catch(JSONException e){a.toast("목표를 불러오지 못했어요.");}}
 void dispose(){closeGroupPreview();web.removeJavascriptInterface("NubiHome");web.stopLoading();web.destroy();}
 boolean trusted(){return ready&&web.getUrl()!=null&&web.getUrl().startsWith(HOME)&&!a.isDestroyed();}
 void groupResult(JSONObject result){if(trusted()){String state=result.optString("state");if(Arrays.asList("completed","failed","cancelled").contains(state)){groupLease="";a.gid=a.chat.goalId;}web.evaluateJavascript("window.NubiGroupResult&&window.NubiGroupResult("+result.toString()+")",null);}}
 boolean groupOwns(JSONObject cmd){return !groupLease.isEmpty()&&groupLease.equals(cmd.optString("request_id"))&&a.relay.session().equals(cmd.optString("device_session"))&&cmd.optString("group_job_id").matches("[a-f0-9]{32}")&&ownsGroupGoal(cmd.optString("goal_id"));}
 boolean ownsGroupGoal(String id){if(!id.matches("[a-f0-9-]{36}"))return false;Iterator<String> it=groupGoals.keys();while(it.hasNext())if(id.equals(groupGoals.optString(it.next())))return true;return false;}
 void showGroupPreview(){if(groupPreview!=null)return;browserParent=(ViewGroup)a.web.getParent();browserParams=a.web.getLayoutParams();if(browserParent!=null)browserParent.removeView(a.web);groupPreview=new LinearLayout(a);groupPreview.setOrientation(LinearLayout.VERTICAL);groupPreview.setBackgroundColor(Color.WHITE);Button title=new Button(a);title.setText("실제 탐색 · 확대 ↗");title.setTextSize(10);title.setOnClickListener(v->expandGroupPreview());groupPreview.addView(title,new LinearLayout.LayoutParams(-1,Ui.dp(a,36)));groupPreview.addView(a.web,new LinearLayout.LayoutParams(-1,0,1));FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(Ui.dp(a,154),Ui.dp(a,206),Gravity.TOP|Gravity.RIGHT);lp.topMargin=Ui.dp(a,125);u.tossHomeHost.addView(groupPreview,lp);}
 void expandGroupPreview(){if(groupPreview==null)return;groupPreview.removeView(a.web);android.app.Dialog d=new android.app.Dialog(a);LinearLayout body=new LinearLayout(a);body.setOrientation(1);Button back=new Button(a);back.setText("채팅으로 돌아가기");back.setOnClickListener(v->d.dismiss());body.addView(back);body.addView(a.web,new LinearLayout.LayoutParams(-1,0,1));d.setContentView(body);d.setOnDismissListener(x->{body.removeView(a.web);if(groupPreview!=null)groupPreview.addView(a.web,new LinearLayout.LayoutParams(-1,0,1));});d.show();d.getWindow().setLayout(-1,-1);}
 void closeGroupPreview(){if(groupPreview==null)return;groupPreview.removeView(a.web);u.tossHomeHost.removeView(groupPreview);groupPreview=null;if(browserParent!=null&&a.web.getParent()==null)browserParent.addView(a.web,browserParams);}

 final class Bridge {
  @JavascriptInterface public void groupRequest(String payload){a.runOnUiThread(()->{if(!trusted()||BuildConfig.HOME_STYLE!=6||payload==null||payload.length()>20000)return;try{JSONObject body=new JSONObject(payload);String request=body.optString("request_id"),text=body.optString("text");JSONArray history=body.optJSONArray("history");if(!request.matches("[a-f0-9-]{36}")||text.isBlank()||text.length()>1500||history==null||history.length()>12)return;body.put("device_session",a.relay.session());if(a.runs.active()!=null){groupResult(new GoalChatUi.JSONObjectSafe("request_id",request).put("error","다른 탐색을 먼저 마치거나 중지해 주세요."));return;}groupLease=request;groupGoals=new JSONObject();for(GoalRules.Preset p:GoalRules.PRESETS){JSONObject chosen=null;for(JSONObject g:a.store.goals())if(!GoalStore.fixture(g)&&p.id.equals(g.optString("character"))){chosen=g;break;}if(chosen==null)chosen=a.store.create(p.id,p.title,p.topic,0);groupGoals.put(p.id,chosen.optString("id"));}body.put("goals",groupGoals);if(!a.relay.connected()){JSONObject error=new JSONObject();error.put("error","Qwen 연결이 필요해요. 연결 후 다시 보내주세요.");error.put("request_id",request);groupResult(error);a.pair();return;}a.relay.chat("/group-submit",body,r->{GoalStore.put(r,"request_id",request);groupResult(r);});}catch(Exception e){a.toast("그룹 요청을 확인해 주세요.");}});}
  @JavascriptInterface public void groupStatus(String job,String request){a.runOnUiThread(()->{if(!trusted()||BuildConfig.HOME_STYLE!=6||job==null||request==null||!job.matches("[a-f0-9]{32}")||!request.matches("[a-f0-9-]{36}"))return;JSONObject b=new JSONObject();GoalStore.put(b,"job_id",job);GoalStore.put(b,"device_session",a.relay.session());a.relay.chat("/group-status",b,r->{GoalStore.put(r,"request_id",request);groupResult(r);});});}

  @JavascriptInterface public void groupCancel(String job,String request){a.runOnUiThread(()->{if(!trusted()||job==null||request==null||!job.matches("[a-f0-9]{32}")||!request.equals(groupLease))return;JSONObject b=new JSONObject();GoalStore.put(b,"job_id",job);GoalStore.put(b,"device_session",a.relay.session());a.relay.chat("/group-cancel",b,r->{GoalStore.put(r,"request_id",request);groupResult(r);});});}
  @JavascriptInterface public void ready(){a.runOnUiThread(()->{if(!a.isDestroyed()){if(!ready){ready=true;sync();}}});}
  @JavascriptInterface public void preference(String variant,String scenario,String focus){a.runOnUiThread(()->{if(!trusted()||variant==null||scenario==null||focus==null||!variant.matches("[AD][1-5]")||!Arrays.asList("now","morning","lunch","travel","school","night","invest").contains(scenario))return;try{GoalRules.preset(focus);}catch(IllegalArgumentException e){return;}prefs.edit().putString("variant",variant).putString("scenario",scenario).putString("focus",focus).apply();});}
  @JavascriptInterface public void contentChanged(){a.runOnUiThread(()->{if(trusted()&&web.isShown()){web.clearFocus();web.requestFocus();web.sendAccessibilityEvent(android.view.accessibility.AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED);}});}
  @JavascriptInterface public void menu(){a.runOnUiThread(()->{if(trusted())u.toggleSidebar();});}
  @JavascriptInterface public void route(String page){a.runOnUiThread(()->{if(trusted()&&Arrays.asList("홈","대화","친구","탐색","작업","내 정보","학교 시작하기").contains(page))u.select(BuildConfig.HOME_STYLE==6&&page.equals("대화")?"누비톡":page);});}
  @JavascriptInterface public void chat(String agent,String prompt){a.runOnUiThread(()->{if(!trusted()||agent==null||prompt==null||prompt.isBlank()||prompt.length()>1500)return;try{GoalRules.preset(agent);}catch(IllegalArgumentException e){return;}new NubiHomeUi(u).chat(agent,prompt);});}
 }
}
