package ai.decisionos.aside;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.*;
import java.util.Set;

/** Package controls and deletion for local metadata. */
public class CollectorActivity extends Activity {
    private TextView state,summary; private LinearLayout root;
    @Override public void onCreate(Bundle b){super.onCreate(b);ScrollView scroll=new ScrollView(this);root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"화면 이벤트 수집",27,Ui.WHITE,true),Ui.match(this,-2,7));
        root.addView(Ui.text(this,"선택한 앱의 화면 전환·클릭·스크롤과 표시 구간, Aside WebView의 페이지 열기·터치만 기기에 저장합니다. 입력값·화면 문구·주소·사진은 수집하지 않습니다. 화면이 잠기면 수집을 멈춥니다. 기록은 최근 24시간과 5,000건 기준으로 다음 기록·조회 때 정리되며 이 화면에서 중지·삭제할 수 있습니다. 앱을 사용하는 기록도 민감할 수 있습니다.",14,Ui.WHITE,false),Ui.match(this,-2,10));
        root.addView(Ui.text(this,"수집할 앱 선택",18,Ui.WHITE,true),Ui.match(this,-2,12));
        checkbox("Aside 브라우저",getPackageName());checkbox("Chrome", "com.android.chrome");checkbox("카카오톡 (이벤트만)", "com.kakao.talk");checkbox("Android 설정", "com.android.settings");
        EditText packageName=new EditText(this);packageName.setSingleLine(true);packageName.setTextColor(Ui.WHITE);packageName.setHintTextColor(Ui.MUTED);packageName.setHint("다른 앱 패키지명 (예: com.example.app)");root.addView(packageName,Ui.match(this,48,4));
        button("패키지 추가",()->changePackage(packageName,true));button("패키지 제거",()->changePackage(packageName,false));
        state=Ui.text(this,"",14,Ui.WHITE,true);root.addView(state,Ui.match(this,-2,10));
        button("수집 시작",this::start);button("수집 중지",()->{CollectorStore.prefs(this).edit().putBoolean(CollectorStore.ACTIVE,false).apply();refresh();});
        button("Android 접근성 수집 서비스 설정",()->startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        button("기록 새로 보기",this::refresh);button("기록 모두 삭제",()->new AlertDialog.Builder(this).setTitle("기록을 모두 지울까요?").setNegativeButton("취소",null).setPositiveButton("삭제",(d,w)->{CollectorStore.clear(this);refresh();}).show());
        summary=Ui.text(this,"",14,Ui.WHITE,false);summary.setTextIsSelectable(true);root.addView(summary,Ui.match(this,-2,10));setContentView(scroll);refresh();
    }
    private void checkbox(String label,String pkg){CheckBox cb=new CheckBox(this);cb.setText(label);cb.setTextColor(Ui.WHITE);cb.setChecked(CollectorStore.apps(this).contains(pkg));cb.setOnCheckedChangeListener((button,on)->{Set<String>s=CollectorStore.apps(this);if(on)s.add(pkg);else s.remove(pkg);CollectorStore.prefs(this).edit().putStringSet(CollectorStore.APPS,s).apply();if(state!=null && summary!=null)refresh();});root.addView(cb,Ui.match(this,-2,3));}
    private void changePackage(EditText field,boolean add){String pkg=field.getText().toString().trim();if(!pkg.matches("[A-Za-z][A-Za-z0-9_]*(\\.[A-Za-z][A-Za-z0-9_]*)+")){state.setText("올바른 앱 패키지명을 입력하세요.");return;}if(pkg.equals(getPackageName()) || pkg.equals("com.android.chrome") || pkg.equals("com.kakao.talk") || pkg.equals("com.android.settings")){state.setText("이 앱은 위 체크박스로 선택하세요.");return;}Set<String> selected=CollectorStore.apps(this);if(add)selected.add(pkg);else selected.remove(pkg);CollectorStore.prefs(this).edit().putStringSet(CollectorStore.APPS,selected).apply();state.setText(add?"패키지를 추가했어요.":"패키지를 제거했어요.");}
    private void button(String name,Runnable action){Button b=Ui.button(this,name);b.setOnClickListener(v->action.run());root.addView(b,Ui.match(this,48,8));}
    private void start(){if(!CollectorStore.serviceEnabled(this)){state.setText("먼저 Android 접근성 수집 서비스를 켜 주세요.");return;}if(CollectorStore.apps(this).isEmpty()){state.setText("먼저 수집할 앱을 선택하세요.");return;}
        if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},91);state.setText("수집 상태 알림을 허용한 다음 다시 시작해 주세요.");return;}
        CollectorStore.prefs(this).edit().putBoolean(CollectorStore.ACTIVE,true).apply();refresh();
    }
    private void refresh(){boolean active=CollectorStore.prefs(this).getBoolean(CollectorStore.ACTIVE,false);state.setText(active?(CollectorStore.serviceEnabled(this)?"수집 켜짐 · 선택한 앱에서 기록 중":"수집 설정 켜짐 · 접근성 서비스가 꺼져 기록 중단"):"수집 꺼짐");summary.setText("선택된 앱: "+CollectorStore.apps(this)+"\n\n"+CollectorStore.summary(this));}
    @Override protected void onResume(){super.onResume();if(state!=null)refresh();}
}
