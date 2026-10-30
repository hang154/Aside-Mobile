package ai.decisionos.aside;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ResolveInfo;
import android.os.Bundle;
import android.widget.*;
import java.util.*;

/** Register launchable apps for explicit, user-initiated opening. */
public class AppRegistryActivity extends Activity {
    private SharedPreferences prefs;
    private LinearLayout saved;
    @Override public void onCreate(Bundle state){
        super.onCreate(state);prefs=getSharedPreferences("aside_apps",MODE_PRIVATE);
        ScrollView scroll=new ScrollView(this);scroll.setBackgroundColor(Ui.BG);
        LinearLayout root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"관심 앱",28,Ui.WHITE,true),Ui.match(this,-2,8));
        root.addView(Ui.text(this,"자주 쓰는 앱을 선택하면 이 화면에서 바로 열 수 있어요. 앱 등록만으로 자동 검색이나 알림이 실행되지는 않습니다.",14,Ui.MUTED,false),Ui.match(this,-2,10));
        saved=Ui.vertical(this,Ui.PANEL,16);saved.setBackground(Ui.bg(Ui.PANEL,16,this));root.addView(saved,Ui.match(this,-2,18));
        LinearLayout list=Ui.vertical(this,Ui.PANEL,16);list.setBackground(Ui.bg(Ui.PANEL,16,this));root.addView(list,Ui.match(this,-2,18));
        list.addView(Ui.text(this,"기기에 설치된 앱",19,Ui.WHITE,true),Ui.match(this,-2,6));
        Intent query=new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> activities=getPackageManager().queryIntentActivities(query,0);
        activities.sort(Comparator.comparing(x->String.valueOf(x.loadLabel(getPackageManager())),String.CASE_INSENSITIVE_ORDER));
        Set<String> seen=new HashSet<>();
        for(ResolveInfo info:activities){
            String pkg=info.activityInfo.packageName;if(pkg.equals(getPackageName())||!seen.add(pkg))continue;
            String label=String.valueOf(info.loadLabel(getPackageManager()));
            CheckBox cb=new CheckBox(this);cb.setText(label);cb.setTextColor(Ui.WHITE);cb.setChecked(selection().contains(pkg));
            cb.setOnCheckedChangeListener((v,checked)->{Set<String> selected=selection();if(checked)selected.add(pkg);else selected.remove(pkg);prefs.edit().putStringSet("selected",selected).apply();renderSaved();});
            list.addView(cb,Ui.match(this,-2,5));
        }
        if(seen.isEmpty())list.addView(Ui.text(this,"표시할 앱을 찾지 못했습니다.",13,Ui.MUTED,false));
        renderSaved();setContentView(scroll);
    }
    private Set<String> selection(){return new HashSet<>(prefs.getStringSet("selected",Collections.emptySet()));}
    private void renderSaved(){
        saved.removeAllViews();saved.addView(Ui.text(this,"등록한 앱",19,Ui.WHITE,true),Ui.match(this,-2,6));
        Set<String> selected=selection();if(selected.isEmpty()){saved.addView(Ui.text(this,"아래 목록에서 앱을 선택하세요.",13,Ui.MUTED,false),Ui.match(this,-2,8));return;}
        List<String> labels=new ArrayList<>(selected);Collections.sort(labels);
        for(String pkg:labels){
            try{
                String label=getPackageManager().getApplicationLabel(getPackageManager().getApplicationInfo(pkg,0)).toString();
                android.widget.Button open=Ui.button(this,label+" 열기");open.setOnClickListener(v->{Intent i=getPackageManager().getLaunchIntentForPackage(pkg);if(i==null){Toast.makeText(this,"앱을 열 수 없습니다.",Toast.LENGTH_SHORT).show();return;}try{startActivity(i);}catch(Exception e){Toast.makeText(this,"앱을 열 수 없습니다.",Toast.LENGTH_SHORT).show();}});saved.addView(open,Ui.match(this,48,8));
            }catch(Exception ignored){saved.addView(Ui.text(this,"설치되지 않은 앱: "+pkg,13,Ui.MUTED,false),Ui.match(this,-2,8));}
        }
    }
}
