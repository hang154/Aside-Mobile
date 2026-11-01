package ai.decisionos.aside;

import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;
import android.webkit.WebView;
import android.webkit.ValueCallback;
import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

/** Opens ChatGPT and uses a synthetic local file; does not upload it. */
final class ChatGptDocumentChecks {
 static void run(Instrumentation i){Bundle out=new Bundle();BrowserWorkspacePanel a=null;GoalAgentActivity host=null;String goalId=null;File fixture=null;boolean passed=false;
  try{
   Context context=i.getTargetContext();File dir=new File(context.getFilesDir(),"documents");if(!dir.exists()&&!dir.mkdirs())throw new AssertionError("fixture directory");
   String name=String.format(java.util.Locale.ROOT,"%064x.hwpx",System.nanoTime());fixture=new File(dir,name);
   if(fixture.exists())throw new AssertionError("fixture path already exists");try(FileOutputStream f=new FileOutputStream(fixture)){f.write("synthetic attachment test".getBytes(StandardCharsets.UTF_8));}
   Uri uri=Uri.parse("content://"+context.getPackageName()+".documents/"+name);
   Intent intent=new Intent(context,GoalAgentActivity.class).setData(uri).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
   try(GoalStore store=new GoalStore(i.getTargetContext())){goalId=store.create("fitness","REGRESSION_BROWSER_TEMP","운동",0).optString("id");}intent.putExtra("goal_id",goalId).putExtra("companion_page","웹 브라우저");host=(GoalAgentActivity)i.startActivitySync(intent);i.waitForIdleSync();a=(BrowserWorkspacePanel)host.chat.companion.panels.get("웹 브라우저");
   Field field=BrowserWorkspacePanel.class.getDeclaredField("web");field.setAccessible(true);WebView web=(WebView)field.get(a);
   i.runOnMainSync(()->web.loadUrl("https://chatgpt.com/"));AtomicReference<String> loaded=new AtomicReference<>();
   for(int n=0;n<30;n++){Thread.sleep(500);i.runOnMainSync(()->loaded.set(web.getProgress()==100?web.getUrl():null));if(loaded.get()!=null&&loaded.get().startsWith("https://chatgpt.com/"))break;}
   if(loaded.get()==null||!loaded.get().startsWith("https://chatgpt.com/"))throw new AssertionError("ChatGPT page did not load");
   i.waitForIdleSync();AtomicReference<Uri[]> received=new AtomicReference<>();
   i.runOnMainSync(()->{if(!web.getWebChromeClient().onShowFileChooser(web,(ValueCallback<Uri[]>)received::set,null))throw new AssertionError("chooser rejected");});
   boolean clicked=false;for(int n=0;n<20;n++){Thread.sleep(200);AccessibilityNodeInfo root=i.getUiAutomation().getRootInActiveWindow();if(root==null)continue;List<AccessibilityNodeInfo> found=root.findAccessibilityNodeInfosByText("준비한 문서");if(!found.isEmpty()){clicked=found.get(0).performAction(AccessibilityNodeInfo.ACTION_CLICK);break;}}
   if(!clicked)throw new AssertionError("document confirmation missing");i.waitForIdleSync();Uri[] selected=received.get();if(selected==null||selected.length!=1||!uri.equals(selected[0]))throw new AssertionError("wrong document returned");
   try(java.io.InputStream stream=context.getContentResolver().openInputStream(selected[0])){if(stream==null||stream.read()<0)throw new AssertionError("document unreadable");}
   out.putString("stream","PASS file chooser confirmation and content URI read; actual web upload not tested\n");passed=true;
  }catch(Throwable t){out.putString("stream","FAIL "+t.getClass().getSimpleName()+": "+t.getMessage()+"\n");}
  finally{if(host!=null){GoalAgentActivity activity=host;i.runOnMainSync(activity::finish);}if(goalId!=null)try(GoalStore store=new GoalStore(i.getTargetContext())){store.deleteGoal(goalId);}if(fixture!=null)fixture.delete();}
  i.finish(passed?-1:0,out);
 }
}
