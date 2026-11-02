package ai.decisionos.aside;
/** Persist browser sessions when any in-app activity is backgrounded. */
public class NubiApplication extends android.app.Application {
 static java.lang.ref.WeakReference<android.app.Activity> foreground=new java.lang.ref.WeakReference<>(null);
 public void onCreate(){super.onCreate();registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks(){
 public void onActivityCreated(android.app.Activity a,android.os.Bundle b){} public void onActivityStarted(android.app.Activity a){} public void onActivityResumed(android.app.Activity a){foreground=new java.lang.ref.WeakReference<>(a);} public void onActivityPaused(android.app.Activity a){if(foreground.get()==a)foreground.clear();WebSessionPolicy.checkpoint();} public void onActivityStopped(android.app.Activity a){WebSessionPolicy.checkpoint();} public void onActivitySaveInstanceState(android.app.Activity a,android.os.Bundle b){} public void onActivityDestroyed(android.app.Activity a){}
 });}
}
