package ai.decisionos.aside;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.*;

/** Suggests one bounded action; execution always requires a separate user tap. */
public class PlanAssistantActivity extends Activity {
    private EditText request;
    private TextView result;
    private android.widget.Button execute;
    private ActionProposal pending;
    @Override public void onCreate(Bundle state){
        super.onCreate(state);ScrollView scroll=new ScrollView(this);scroll.setBackgroundColor(Ui.BG);LinearLayout root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"AI와 함께 찾기",28,Ui.WHITE,true),Ui.match(this,-2,8));
        root.addView(Ui.text(this,"요청을 기기 안에서 해석하고 검색 또는 네이버 열기를 제안해요. 실행은 아래 버튼을 누를 때만 시작합니다.",14,Ui.MUTED,false),Ui.match(this,-2,12));
        request=new EditText(this);request.setTextColor(Ui.WHITE);request.setHintTextColor(Ui.MUTED);request.setHint("예: 서울 공연 근처 숙소 찾아줘");request.setSingleLine(false);request.setMinLines(2);request.setBackground(Ui.bg(Ui.PANEL,10,this));request.setPadding(Ui.dp(this,12),Ui.dp(this,10),Ui.dp(this,12),Ui.dp(this,10));root.addView(request,Ui.match(this,-2,16));
        android.widget.Button suggest=Ui.button(this,"어떻게 할지 제안받기");root.addView(suggest,Ui.match(this,52,12));
        result=Ui.text(this,"모델 준비 상태를 확인해 주세요.",15,Ui.WHITE,false);result.setTextIsSelectable(true);root.addView(result,Ui.match(this,-2,12));
        execute=Ui.button(this,"제안 실행");execute.setEnabled(false);execute.setOnClickListener(v->executeProposal());root.addView(execute,Ui.match(this,52,12));
        suggest.setOnClickListener(v->{
            String input=request.getText().toString().trim(); pending=null;execute.setEnabled(false);
            if(input.isEmpty()||input.length()>500){result.setText("요청을 1~500자로 입력하세요.");return;}
            if(!LocalModel.model(this).isFile()){result.setText("먼저 Aside 홈의 로컬 AI에서 모델 파일을 선택하세요.");return;}
            result.setText("기기에서 제안을 준비하는 중…");
            String prompt="다음 예시처럼 정확히 한 줄로 출력해.\n요청: 네이버 열어\n결과: NAVER\n요청: 대구 맛집 찾아줘\n결과: SEARCH|대구 맛집\n요청: "+input+"\n결과:";
            LocalModel.infer(this,prompt,reply->runOnUiThread(()->{pending=ActionProposal.parse(reply);if(pending.type==ActionProposal.Type.SEARCH){result.setText("제안: 웹에서 검색\n검색어: "+pending.query);execute.setEnabled(true);}else if(pending.type==ActionProposal.Type.NAVER){result.setText("제안: 네이버 홈페이지 열기");execute.setEnabled(true);}else {result.setText("실행 가능한 제안을 만들지 못했어요. 요청을 더 구체적으로 적어 주세요.");execute.setEnabled(false);}}));
        });
        setContentView(scroll);
    }
    private void executeProposal(){
        if(pending==null)return;Uri uri;
        if(pending.type==ActionProposal.Type.NAVER)uri=Uri.parse("https://www.naver.com");
        else if(pending.type==ActionProposal.Type.SEARCH)uri=Uri.parse("https://www.google.com/search").buildUpon().appendQueryParameter("q",pending.query).build();
        else return;
        try{Intent i=new Intent(this,BrowserWorkspaceActivity.class);i.putExtra("start_url",uri.toString());startActivity(i);}catch(Exception e){result.setText("브라우저를 열 수 없어요.");}
    }
}
