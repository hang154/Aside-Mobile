package ai.decisionos.aside;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.*;
import java.util.LinkedHashMap;
import java.util.Map;

/** User supplies and verifies the prices and timetable used by this offline calculation. */
final class ConcertTripPanel extends CompanionPanel {
 ConcertTripPanel(NubiCompanionUi ui){super(ui);}

    private final Map<String,EditText> fields=new LinkedHashMap<>();
    private SharedPreferences prefs;
    private TextView result;
    private LinearLayout root;
     public void onCreate(Bundle state) {
        super.onCreate(state); prefs=getSharedPreferences("concert_trip",MODE_PRIVATE);
        ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true); root=Ui.vertical(this,0xffffffff,0);scroll.addView(root);
        label("공연 원정, 돌아오는 길까지",26,true);
        label("시간표와 숙소 가격을 직접 확인해 입력하면 귀가 가능성과 비용을 비교해요. 결과는 예약이 아닙니다.",14,false);
        button("연습용 시나리오 채우기",()->sample());
        field("origin","출발 도시 (예: 대구)",false); field("city","공연 도시 (예: 서울)",false); field("venue","공연장",false);
        field("end","공연 종료 예상 · YYYY-MM-DD HH:mm",false);
        field("exit","퇴장에 걸리는 시간 · 분",true); field("travel","공연장에서 역까지 이동 · 분",true);
        field("train","귀가 열차 출발 · YYYY-MM-DD HH:mm",false);
        field("people","인원 · 명",true); field("budget","귀가·숙박 총 예산 · 원",true);
        field("fare","당일 열차 1인 요금 · 원",true); field("hotel","숙소 전체 금액 · 원",true); field("next","다음날 열차 1인 요금 · 원",true);
        button("비교하고 저장",()->{save();calculate();});
        result=Ui.text(this,"입력 후 비교하면 결과가 여기에 표시돼요.",15,0xff111111,false);result.setTextIsSelectable(true);root.addView(result,Ui.match(this,-2,16));
        button("돌아가는 열차 시간·요금 찾기",()->search(value("city")+" "+value("origin")+" 열차 시간표 요금"));
        button("공연장 근처 숙소 찾기",()->search(value("city")+" "+value("venue")+" 숙소 가격"));
        button("공연장 주변 지도 열기",()->open(Uri.parse("https://map.naver.com/p/search/").buildUpon().appendPath(value("city")+" "+value("venue")).build()));
        label("검색에서 확인한 값과 조회 시점을 따로 확인하세요. 실제 예약·결제는 각 서비스에서 직접 진행합니다.",13,false);
        setContentView(scroll);if(prefs.getBoolean("saved",false))calculate();
    }
    private void label(String text,int size,boolean bold){root.addView(Ui.text(this,text,size,bold?0xff111111:0xff888888,bold),Ui.match(this,-2,12));}
    private void field(String key,String hint,boolean numeric){
        label(hint,13,false);EditText e=new EditText(this);e.setSingleLine(true);e.setTextColor(0xff111111);e.setHintTextColor(0xff888888);e.setHint(hint);e.setTextSize(15);e.setPadding(Ui.dp(this,12),0,Ui.dp(this,12),0);e.setBackground(Ui.bg(0xfff4f4f4,9,this));if(numeric)e.setInputType(InputType.TYPE_CLASS_NUMBER);e.setText(prefs.getString(key,""));root.addView(e,Ui.match(this,50,5));fields.put(key,e);e.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int start,int count,int after){} public void onTextChanged(CharSequence s,int start,int before,int count){if(result!=null)result.setText("입력이 변경됐어요. 다시 비교하고 저장해 주세요.");} public void afterTextChanged(Editable text){}});
    }
    private void button(String title,Runnable action){Button b=skinButton(title);b.setOnClickListener(v->action.run());root.addView(b,Ui.match(this,50,12));}
    private String value(String key){return fields.get(key).getText().toString().trim();}
    private void sample(){String[] v={"대구","서울","공연장 예시","2026-11-14 22:30","30","40","2026-11-14 23:20","2","200000","30000","100000","30000"};int i=0;for(EditText e:fields.values())e.setText(v[i++]);result.setText("연습용 가상 값입니다. 비교하고 저장을 눌러 결과를 확인하세요.");}
    private void save(){SharedPreferences.Editor edit=prefs.edit();for(Map.Entry<String,EditText> f:fields.entrySet())edit.putString(f.getKey(),f.getValue().getText().toString());edit.putBoolean("saved",true).apply();}
    private void calculate(){result.setText(ConcertDecision.calculate(value("end"),value("exit"),value("travel"),value("train"),value("people"),value("budget"),value("fare"),value("hotel"),value("next")));}
    private void search(String query){if(value("city").isEmpty()){Toast.makeText(this,"공연 도시를 입력하세요.",Toast.LENGTH_SHORT).show();return;}open(Uri.parse("https://www.google.com/search").buildUpon().appendQueryParameter("q",query.trim()).build());}
    private void open(Uri uri){try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception e){Toast.makeText(this,"열 수 있는 앱이 없습니다.",Toast.LENGTH_SHORT).show();}}
}
