package ai.decisionos.aside;

import android.app.Activity;
import android.app.DatePickerDialog;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.provider.CalendarContract;
import android.text.InputType;
import android.widget.*;
import java.util.Calendar;
import java.util.Locale;

/** User-created plans and explicit search shortcuts; data stays on device. */
public class LifeActivity extends Activity {
    private SharedPreferences prefs;
    private EditText origin, destination, venue, people, budget, shared;
    private TextView when, summary;
    private Calendar event;
    private boolean dateSet, timeSet;
    private final String[] interests={"공연·팬덤","야구·스포츠","데이트·맛집","축제·여행","패션·뷰티","친구 모임","부업·알바","취업·대외활동","창업 지원","자취·생활"};
    @Override public void onCreate(Bundle b){
        super.onCreate(b); prefs=getSharedPreferences("life_plans",MODE_PRIVATE);
        event=Calendar.getInstance(); event.setTimeInMillis(prefs.getLong("event_time",System.currentTimeMillis()+86400000L));
        dateSet=prefs.getBoolean("event_date_set",false);timeSet=prefs.getBoolean("event_time_set",false);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(Ui.BG);
        LinearLayout root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"내 생활 계획",28,Ui.WHITE,true),Ui.match(this,-2,8));
        root.addView(Ui.text(this,"관심사를 저장하고, 나에게 필요한 계획을 차근차근 준비해요.",14,Ui.MUTED,false),Ui.match(this,-2,10));
        LinearLayout interest=card(root,"관심사");
        for(int i=0;i<interests.length;i++){
            final String key="interest_"+i; CheckBox cb=new CheckBox(this);cb.setText(interests[i]);cb.setTextColor(Ui.WHITE);
            cb.setChecked(prefs.getBoolean(key,false));cb.setOnCheckedChangeListener((button,checked)->prefs.edit().putBoolean(key,checked).apply());
            interest.addView(cb,Ui.match(this,-2,4));
        }
        LinearLayout plan=card(root,"공연·외출 계획");
        plan.addView(Ui.text(this,"공연이 끝난 뒤 이동과 숙소까지 이어서 챙겨요.",13,Ui.MUTED,false),Ui.match(this,-2,6));
        origin=field(plan,"출발지 (예: 대구)","origin"); destination=field(plan,"방문 도시 (예: 서울)","destination");
        venue=field(plan,"공연장 또는 목적지","venue");people=field(plan,"인원","people");budget=field(plan,"총 예산 (원)","budget");
        people.setInputType(InputType.TYPE_CLASS_NUMBER);budget.setInputType(InputType.TYPE_CLASS_NUMBER);
        when=Ui.text(this,"",15,Ui.WHITE,true);plan.addView(when,Ui.match(this,-2,10));updateTime();
        button(plan,"날짜 선택",()->new DatePickerDialog(this,(v,y,m,d)->{event.set(y,m,d);dateSet=true;updateTime();},event.get(Calendar.YEAR),event.get(Calendar.MONTH),event.get(Calendar.DAY_OF_MONTH)).show());
        button(plan,"공연 종료 예상 시간 선택",()->new TimePickerDialog(this,(v,h,m)->{event.set(Calendar.HOUR_OF_DAY,h);event.set(Calendar.MINUTE,m);timeSet=true;updateTime();},event.get(Calendar.HOUR_OF_DAY),event.get(Calendar.MINUTE),true).show());
        button(plan,"계획 저장",()->{savePlan(); renderPlan();});
        summary=Ui.text(this,"",14,Ui.WHITE,false);summary.setTextIsSelectable(true);plan.addView(summary,Ui.match(this,-2,12));renderPlan();
        button(plan,"돌아가는 기차 검색",()->search(required(destination)+" "+required(origin)+" "+dateQuery()+" 기차 막차 시간"));
        button(plan,"공연장 근처 숙소 검색",()->search(required(destination)+" "+required(venue)+" "+dateQuery()+" 근처 숙소 가격 비교"));
        button(plan,"공연장까지 경로 보기",()->map(required(venue).isEmpty()?required(destination):required(venue)));
        button(plan,"날씨 확인",()->search(required(destination)+" "+dateQuery()+" 날씨"));
        button(plan,"종료 예정 시간을 캘린더에 추가",this::calendar);
        LinearLayout explore=card(root,"더 찾아보기");
        explore.addView(Ui.text(this,"검색 결과에서 일정·가격·예약 가능 여부를 직접 확인하세요.",13,Ui.MUTED,false),Ui.match(this,-2,6));
        button(explore,"주변 축제·행사 찾기",()->search(required(destination)+" 축제 행사 일정"));
        button(explore,"데이트·맛집 찾기",()->search(required(destination)+" 데이트 맛집"));
        button(explore,"패션 체험단 찾기",()->search("무신사 체험단 모집"));
        button(explore,"재택 부업 찾기",()->search("한국어 재택 AI 평가 일자리"));
        button(explore,"창업 지원사업 찾기",()->search("K-Startup 창업 지원사업 공고"));
        LinearLayout share=card(root,"게시물에서 이어 찾기");
        share.addView(Ui.text(this,"공유받은 문구나 관심 키워드를 저장하고 관련 정보를 찾아요.",13,Ui.MUTED,false),Ui.match(this,-2,6));
        shared=field(share,"관심 있는 음식·장소·상품","shared");
        if(Intent.ACTION_SEND.equals(getIntent().getAction())) {String value=getIntent().getStringExtra(Intent.EXTRA_TEXT);if(value!=null)shared.setText(value.substring(0,Math.min(value.length(),2000)));}
        button(share,"관심 내용 저장",()->{prefs.edit().putString("shared",shared.getText().toString().trim()).apply();Toast.makeText(this,"저장했어요.",Toast.LENGTH_SHORT).show();});
        button(share,"비슷한 것 찾기",()->search(required(shared)+" 비슷한 추천"));
        button(share,"주변에서 찾기",()->map(required(destination)+" "+required(shared)));
        setContentView(scroll);
    }
    private LinearLayout card(LinearLayout parent,String title){LinearLayout c=Ui.vertical(this,Ui.PANEL,16);c.setBackground(Ui.bg(Ui.PANEL,16,this));parent.addView(c,Ui.match(this,-2,18));c.addView(Ui.text(this,title,19,Ui.WHITE,true));return c;}
    private EditText field(LinearLayout parent,String hint,String key){EditText e=new EditText(this);e.setSingleLine(true);e.setTextColor(Ui.WHITE);e.setHintTextColor(Ui.MUTED);e.setTextSize(15);e.setHint(hint);e.setText(prefs.getString(key,""));e.setPadding(Ui.dp(this,12),0,Ui.dp(this,12),0);e.setBackground(Ui.bg(Ui.BG,9,this));parent.addView(e,Ui.match(this,52,8));return e;}
    private void button(LinearLayout parent,String label,Runnable action){android.widget.Button b=Ui.button(this,label);b.setOnClickListener(v->action.run());parent.addView(b,Ui.match(this,48,8));}
    private String required(EditText e){return e.getText().toString().trim();}
    private String dateText(){return String.format(Locale.KOREA,"%04d-%02d-%02d",event.get(Calendar.YEAR),event.get(Calendar.MONTH)+1,event.get(Calendar.DAY_OF_MONTH));}
    private String dateQuery(){return dateSet?dateText():"";}
    private String timeText(){return (dateSet?dateText():"날짜 미선택")+(timeSet?String.format(Locale.KOREA," %02d:%02d",event.get(Calendar.HOUR_OF_DAY),event.get(Calendar.MINUTE)):" · 시간 미선택");}
    private void updateTime(){when.setText("공연 종료 예상: "+timeText());}
    private void savePlan(){prefs.edit().putString("origin",required(origin)).putString("destination",required(destination)).putString("venue",required(venue)).putString("people",required(people)).putString("budget",required(budget)).putLong("event_time",event.getTimeInMillis()).putBoolean("event_date_set",dateSet).putBoolean("event_time_set",timeSet).apply();Toast.makeText(this,"계획을 저장했어요.",Toast.LENGTH_SHORT).show();}
    private void renderPlan(){if(summary==null)return;String city=required(destination);String place=required(venue);StringBuilder s=new StringBuilder();if(city.isEmpty()&&place.isEmpty())s.append("방문 도시와 공연장을 입력해 주세요.");else s.append("목적지: ").append(city).append(" ").append(place).append("\n종료 예상: ").append(timeText()).append("\n공연 후 퇴장·이동 시간을 여유 있게 잡고 막차를 확인하세요. 막차가 어렵다면 숙소를 비교해 보세요.");if(!required(people).isEmpty())s.append("\n인원: ").append(required(people)).append("명");if(!required(budget).isEmpty())s.append(" · 예산: ").append(required(budget)).append("원");if(!required(people).isEmpty()&&!required(budget).isEmpty()){
            try{long n=Long.parseLong(required(people));long total=Long.parseLong(required(budget));
                if(n>0){s.append("\n1인당 예상 분담: ").append(total/n).append("원");if(total%n!=0)s.append(" (남는 금액 ").append(total%n).append("원)");}
                else s.append("\n인원은 1명 이상 입력하세요.");
            }catch(NumberFormatException e){s.append("\n인원과 예산을 다시 확인하세요.");}
        }summary.setText(s);}
    private void search(String query){if(query.trim().isEmpty())return;Uri uri=Uri.parse("https://www.google.com/search").buildUpon().appendQueryParameter("q",query.trim()).build();open(uri);}
    private void map(String query){if(query.trim().isEmpty()){Toast.makeText(this,"도시나 장소를 먼저 입력하세요.",Toast.LENGTH_SHORT).show();return;}open(Uri.parse("https://map.naver.com/p/search/").buildUpon().appendPath(query.trim()).build());}
    private void open(Uri uri){try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception e){Toast.makeText(this,"열 수 있는 앱이 없습니다.",Toast.LENGTH_SHORT).show();}}
    private void calendar(){if(!dateSet||!timeSet){Toast.makeText(this,"날짜와 종료 시간을 먼저 선택하세요.",Toast.LENGTH_SHORT).show();return;}Intent i=new Intent(Intent.ACTION_INSERT).setData(CalendarContract.Events.CONTENT_URI).putExtra(CalendarContract.Events.TITLE,required(venue).isEmpty()?"공연·외출 종료 예정":required(venue)+" 종료 예정").putExtra(CalendarContract.Events.EVENT_LOCATION,required(destination)+" "+required(venue)).putExtra(CalendarContract.EXTRA_EVENT_BEGIN_TIME,event.getTimeInMillis()).putExtra(CalendarContract.EXTRA_EVENT_END_TIME,event.getTimeInMillis()+3600000L);try{startActivity(i);}catch(Exception e){Toast.makeText(this,"캘린더 앱을 찾지 못했어요.",Toast.LENGTH_SHORT).show();}}
}
