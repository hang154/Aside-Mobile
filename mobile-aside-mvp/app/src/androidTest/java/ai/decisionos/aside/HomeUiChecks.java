package ai.decisionos.aside;
import android.content.*;import android.os.*;import android.graphics.Bitmap;import android.view.*;import android.widget.*;import java.io.*;
final class HomeUiChecks {
 static void run(GoalInstrumentation i){Bundle out=new Bundle();GoalAgentActivity a=null;try{
 a=(GoalAgentActivity)i.startActivitySync(new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("companion_page","홈").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));final GoalAgentActivity h=a;i.waitForIdleSync();
 i.check(BuildConfig.HOME_LIGHT&&!NubiCompanionUi.DARK&&NubiCompanionUi.WHITE==0xffffffff,"white shell across pages");
 i.check(BuildConfig.HOME_STYLE>=1&&BuildConfig.HOME_STYLE<=4,"variant style");
 i.runOnMainSync(()->{h.chat.companion.select("홈");});i.waitForIdleSync();
 NubiCompanionUi u=h.chat.companion;for(String mode:new String[]{"지금","기상","점심","귀가","학교 소식","저녁","투자"}){
 i.runOnMainSync(()->{h.getSharedPreferences("home_context",0).edit().putString("scenario",mode).apply();u.refresh();});i.waitForIdleSync();
 final String[] s={""};i.runOnMainSync(()->s[0]=all(u.sideBody));i.check(s[0].contains("건강이")&&s[0].contains("차곡이")&&s[0].contains("떠남이")&&s[0].contains("든든이")&&s[0].contains("다정이")&&s[0].contains("똑똑이"),mode+" six agents");
 i.check(s[0].contains("중요한 알림")&&s[0].contains("목표 선택·개인화"),mode+" goals and alerts");
 if(!mode.equals("지금"))i.check(s[0].contains("상황 미리보기"),"preview distinguished "+mode);
 if(mode.equals("귀가"))i.check(s[0].contains("513번")&&s[0].contains("수업 끝나면, 집으로"),"bus train preview");
 if(mode.equals("지금")||mode.equals("귀가")){i.runOnMainSync(()->u.sideScroll.scrollTo(0,0));i.waitForIdleSync();shot(i,"home-"+BuildConfig.HOME_STYLE+"-"+(mode.equals("지금")?"now":"travel")+".png");}
 }
 for(GoalRules.Preset p:GoalRules.PRESETS){i.runOnMainSync(()->new NubiHomeUi(h.chat.companion).chat(p.id,p.name+" 검증 질문"));i.waitForIdleSync();i.check(h.chat.character.equals(p.id),"correct owner "+p.id);final String[] draft={""};i.runOnMainSync(()->draft[0]=h.chat.input.getText().toString());i.check(draft[0].contains("검증 질문"),"draft preserved "+p.id);}
 shot(i,"white-chat-"+BuildConfig.HOME_STYLE+".png");
 for(String page:new String[]{"친구","탐색","작업","내 정보","홈"}){i.runOnMainSync(()->h.chat.companion.select(page));i.waitForIdleSync();i.check(h.chat.companion.page.equals(page),"preserved destination "+page);if(page.equals("작업")||page.equals("내 정보"))shot(i,"white-"+page+"-"+BuildConfig.HOME_STYLE+".png");}
 i.runOnMainSync(()->{h.getSharedPreferences("home_context",0).edit().putString("scenario","지금").apply();h.chat.companion.select("홈");});i.waitForIdleSync();
 out.putString("stream","PASS "+i.checks+" home UI checks, style="+BuildConfig.HOME_STYLE+"\n");
 }catch(Throwable e){out.putString("stream","FAIL "+e+"\n");}finally{if(a!=null){final GoalAgentActivity h=a;i.runOnMainSync(h::finish);}}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
 static String all(View v){String s=v instanceof TextView?((TextView)v).getText().toString()+"\n":"";if(v instanceof ViewGroup){ViewGroup g=(ViewGroup)v;for(int n=0;n<g.getChildCount();n++)s+=all(g.getChildAt(n));}return s;}
 static void shot(GoalInstrumentation i,String name)throws Exception{Thread.sleep(350);i.waitForIdleSync();Bitmap b=i.getUiAutomation().takeScreenshot();if(b==null)throw new AssertionError("screenshot");File f=new File(i.getTargetContext().getExternalFilesDir(null),name);try(FileOutputStream o=new FileOutputStream(f)){b.compress(Bitmap.CompressFormat.PNG,100,o);}b.recycle();}
}
