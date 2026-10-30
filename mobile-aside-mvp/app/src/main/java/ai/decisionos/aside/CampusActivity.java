package ai.decisionos.aside;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.*;

/** Nubi campus home. Search and local task drafts only; no autonomous claims. */
public class CampusActivity extends Activity {
    private static final int BG=Color.rgb(249,248,253),INK=Color.rgb(36,32,51),MUTED=Color.rgb(105,100,119),PURPLE=Color.rgb(111,89,209),CARD=Color.WHITE;
    private EditText school,question;private TextView status;
    @Override public void onCreate(Bundle b){super.onCreate(b);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);LinearLayout root=Ui.vertical(this,BG,22);scroll.addView(root);
        TextView brand=label("●  누비",23,PURPLE,true);root.addView(brand,Ui.match(this,-2,3));
        root.addView(label("학교생활, 같이 챙길게.",28,INK,true),Ui.match(this,-2,12));
        root.addView(label("학사 정보부터 주말까지, 필요한 내용을 같이 찾아요.",14,MUTED,false),Ui.match(this,-2,8));
        LinearLayout profile=panel();profile.addView(label("우리 학교를 알려줘",16,INK,true));
        school=entry("학교 이름 (예: OO대학교)");school.setText(getSharedPreferences("nubi_campus",MODE_PRIVATE).getString("school","UNIST"));profile.addView(school,Ui.match(this,48,8));
        Button save=button("학교 저장",false);save.setOnClickListener(v->{String s=school.getText().toString().trim();if(s.length()>100){status.setText("학교 이름은 100자 이내로 적어줘.");return;}getSharedPreferences("nubi_campus",MODE_PRIVATE).edit().putString("school",s).apply();status.setText(s.isEmpty()?"학교 이름을 지웠어.":"학교를 저장했어: "+s);});profile.addView(save,Ui.match(this,44,8));root.addView(profile,Ui.match(this,-2,16));
        status=label("",13,MUTED,false);root.addView(status,Ui.match(this,-2,5));
        LinearLayout chat=panel();chat.addView(label("누비에게 부탁하기",18,INK,true));chat.addView(label("궁금한 걸 검색하거나 할 일로 남길 수 있어요.",13,MUTED,false),Ui.match(this,-2,5));question=entry("예: 부산 여행 숙소 찾아줘");chat.addView(question,Ui.match(this,50,9));
        Button search=button("웹에서 찾기",true);search.setOnClickListener(v->{String q=question.getText().toString().trim();if(q.isEmpty()||q.length()>150){status.setText("찾을 내용을 1~150자로 적어줘.");return;}openSearch(q);});chat.addView(search,Ui.match(this,46,8));root.addView(chat,Ui.match(this,-2,12));
        LinearLayout official=panel();official.addView(label("UNIST 공식 정보",16,INK,true));official.addView(label("다가오는 공식 학사일정을 불러오고, 주간 메뉴는 학교 포털에서 확인해요.",13,MUTED,false),Ui.match(this,-2,5));
        Button calendar=button("UNIST 다가오는 학사일정",true);calendar.setOnClickListener(v->startActivity(new Intent(this,UnistCalendarActivity.class)));official.addView(calendar,Ui.match(this,46,8));
        Button portal=button("UNIST m-Portal 앱 안내",false);portal.setOnClickListener(v->{try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://play.google.com/store/apps/details?id=kr.ac.unist.mportal")));}catch(Exception e){status.setText("앱 안내를 열지 못했어.");}});official.addView(portal,Ui.match(this,46,8));root.addView(official,Ui.match(this,-2,12));
        LinearLayout nav=new LinearLayout(this);Button tasks=button("내 할 일",false);tasks.setOnClickListener(v->startActivity(new Intent(this,TaskActivity.class)));Button ai=button("로컬 AI",false);ai.setOnClickListener(v->startActivity(new Intent(this,PlanAssistantActivity.class)));nav.addView(tasks,new LinearLayout.LayoutParams(0,Ui.dp(this,48),1));LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(0,Ui.dp(this,48),1);ap.leftMargin=Ui.dp(this,8);nav.addView(ai,ap);root.addView(nav,Ui.match(this,-2,12));
        root.addView(label("이런 일도 같이 해볼까?",21,INK,true),Ui.match(this,-2,24));
        String group="";for(CampusScenario s:CampusScenario.ALL){if(!s.group.equals(group)){group=s.group;root.addView(label(group,15,PURPLE,true),Ui.match(this,-2,18));}root.addView(scenario(s),Ui.match(this,-2,9));}
        Button advanced=button("브라우저와 기기 설정",false);advanced.setOnClickListener(v->startActivity(new Intent(this,MainActivity.class)));root.addView(advanced,Ui.match(this,48,20));
        root.addView(label("검색 결과의 일정·가격·접수 가능 여부는 원문에서 확인해 주세요. 예약이나 발송은 자동으로 완료되지 않아요.",12,MUTED,false),Ui.match(this,-2,16));setContentView(scroll);
    }
    private LinearLayout scenario(CampusScenario s){LinearLayout c=panel();c.addView(label(s.title,17,INK,true));c.addView(label(s.description,13,MUTED,false),Ui.match(this,-2,4));LinearLayout row=new LinearLayout(this);Button find=button("웹에서 확인",true);find.setOnClickListener(v->{String query=s.queryFor(school.getText().toString());if(query.isEmpty()){status.setText("이 기능은 학교 이름을 먼저 적어줘.");Toast.makeText(this,"학교 이름을 먼저 적어줘.",Toast.LENGTH_SHORT).show();return;}openSearch(query);});Button task=button("할 일에 담기",false);task.setOnClickListener(v->{String prefix=s.requiresSchool?school.getText().toString().trim():"";if(s.requiresSchool&&prefix.isEmpty()){Toast.makeText(this,"학교 이름을 먼저 적어줘.",Toast.LENGTH_SHORT).show();return;}Intent i=new Intent(this,TaskActivity.class);i.putExtra("task_draft",prefix.isEmpty()?s.title:prefix+" "+s.title);startActivity(i);});row.addView(find,new LinearLayout.LayoutParams(0,Ui.dp(this,42),1));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,Ui.dp(this,42),1);p.leftMargin=Ui.dp(this,8);row.addView(task,p);c.addView(row,Ui.match(this,-2,9));return c;}
    private void openUrl(String url){Intent i=new Intent(this,BrowserWorkspaceActivity.class);i.putExtra("start_url",url);startActivity(i);}
    private void openSearch(String q){Uri uri=Uri.parse("https://www.google.com/search").buildUpon().appendQueryParameter("q",q).build();Intent i=new Intent(this,BrowserWorkspaceActivity.class);i.putExtra("start_url",uri.toString());startActivity(i);}
    private TextView label(String text,int size,int color,boolean bold){return Ui.text(this,text,size,color,bold);}
    private LinearLayout panel(){LinearLayout p=Ui.vertical(this,CARD,15);p.setBackground(Ui.bg(CARD,16,this));return p;}
    private EditText entry(String hint){EditText e=new EditText(this);e.setSingleLine(true);e.setTextColor(INK);e.setHintTextColor(MUTED);e.setTextSize(15);e.setHint(hint);e.setPadding(Ui.dp(this,12),0,Ui.dp(this,12),0);e.setBackground(Ui.bg(BG,10,this));return e;}
    private Button button(String text,boolean filled){Button b=new Button(this);b.setAllCaps(false);b.setText(text);b.setTextColor(filled?Color.WHITE:PURPLE);b.setTextSize(13);b.setGravity(Gravity.CENTER);b.setBackground(Ui.bg(filled?PURPLE:Color.rgb(239,236,251),10,this));return b;}
}
