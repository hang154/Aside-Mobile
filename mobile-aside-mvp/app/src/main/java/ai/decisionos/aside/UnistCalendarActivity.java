package ai.decisionos.aside;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Locale;

/** Live read of the public UNIST calendar endpoint used by its official page. */
public class UnistCalendarActivity extends Activity {
    private static final String PAGE="https://www.unist.ac.kr/unist/education/academic/schedule.do";
    private static final ZoneId SEOUL=ZoneId.of("Asia/Seoul");
    private LinearLayout rows;private TextView state;private Button refresh;private int generation;
    @Override public void onCreate(Bundle b){super.onCreate(b);ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(Ui.BG);LinearLayout root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"UNIST 학사일정",27,Ui.WHITE,true),Ui.match(this,-2,8));
        root.addView(Ui.text(this,"공식 학사일정에서 오늘부터 60일 동안의 일정을 불러와요. 해당 여부와 변경 사항은 원문에서 확인해 주세요.",14,Ui.MUTED,false),Ui.match(this,-2,8));
        refresh=Ui.button(this,"일정 새로고침");refresh.setOnClickListener(v->load());root.addView(refresh,Ui.match(this,48,10));
        Button official=Ui.button(this,"UNIST 공식 원문 열기");official.setOnClickListener(v->{Intent i=new Intent(this,BrowserWorkspaceActivity.class);i.putExtra("start_url",PAGE);startActivity(i);});root.addView(official,Ui.match(this,48,8));
        state=Ui.text(this,"",14,Ui.WHITE,false);root.addView(state,Ui.match(this,-2,12));rows=Ui.vertical(this,Ui.BG,0);root.addView(rows,Ui.match(this,-2,6));setContentView(scroll);load();
    }
    private void load(){final int run=++generation;refresh.setEnabled(false);state.setText("UNIST 공식 일정을 불러오는 중…");rows.removeAllViews();
        new Thread(()->{try{
            LocalDate from=LocalDate.now(SEOUL),until=from.plusDays(60);
            String url=Uri.parse(PAGE).buildUpon().appendQueryParameter("mode","getCalendarData").appendQueryParameter("siteId","unist").appendQueryParameter("start",from.toString()).appendQueryParameter("end",until.toString()).build().toString();
            HttpURLConnection conn=(HttpURLConnection)new URL(url).openConnection();conn.setConnectTimeout(10000);conn.setReadTimeout(10000);conn.setInstanceFollowRedirects(false);
            String raw;try{if(conn.getResponseCode()!=200)throw new IllegalStateException("http");try(InputStream in=conn.getInputStream();ByteArrayOutputStream bytes=new ByteArrayOutputStream()){byte[] buf=new byte[8192];int count,total=0;while((count=in.read(buf))!=-1){total+=count;if(total>1048576)throw new IllegalStateException("large");bytes.write(buf,0,count);}raw=new String(bytes.toByteArray(),StandardCharsets.UTF_8);}}finally{conn.disconnect();}
            JSONArray data=new JSONObject(raw).getJSONArray("data");ArrayList<Event> events=new ArrayList<>();
            for(int n=0;n<data.length();n++){JSONObject o=data.getJSONObject(n);String text=o.optString("content","").trim();if(text.isEmpty()||text.length()>300)continue;try{LocalDate start=LocalDate.parse(o.getString("beginDt").replace('.','-'));LocalDate end=LocalDate.parse(o.getString("endDt").replace('.','-'));if(!end.isBefore(from)&&!start.isAfter(until)&&!end.isBefore(start))events.add(new Event(start,end,text));}catch(Exception ignored){}}
            Collections.sort(events,Comparator.comparing(e->e.start));String checked=ZonedDateTime.now(SEOUL).format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm",Locale.KOREA));
            runOnUiThread(()->{if(run!=generation||isFinishing()||isDestroyed())return;refresh.setEnabled(true);state.setText("출처: UNIST 공식 학사일정 · 조회 "+checked+" (한국시간)\n조회 범위 "+from+" ~ "+until+" · "+events.size()+"건");rows.removeAllViews();for(Event e:events){TextView t=Ui.text(this,e.start+(e.start.equals(e.end)?"":" ~ "+e.end)+"\n"+e.text,15,Ui.WHITE,false);t.setPadding(Ui.dp(this,14),Ui.dp(this,12),Ui.dp(this,14),Ui.dp(this,12));t.setBackground(Ui.bg(Ui.PANEL,10,this));rows.addView(t,Ui.match(this,-2,8));}if(events.isEmpty())rows.addView(Ui.text(this,"조회된 일정이 없어요. 원문에서 다시 확인해 주세요.",14,Ui.MUTED,false));});
        }catch(Exception e){runOnUiThread(()->{if(run!=generation||isFinishing()||isDestroyed())return;refresh.setEnabled(true);state.setText("일정을 불러오지 못했어요. 인터넷 연결 또는 공식 원문을 확인해 주세요.");});}}).start();
    }
    private static final class Event {final LocalDate start,end;final String text;Event(LocalDate s,LocalDate e,String t){start=s;end=e;text=t;}}
}
