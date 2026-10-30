package ai.decisionos.aside;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.*;
import java.util.*;

/** Curated app shortcuts; no installed-app inventory is collected. */
public class AppRegistryActivity extends Activity {
    private static final String[][] APPS={{"Chrome","com.android.chrome"},{"네이버","com.nhn.android.search"},{"인스타그램","com.instagram.android"},{"카카오톡","com.kakao.talk"},{"무신사","com.musinsa.store"},{"토스","viva.republica.toss"}};
    private SharedPreferences prefs;
    private LinearLayout saved;
    @Override public void onCreate(Bundle state){
        super.onCreate(state);prefs=getSharedPreferences("aside_apps",MODE_PRIVATE);
        ScrollView scroll=new ScrollView(this);scroll.setBackgroundColor(Ui.BG);
        LinearLayout root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"관심 앱",28,Ui.WHITE,true),Ui.match(this,-2,8));
        root.addView(Ui.text(this,"필요한 앱을 등록하고 직접 열어 보세요. 앱 설치 여부는 열 때 확인합니다. 자동 검색이나 알림은 아직 실행하지 않습니다.",14,Ui.MUTED,false),Ui.match(this,-2,10));
        saved=Ui.vertical(this,Ui.PANEL,16);saved.setBackground(Ui.bg(Ui.PANEL,16,this));root.addView(saved,Ui.match(this,-2,18));
        LinearLayout list=Ui.vertical(this,Ui.PANEL,16);list.setBackground(Ui.bg(Ui.PANEL,16,this));root.addView(list,Ui.match(this,-2,18));
        list.addView(Ui.text(this,"추천 앱 선택",19,Ui.WHITE,true),Ui.match(this,-2,6));
        for(String[] app:APPS){
            String label=app[0],pkg=app[1];CheckBox cb=new CheckBox(this);cb.setText(label);cb.setTextColor(Ui.WHITE);cb.setChecked(selection().contains(pkg));
            cb.setOnCheckedChangeListener((v,checked)->{Set<String> selected=selection();if(checked)selected.add(pkg);else selected.remove(pkg);prefs.edit().putStringSet("selected",selected).apply();renderSaved();});
            list.addView(cb,Ui.match(this,-2,5));
        }
        renderSaved();setContentView(scroll);
    }
    private Set<String> selection(){return new HashSet<>(prefs.getStringSet("selected",Collections.emptySet()));}
    private void renderSaved(){
        saved.removeAllViews();saved.addView(Ui.text(this,"등록한 앱",19,Ui.WHITE,true),Ui.match(this,-2,6));
        Set<String> selected=selection();if(selected.isEmpty()){saved.addView(Ui.text(this,"아래 목록에서 앱을 선택하세요.",13,Ui.MUTED,false),Ui.match(this,-2,8));return;}
        for(String[] app:APPS){String label=app[0],pkg=app[1];if(!selected.contains(pkg))continue;
            android.widget.Button open=Ui.button(this,label+" 열기");open.setOnClickListener(v->{
                Intent i=new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER).setPackage(pkg);
                try{startActivity(i);}catch(Exception e){Toast.makeText(this,"앱이 설치돼 있지 않거나 열 수 없습니다.",Toast.LENGTH_LONG).show();}
            });saved.addView(open,Ui.match(this,48,8));
        }
    }
}
