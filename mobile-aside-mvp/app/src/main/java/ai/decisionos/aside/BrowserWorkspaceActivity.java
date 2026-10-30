package ai.decisionos.aside;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;

/** Foreground-only WebView workspace. No Javascript interface or remote endpoint. */
public class BrowserWorkspaceActivity extends Activity {
    private WebView web;
    private EditText address;
    private TextView info;
    private String observedUrl="";
    private JSONArray candidates=new JSONArray();
    private static final String ENUMERATE="Array.from(document.querySelectorAll('a[href],button,[role=button]')).filter(e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'}).slice(0,30)";
    @Override public void onCreate(Bundle state){super.onCreate(state);
        LinearLayout root=Ui.vertical(this,Ui.BG,12);
        root.addView(Ui.text(this,"Aside 브라우저 작업 공간",22,Ui.WHITE,true),Ui.match(this,-2,2));
        root.addView(Ui.text(this,"사용자 전용 웹 공간 · 원격 연결 준비 전 · 로그인과 인증은 직접 진행",12,Ui.MUTED,false),Ui.match(this,-2,4));
        LinearLayout nav=new LinearLayout(this); address=new EditText(this);address.setSingleLine(true);address.setTextColor(Ui.WHITE);address.setHintTextColor(Ui.MUTED);address.setTextSize(14);address.setHint("https:// 주소 입력");address.setText("https://example.com");nav.addView(address,new LinearLayout.LayoutParams(0,Ui.dp(this,48),1));
        Button go=Ui.button(this,"열기");nav.addView(go,new LinearLayout.LayoutParams(Ui.dp(this,70),Ui.dp(this,48)));root.addView(nav,Ui.match(this,-2,4));
        web=new WebView(this);web.getSettings().setJavaScriptEnabled(true);web.getSettings().setDomStorageEnabled(true);web.getSettings().setAllowFileAccess(false);web.getSettings().setAllowContentAccess(false);web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);web.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW);web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest req){Uri u=req.getUrl();return !"https".equalsIgnoreCase(u.getScheme());}
            @Override public void onPageStarted(WebView v,String url,Bitmap icon){observedUrl="";candidates=new JSONArray();address.setText(url);info.setText("페이지를 불러오는 중");}
            @Override public void onPageFinished(WebView v,String url){address.setText(url);info.setText("페이지 준비됨 · 관찰을 눌러 선택지를 확인하세요");}
            @Override public void doUpdateVisitedHistory(WebView v,String url,boolean reload){super.doUpdateVisitedHistory(v,url,reload);if(url!=null && !address.hasFocus())address.setText(url);if(!observedUrl.isEmpty()&&!observedUrl.equals(url)){observedUrl="";candidates=new JSONArray();}}
        });
        root.addView(web,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        LinearLayout bar=new LinearLayout(this);Button back=Ui.button(this,"뒤로");Button observe=Ui.button(this,"화면 관찰");Button select=Ui.button(this,"항목 선택");Button type=Ui.button(this,"검색어 입력");Button down=Ui.button(this,"아래로");
        for(Button b:new Button[]{back,observe,select,type,down})bar.addView(b,new LinearLayout.LayoutParams(0,Ui.dp(this,48),1));root.addView(bar,Ui.match(this,-2,6));
        info=Ui.text(this,"HTTPS 주소를 열어 주세요.",12,Ui.MUTED,false);root.addView(info,Ui.match(this,-2,5));
        go.setOnClickListener(v->navigate());back.setOnClickListener(v->{if(web.canGoBack())web.goBack();});observe.setOnClickListener(v->observe());select.setOnClickListener(v->choose());type.setOnClickListener(v->enterSearch());down.setOnClickListener(v->web.pageDown(false));setContentView(root);
        String initial=getIntent().getStringExtra("start_url");if(initial!=null){address.setText(initial);navigate();}
    }
    private void navigate(){String url=address.getText().toString().trim();try{Uri u=Uri.parse(url);if(!"https".equalsIgnoreCase(u.getScheme())||u.getHost()==null||u.getUserInfo()!=null)throw new IllegalArgumentException();address.clearFocus();web.loadUrl(url);}catch(Exception e){info.setText("HTTPS 웹 주소만 열 수 있어요.");}}
    private void observe(){if(web.getUrl()==null||!web.getUrl().startsWith("https://")){info.setText("먼저 HTTPS 페이지를 열어 주세요.");return;}
        final String url=web.getUrl();String js="(()=>JSON.stringify("+ENUMERATE+".map(e=>(e.innerText||e.getAttribute('aria-label')||e.getAttribute('title')||'이름 없는 항목').trim().slice(0,80))))()";
        web.evaluateJavascript(js,answer->{try{if(!url.equals(web.getUrl()))return;String decoded=new JSONArray("["+answer+"]").getString(0);candidates=new JSONArray(decoded);observedUrl=url;info.setText("항목 "+candidates.length()+"개 발견 · 항목 선택을 눌러 확인하세요");}catch(Exception ex){info.setText("페이지 항목을 읽지 못했어요.");}});
    }
    private void choose(){if(!observedUrl.equals(web.getUrl())||candidates.length()==0){info.setText("먼저 현재 페이지를 관찰해 주세요.");return;}
        String[] labels=new String[candidates.length()];for(int i=0;i<labels.length;i++)labels[i]=candidates.optString(i,"이름 없는 항목");
        new AlertDialog.Builder(this).setTitle("열거나 누를 항목 선택").setItems(labels,(dialog,index)->new AlertDialog.Builder(this).setTitle("이 항목을 실행할까요?").setMessage(labels[index]+"\n\n사이트의 버튼은 주문·전송 등 실제 동작을 수행할 수 있습니다.").setNegativeButton("취소",null).setPositiveButton("실행",(d,w)->click(index,labels[index])).show()).setNegativeButton("닫기",null).show();
    }
    private void enterSearch(){
        if(web.getUrl()==null||!web.getUrl().startsWith("https://")){info.setText("먼저 HTTPS 페이지를 열어 주세요.");return;}
        final String url=web.getUrl();EditText entry=new EditText(this);entry.setSingleLine(true);entry.setHint("검색어");
        new AlertDialog.Builder(this).setTitle("검색어 직접 입력").setMessage("검색 전용 입력란에만 넣어요. 비밀번호·인증번호는 직접 입력하세요.").setView(entry).setNegativeButton("취소",null).setPositiveButton("입력",(d,w)->{
            String value=entry.getText().toString();if(value.isEmpty()||value.length()>200||!url.equals(web.getUrl())){info.setText("검색어 또는 페이지를 확인하세요.");return;}
            String js="(()=>{let e=document.querySelector('input[type=search]');if(!e||e.disabled||e.readOnly)return 'missing';e.focus();let setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;setter.call(e,"+JSONObject.quote(value)+");e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return 'typed'})()";
            web.evaluateJavascript(js,r->info.setText("\"typed\"".equals(r)?"검색어를 입력했어요. 검색 실행은 직접 확인하세요.":"검색 전용 입력란을 찾지 못했어요."));
        }).show();
    }
    private void click(int index,String label){if(!observedUrl.equals(web.getUrl())){info.setText("페이지가 바뀌었어요. 다시 관찰해 주세요.");return;}
        String js="(()=>{let a="+ENUMERATE+",e=a["+index+"];if(!e)return 'changed';let t=(e.innerText||e.getAttribute('aria-label')||e.getAttribute('title')||'이름 없는 항목').trim().slice(0,80);if(t!=="+JSONObject.quote(label)+")return 'changed';e.click();return 'clicked'})()";
        web.evaluateJavascript(js,r->{observedUrl="";candidates=new JSONArray();info.setText("\"clicked\"".equals(r)?"실행 요청을 보냈어요. 페이지에서 결과를 확인하세요.":"항목이 바뀌었어요. 다시 관찰해 주세요.");});
    }
    @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){if(web!=null){web.stopLoading();web.destroy();}super.onDestroy();}
}
