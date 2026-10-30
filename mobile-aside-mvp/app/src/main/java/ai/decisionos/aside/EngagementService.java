package ai.decisionos.aside;

import android.accessibilityservice.AccessibilityService;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.SystemClock;
import android.view.accessibility.AccessibilityEvent;

/** Only selected app package and event category; never reads node contents. */
public class EngagementService extends AccessibilityService {
    private String current;private long started;private boolean receiverRegistered;
    private final SharedPreferences.OnSharedPreferenceChangeListener listener=(p,k)->{if(!p.getBoolean(CollectorStore.ACTIVE,false)||CollectorStore.APPS.equals(k)){current=null;started=0;}updateNotice();};
    private final BroadcastReceiver screenOff=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent i){current=null;started=0;}};
    @Override protected void onServiceConnected(){super.onServiceConnected();CollectorStore.prefs(this).registerOnSharedPreferenceChangeListener(listener);registerReceiver(screenOff,new IntentFilter(Intent.ACTION_SCREEN_OFF));receiverRegistered=true;updateNotice();}
    @Override public void onAccessibilityEvent(AccessibilityEvent e){
        if(!CollectorStore.prefs(this).getBoolean(CollectorStore.ACTIVE,false)){current=null;return;}
        String pkg=e.getPackageName()==null?"":e.getPackageName().toString();int kind=e.getEventType();
        // Our WebView records its own lifecycle; avoid counting it twice.
        if(kind==AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED){
            if(current!=null && !current.equals(pkg)){CollectorStore.record(this,current,"window_end",SystemClock.elapsedRealtime()-started);current=null;}
            if(!pkg.equals(getPackageName()) && CollectorStore.allowed(this,pkg) && !pkg.equals(current)){current=pkg;started=SystemClock.elapsedRealtime();CollectorStore.record(this,pkg,"window_open",0);}
        }else if(!pkg.equals(getPackageName()) && CollectorStore.allowed(this,pkg)){
            if(kind==AccessibilityEvent.TYPE_VIEW_CLICKED)CollectorStore.record(this,pkg,"click",0);
            else if(kind==AccessibilityEvent.TYPE_VIEW_SCROLLED)CollectorStore.record(this,pkg,"scroll",0);
        }
    }
    private void updateNotice(){NotificationManager m=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);if(!CollectorStore.prefs(this).getBoolean(CollectorStore.ACTIVE,false)){m.cancel(9151);return;}
        m.createNotificationChannel(new NotificationChannel("aside_collection","Aside 수집 상태",NotificationManager.IMPORTANCE_LOW));Intent i=new Intent(this,CollectorActivity.class);PendingIntent pi=PendingIntent.getActivity(this,0,i,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification n=new Notification.Builder(this,"aside_collection").setSmallIcon(android.R.drawable.ic_menu_view).setContentTitle("Aside 화면 이벤트 수집 중").setContentText("선택한 앱의 이벤트만 기기에 기록 · 눌러서 중지").setContentIntent(pi).setOngoing(true).build();try{m.notify(9151,n);}catch(SecurityException ignored){}
    }
    @Override public void onInterrupt(){current=null;started=0;}
    @Override public void onDestroy(){CollectorStore.prefs(this).unregisterOnSharedPreferenceChangeListener(listener);if(receiverRegistered)unregisterReceiver(screenOff);((NotificationManager)getSystemService(NOTIFICATION_SERVICE)).cancel(9151);super.onDestroy();}
}
