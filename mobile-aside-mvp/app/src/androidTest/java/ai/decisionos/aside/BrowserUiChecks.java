package ai.decisionos.aside;

import android.app.Instrumentation;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.accessibility.AccessibilityNodeInfo;
import android.webkit.WebView;
import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.Field;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

final class BrowserUiChecks {
 static View find(View v,String description){if(description.contentEquals(v.getContentDescription()==null?"":v.getContentDescription()))return v;if(v instanceof ViewGroup){ViewGroup group=(ViewGroup)v;for(int n=0;n<group.getChildCount();n++){View child=find(group.getChildAt(n),description);if(child!=null)return child;}}return null;}
 static void run(Instrumentation i){Bundle out=new Bundle();BrowserWorkspacePanel a=null;GoalAgentActivity host=null;String goalId=null;boolean passed=false;
  try{
   Intent intent=new Intent(i.getTargetContext(),GoalAgentActivity.class).putExtra("start_url","https://example.com/").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
   try(GoalStore store=new GoalStore(i.getTargetContext())){goalId=store.create("fitness","REGRESSION_BROWSER_TEMP","운동",0).optString("id");}intent.putExtra("goal_id",goalId).putExtra("companion_page","웹 브라우저");host=(GoalAgentActivity)i.startActivitySync(intent);i.waitForIdleSync();a=(BrowserWorkspacePanel)host.chat.companion.panels.get("웹 브라우저");BrowserWorkspacePanel activity=a;
   Field field=BrowserWorkspacePanel.class.getDeclaredField("web");field.setAccessible(true);WebView web=(WebView)field.get(a);AtomicReference<String> url=new AtomicReference<>();
   for(int n=0;n<30;n++){Thread.sleep(300);i.runOnMainSync(()->url.set(web.getProgress()==100?web.getUrl():null));if("https://example.com/".equals(url.get()))break;}
   if(!"https://example.com/".equals(url.get()))throw new AssertionError("page not loaded");
   AtomicReference<View> menu=new AtomicReference<>();i.runOnMainSync(()->{View root=activity.getWindow().getDecorView();if(find(root,"뒤로")==null||find(root,"웹 주소")==null||find(root,"주소 열기")==null)throw new AssertionError("navigation controls missing");menu.set(find(root,"브라우저 메뉴"));});
   if(menu.get()==null)throw new AssertionError("menu missing");Bitmap screenshot=i.getUiAutomation().takeScreenshot();try(FileOutputStream f=new FileOutputStream(new File(i.getTargetContext().getCacheDir(),"browser-ui-check.png"))){screenshot.compress(Bitmap.CompressFormat.PNG,100,f);}screenshot.recycle();
   i.runOnMainSync(()->menu.get().performClick());Thread.sleep(400);AccessibilityNodeInfo root=i.getUiAutomation().getRootInActiveWindow();if(root==null)throw new AssertionError("menu inaccessible");
   for(String label:new String[]{"새로고침","화면 관찰","항목 선택","원격 연결","브라우저 닫기"}){List<AccessibilityNodeInfo> nodes=root.findAccessibilityNodeInfosByText(label);if(nodes.isEmpty())throw new AssertionError("menu item missing: "+label);}
   out.putString("stream","PASS browser loads example.com; address, navigation and menu actions are visible\n");passed=true;
  }catch(Throwable t){out.putString("stream","FAIL "+t.getClass().getSimpleName()+": "+t.getMessage()+"\n");}
  finally{if(host!=null){GoalAgentActivity activity=host;i.runOnMainSync(activity::finish);}if(goalId!=null)try(GoalStore store=new GoalStore(i.getTargetContext())){store.deleteGoal(goalId);}}
  i.finish(passed?-1:0,out);
 }
}
