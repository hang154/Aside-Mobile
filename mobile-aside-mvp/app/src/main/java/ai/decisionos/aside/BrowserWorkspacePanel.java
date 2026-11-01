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
import android.webkit.ValueCallback;
import android.content.Intent;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;

/** Foreground-only WebView workspace. No Javascript interface or remote endpoint. */
final class BrowserWorkspacePanel extends CompanionPanel {
 BrowserWorkspacePanel(NubiCompanionUi ui){super(ui);}

    private WebView web;
    private EditText address;
    private TextView info;
    private String observedUrl="";
    private boolean loadFailed;
    private long webStarted;
    private boolean foreground;
    private RemoteBrowserRelay relay;
    private android.app.Dialog popupDialog;
    private ValueCallback<Uri[]> fileCallback;
    private Uri preparedDocument;
    private static final int PICK_DOCUMENT=7214;
    private JSONArray candidates=new JSONArray();
    private static final String ENUMERATE="Array.from(document.querySelectorAll('a[href],button,[role=button]')).filter(e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'}).slice(0,30)";
    private TextView chromeButton(String label,String description){TextView v=Ui.text(this,label,25,0xff171717,false);v.setGravity(android.view.Gravity.CENTER);v.setContentDescription(description);v.setBackground(Ui.bg(0xfff3f3f3,24,this));return v;}
     public void onCreate(Bundle state){super.onCreate(state);
        getWindow().setStatusBarColor(0xffffffff);getWindow().setNavigationBarColor(0xffffffff);getWindow().getDecorView().setSystemUiVisibility(android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        LinearLayout root=Ui.vertical(this,0xffffffff,12);root.setPadding(Ui.dp(this,12),Ui.dp(this,40),Ui.dp(this,12),Ui.dp(this,12));root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(Ui.dp(this,12),Ui.dp(this,12)+Math.max(insets.getSystemWindowInsetTop(),Ui.dp(this,28)),Ui.dp(this,12),Ui.dp(this,12)+insets.getSystemWindowInsetBottom());return insets;});
        LinearLayout header=new LinearLayout(this);header.setGravity(android.view.Gravity.CENTER_VERTICAL);
        TextView back=chromeButton("‹","뒤로");header.addView(back,new LinearLayout.LayoutParams(Ui.dp(this,44),Ui.dp(this,44)));
        TextView title=Ui.text(this,"브라우저",19,0xff151515,true);title.setGravity(android.view.Gravity.CENTER);header.addView(title,new LinearLayout.LayoutParams(0,Ui.dp(this,44),1));
        TextView menu=chromeButton("⋯","브라우저 메뉴");header.addView(menu,new LinearLayout.LayoutParams(Ui.dp(this,44),Ui.dp(this,44)));root.addView(header,Ui.match(this,-2,4));
        LinearLayout nav=new LinearLayout(this);nav.setGravity(android.view.Gravity.CENTER_VERTICAL);nav.setPadding(Ui.dp(this,15),0,Ui.dp(this,5),0);nav.setBackground(Ui.bg(0xfff1f1f1,24,this));
        address=new EditText(this);address.setSingleLine(true);address.setTextColor(0xff202020);address.setHintTextColor(0xff888888);address.setTextSize(14);address.setBackgroundColor(android.graphics.Color.TRANSPARENT);address.setHint("웹 주소 입력");address.setContentDescription("웹 주소");address.setText("https://example.com");address.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_URI);address.setImeOptions(android.view.inputmethod.EditorInfo.IME_ACTION_GO);nav.addView(address,new LinearLayout.LayoutParams(0,Ui.dp(this,48),1));
        TextView go=chromeButton("→","주소 열기");nav.addView(go,new LinearLayout.LayoutParams(Ui.dp(this,40),Ui.dp(this,40)));root.addView(nav,Ui.match(this,48,8));
        web=new WebView(this){ public boolean dispatchTouchEvent(android.view.MotionEvent e){if(e.getActionMasked()==android.view.MotionEvent.ACTION_UP)CollectorStore.record(BrowserWorkspacePanel.this,getPackageName(),"web_touch",0);return super.dispatchTouchEvent(e);}};web.getSettings().setJavaScriptEnabled(true);web.getSettings().setDomStorageEnabled(true);web.getSettings().setAllowFileAccess(false);web.getSettings().setAllowContentAccess(false);web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);web.getSettings().setSupportMultipleWindows(true);web.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW);web.setWebChromeClient(new PopupChromeClient());
        web.setWebViewClient(new WebViewClient(){
             public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest req){Uri u=req.getUrl();if(!"https".equalsIgnoreCase(u.getScheme())){if(req.isForMainFrame()){loadFailed=true;info.setText("HTTPS가 아닌 이동은 차단했어요.");}return true;}return false;}
             public void onPageStarted(WebView v,String url,Bitmap icon){endWeb();observedUrl="";candidates=new JSONArray();loadFailed=false;address.setText(url);info.setText("페이지를 불러오는 중");}
             public void onReceivedError(WebView v,WebResourceRequest req,android.webkit.WebResourceError error){if(req.isForMainFrame()){loadFailed=true;info.setText("페이지를 열지 못했어요. 주소와 연결을 확인하세요.");}}
             public void onPageFinished(WebView v,String url){address.setText(url);if(!loadFailed && url.startsWith("https://")){info.setText("");beginWeb();}}
             public void doUpdateVisitedHistory(WebView v,String url,boolean reload){super.doUpdateVisitedHistory(v,url,reload);if(url!=null && !address.hasFocus())address.setText(url);if(!observedUrl.isEmpty()&&!observedUrl.equals(url)){observedUrl="";candidates=new JSONArray();}}
        });
        info=Ui.text(this,"",12,0xff777777,false);root.addView(info,Ui.match(this,-2,2));
        root.addView(web,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        relay=new RemoteBrowserRelay(a,web,text->info.setText(text));
        menu.setOnClickListener(v->{PopupMenu popup=new PopupMenu(this,menu);String[] entries={"새로고침","앞으로","화면 관찰","항목 선택","검색어 입력","아래로","원격 연결","연결 끊기","브라우저 닫기"};for(int n=0;n<entries.length;n++)popup.getMenu().add(0,n, n,entries[n]);popup.setOnMenuItemClickListener(item->{switch(item.getItemId()){case 0:web.reload();break;case 1:if(web.canGoForward())web.goForward();break;case 2:observe();break;case 3:choose();break;case 4:enterSearch();break;case 5:web.pageDown(false);break;case 6:pairRemote();break;case 7:relay.stop();info.setText("원격 연결을 끊었어요.");break;case 8:finish();break;}return true;});popup.show();});
        go.setOnClickListener(v->navigate());address.setOnEditorActionListener((v,action,event)->{if(action==android.view.inputmethod.EditorInfo.IME_ACTION_GO){navigate();return true;}return false;});back.setOnClickListener(v->{if(web.canGoBack())web.goBack();else finish();});setContentView(root);root.requestApplyInsets();
        Uri candidate=getIntent().getData();if(candidate!=null&&"content".equals(candidate.getScheme())&&(getPackageName()+".documents").equals(candidate.getAuthority()))preparedDocument=candidate;
        String initial=getIntent().getStringExtra("start_url");if(initial!=null){address.setText(initial);navigate();}
    }
    void openIntent(Intent intent){panelIntent=intent;Uri candidate=intent.getData();if(candidate!=null&&"content".equals(candidate.getScheme())&&(getPackageName()+".documents").equals(candidate.getAuthority()))preparedDocument=candidate;String initial=intent.getStringExtra("start_url");if(initial!=null){address.setText(initial);navigate();}}
    private void pairRemote(){EditText pairing=new EditText(this);pairing.setSingleLine(true);pairing.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);pairing.setHint("https://서버:포트|연결키|인증서지문");new AlertDialog.Builder(this).setTitle("브라우저 원격 연결").setMessage("신뢰하는 서버의 연결 정보만 입력해 주세요. 테스트 연결은 공개 위키 조회에 한정되며 화면을 벗어나면 중지됩니다.").setView(pairing).setNegativeButton("취소",null).setPositiveButton("연결",(d,w)->{try{relay.connect(pairing.getText().toString());}catch(Exception ex){info.setText("연결 실패 · "+ex.getMessage());}}).show();}

    /** User-initiated popup is a separate view with the same app WebView session. */
    private final class PopupChromeClient extends WebChromeClient {
         public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params){
            if(fileCallback!=null)fileCallback.onReceiveValue(null);fileCallback=callback;
            Uri current=Uri.parse(view.getUrl()==null?"":view.getUrl());
            if(preparedDocument!=null&&"https".equalsIgnoreCase(current.getScheme())&&"chatgpt.com".equalsIgnoreCase(current.getHost())){
                new AlertDialog.Builder(BrowserWorkspacePanel.this).setTitle("ChatGPT에 문서 첨부")
                  .setMessage("선택한 문서를 ChatGPT에 첨부해요. 전송할 내용은 ChatGPT에서 확인해 주세요.")
                  .setPositiveButton("준비한 문서",(d,w)->{Uri selected=preparedDocument;preparedDocument=null;finishFileChoice(new Uri[]{selected});})
                  .setNeutralButton("다른 파일",(d,w)->pickDocument())
                  .setNegativeButton("취소",(d,w)->finishFileChoice(null)).setOnCancelListener(d->finishFileChoice(null)).show();return true;
            }
            pickDocument();return true;
        }
         public boolean onCreateWindow(WebView parent,boolean isDialog,boolean isUserGesture,android.os.Message resultMsg){
            if(!isUserGesture || popupDialog!=null || resultMsg==null || !(resultMsg.obj instanceof WebView.WebViewTransport))return false;
            final WebView child=new WebView(BrowserWorkspacePanel.this);
            child.getSettings().setJavaScriptEnabled(true);child.getSettings().setDomStorageEnabled(true);
            child.getSettings().setAllowFileAccess(false);child.getSettings().setAllowContentAccess(false);
            child.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW);
            child.setWebViewClient(new WebViewClient(){
                 public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest req){return !"https".equalsIgnoreCase(req.getUrl().getScheme());}
            });
            android.app.Dialog dialog=new android.app.Dialog(BrowserWorkspacePanel.this);popupDialog=dialog;
            LinearLayout panel=new LinearLayout(BrowserWorkspacePanel.this);panel.setOrientation(LinearLayout.VERTICAL);
            Button close=skinButton("창 닫기");close.setOnClickListener(v->dialog.dismiss());
            panel.addView(close,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,Ui.dp(BrowserWorkspacePanel.this,48)));
            panel.addView(child,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));dialog.setContentView(panel);
            dialog.setOnDismissListener(d->{popupDialog=null;child.stopLoading();child.destroy();});
            ((WebView.WebViewTransport)resultMsg.obj).setWebView(child);resultMsg.sendToTarget();dialog.show();
            if(dialog.getWindow()!=null)dialog.getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT);
            return true;
        }
    }
    private void pickDocument(){try{Intent pick=new Intent(Intent.ACTION_GET_CONTENT).addCategory(Intent.CATEGORY_OPENABLE).setType("*/*");startActivityForResult(Intent.createChooser(pick,"첨부할 파일 선택"),PICK_DOCUMENT);}catch(Exception e){finishFileChoice(null);info.setText("파일 선택기를 열지 못했어요.");}}
    private void finishFileChoice(Uri[] values){if(fileCallback!=null){ValueCallback<Uri[]> cb=fileCallback;fileCallback=null;cb.onReceiveValue(values);}}
     protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==PICK_DOCUMENT){Uri u=result==RESULT_OK&&data!=null?data.getData():null;finishFileChoice(u==null?null:new Uri[]{u});}}
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
    private void beginWeb(){if(foreground && webStarted==0 && CollectorStore.allowed(this,getPackageName())){webStarted=android.os.SystemClock.elapsedRealtime();CollectorStore.record(this,getPackageName(),"web_page_open",0);}}
    private void endWeb(){if(webStarted!=0){CollectorStore.record(this,getPackageName(),"web_page_end",android.os.SystemClock.elapsedRealtime()-webStarted);webStarted=0;}}
     protected void onPause(){if(relay!=null)relay.stop();endWeb();foreground=false;super.onPause();}
     protected void onResume(){super.onResume();foreground=true;if(web!=null && web.getUrl()!=null && web.getUrl().startsWith("https://"))beginWeb();}
     public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
     protected void onDestroy(){finishFileChoice(null);if(popupDialog!=null)popupDialog.dismiss();if(web!=null){web.stopLoading();web.destroy();}super.onDestroy();}
}
