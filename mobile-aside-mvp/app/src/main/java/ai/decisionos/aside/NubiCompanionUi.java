package ai.decisionos.aside;

import android.app.*;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.view.*;
import android.view.inputmethod.InputMethodManager;
import android.widget.*;
import org.json.*;
import java.util.*;

/** Nubi's own native companion shell. Public Pickle layout reference; no vendor assets or runtime. */
final class NubiCompanionUi {
 static final int INK=0xff161616,MUTED=0xff858585,WHITE=0xfffefefe;
 final GoalChatUi c;final GoalAgentActivity a;
 LinearLayout chatPage,sidePage,sideBody;ScrollView sideScroll;String page="대화";
 final Map<String,TextView> tabs=new LinkedHashMap<>();
 NubiCompanionUi(GoalChatUi c){this.c=c;a=c.a;}
 int dp(int n){return c.dp(n);}
 GradientDrawable pill(int color,int radius,boolean border){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));if(border)d.setStroke(dp(1),0xffe7e7e7);return d;}
 TextView text(String value,int size,boolean bold){return a.txt(value,size,INK,bold);}
 TextView button(String label,Runnable action){TextView b=text(label,14,false);b.setGravity(Gravity.CENTER);b.setPadding(dp(16),dp(10),dp(16),dp(10));b.setBackground(pill(WHITE,28,true));b.setMinHeight(dp(44));b.setOnClickListener(v->action.run());return b;}
 void detach(View v){if(v.getParent()!=null)((ViewGroup)v.getParent()).removeView(v);}
 void build(){
  a.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);a.getWindow().setStatusBarColor(WHITE);a.getWindow().setNavigationBarColor(WHITE);a.getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
  detach(a.web);detach(a.remoteStatus);c.workspace=null;
  android.widget.FrameLayout outer=new android.widget.FrameLayout(a);outer.setBackgroundColor(WHITE);
  LinearLayout root=c.box(WHITE,16);root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(dp(16),dp(8)+insets.getSystemWindowInsetTop(),dp(16),dp(8)+insets.getSystemWindowInsetBottom());return insets;});
  int width=a.getResources().getConfiguration().screenWidthDp;outer.addView(root,new android.widget.FrameLayout.LayoutParams(width>720?dp(680):-1,-1,Gravity.CENTER_HORIZONTAL));
  LinearLayout header=new LinearLayout(a);header.setGravity(Gravity.CENTER_VERTICAL);
  View menu=icon("menu","내 대화와 연결",()->new AlertDialog.Builder(a).setTitle("누비").setItems(new String[]{"목표별 대화","화면 선택","Qwen 연결","목표 관리"},(d,w)->{if(w==0)GoalWorkspaceUi.conversations(c);if(w==1)c.chooseLayout();if(w==2)a.pair();if(w==3)manage();}).show(),false);
  header.addView(menu,new LinearLayout.LayoutParams(dp(46),dp(46)));
  LinearLayout identity=c.box(WHITE,0);identity.setGravity(Gravity.CENTER);GoalUi.Buddy buddy=new GoalUi.Buddy(a,c.preset.color,c.preset.name);identity.addView(buddy,new LinearLayout.LayoutParams(dp(58),dp(58)));
  TextView name=button(c.preset.name+" ⌄",this::purposePicker);name.setTextSize(17);name.setTypeface(null,1);identity.addView(name);header.addView(identity,new LinearLayout.LayoutParams(0,-2,1));
  header.addView(button("목적",this::purposePicker),new LinearLayout.LayoutParams(dp(64),dp(44)));root.addView(header,Ui.match(a,-2,4));
  LinearLayout pages=c.box(WHITE,0);chatPage=c.box(WHITE,0);sidePage=c.box(WHITE,0);
  c.thread=new ScrollView(a);c.thread.setId(0x501);c.thread.setFillViewport(true);c.messages=c.box(WHITE,8);c.thread.addView(c.messages);chatPage.addView(c.thread,new LinearLayout.LayoutParams(-1,0,1));
  c.progress=text("",11,false);c.progress.setTextColor(MUTED);chatPage.addView(c.progress,Ui.match(a,-2,4));
  HorizontalScrollView suggestions=new HorizontalScrollView(a);suggestions.setHorizontalScrollBarEnabled(false);LinearLayout chips=new LinearLayout(a);for(String q:GoalWorkspaceUi.suggestions(c.character)){TextView chip=button(q,()->c.draft(q));chip.setTextSize(12);LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-2,dp(40));cp.setMargins(dp(3),0,dp(3),0);chips.addView(chip,cp);}suggestions.addView(chips);chatPage.addView(suggestions,Ui.match(a,-2,6));
  sideScroll=new ScrollView(a);sideBody=c.box(WHITE,12);sideScroll.addView(sideBody);sidePage.addView(sideScroll,new LinearLayout.LayoutParams(-1,0,1));
  // The same live WebView is kept mounted across tabs. Only its visibility changes.
  LinearLayout webPanel=c.box(WHITE,0);webPanel.setTag("web");c.address=text("실제 브라우저",12,true);webPanel.addView(c.address,Ui.match(a,-2,8));webPanel.addView(a.remoteStatus,Ui.match(a,-2,6));webPanel.addView(a.web,new LinearLayout.LayoutParams(-1,0,1));sidePage.addView(webPanel,new LinearLayout.LayoutParams(-1,0,1));webPanel.setVisibility(View.GONE);
  pages.addView(chatPage,new LinearLayout.LayoutParams(-1,-1));pages.addView(sidePage,new LinearLayout.LayoutParams(-1,-1));sidePage.setVisibility(View.GONE);root.addView(pages,new LinearLayout.LayoutParams(-1,0,1));
  LinearLayout composer=new LinearLayout(a);composer.setGravity(Gravity.CENTER_VERTICAL);composer.setPadding(dp(8),dp(5),dp(6),dp(5));composer.setBackground(pill(0xfffafafa,32,true));
  composer.addView(icon("plus","문서와 실행 기록",()->select("작업"),false),new LinearLayout.LayoutParams(dp(42),dp(44)));
  c.input=new EditText(a);c.input.setId(0x502);c.input.setContentDescription("에이전트에게 메시지");c.input.setHint("메시지 보내기");c.input.setTextColor(INK);c.input.setHintTextColor(0xffb8b8b8);c.input.setTextSize(16);c.input.setPadding(dp(6),dp(6),dp(6),dp(6));c.input.setBackgroundColor(Color.TRANSPARENT);c.input.setMaxLines(4);c.input.setInputType(131073);c.input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(1500)});c.input.setText(a.store.goal(c.goalId).optString("chatDraft"));composer.addView(c.input,new LinearLayout.LayoutParams(0,-2,1));
  c.send=new Button(a);c.send.setId(0x503);c.send.setAllCaps(false);c.send.setText(c.running?"■":"↑");c.send.setTextColor(Color.WHITE);c.send.setTextSize(23);c.send.setPadding(0,0,0,0);c.send.setBackground(pill(Color.BLACK,30,false));c.send.setContentDescription(c.running?"탐색 중지":"메시지 전송");c.send.setOnClickListener(v->{if(c.running||c.submitting)c.cancel();else{select("대화");c.submit();}});composer.addView(c.send,new LinearLayout.LayoutParams(dp(46),dp(46)));root.addView(composer,Ui.match(a,-2,8));
  LinearLayout dock=new LinearLayout(a);dock.setPadding(dp(8),dp(4),dp(8),dp(4));dock.setGravity(Gravity.CENTER);dock.setBackground(pill(0xfffafafa,40,true));String[] labels={"대화","탐색","작업","내 정보"},icons={"chat","compass","tray","person"};for(int n=0;n<labels.length;n++){final String label=labels[n];LinearLayout item=c.box(Color.TRANSPARENT,0);item.setGravity(Gravity.CENTER);item.addView(icon(icons[n],label,()->select(label),false),new LinearLayout.LayoutParams(dp(42),dp(31)));TextView caption=text(label,10,false);caption.setGravity(Gravity.CENTER);item.addView(caption);tabs.put(label,caption);item.setOnClickListener(v->select(label));dock.addView(item,new LinearLayout.LayoutParams(0,dp(48),1));}
  LinearLayout.LayoutParams dockParams=new LinearLayout.LayoutParams(dp(300),dp(60));dockParams.gravity=Gravity.CENTER_HORIZONTAL;dockParams.topMargin=dp(12);root.addView(dock,dockParams);
  a.setContentView(outer);root.requestApplyInsets();c.render();select("대화");
 }
 View icon(String kind,String description,Runnable action,boolean fill){View v=new Glyph(a,kind,fill);v.setContentDescription(description);v.setBackground(pill(WHITE,30,true));v.setOnClickListener(w->action.run());return v;}
 void manage(){a.startActivity(new Intent(a,CampusActivity.class).putExtra("section","홈"));}
 void purposePicker(){new AlertDialog.Builder(a).setTitle("어떤 목적을 맡길까?").setItems(new String[]{"건강이 · 운동","다정이 · 연애","똑똑이 · 학점","차곡이 · 집 사기"},(d,w)->c.switchAgent(new String[]{"fitness","love","grades","home"}[w])).setNeutralButton("내 목표별 대화",(d,w)->GoalWorkspaceUi.conversations(c)).setNegativeButton("닫기",null).show();}
 void select(String next){page=next;boolean chat=next.equals("대화");chatPage.setVisibility(chat?View.VISIBLE:View.GONE);sidePage.setVisibility(chat?View.GONE:View.VISIBLE);for(Map.Entry<String,TextView> e:tabs.entrySet()){e.getValue().setTextColor(e.getKey().equals(next)?INK:MUTED);e.getValue().setTypeface(null,e.getKey().equals(next)?1:0);}if(!chat)refresh();}
 void browser(){page="브라우저";chatPage.setVisibility(View.GONE);sidePage.setVisibility(View.VISIBLE);refresh();}
 void add(String title,String description,Runnable fn){LinearLayout card=c.box(0xfffafafa,16);card.setBackground(pill(0xfffafafa,22,true));card.addView(text(title,17,true));if(!description.isEmpty()){TextView desc=text(description,13,false);desc.setTextColor(MUTED);card.addView(desc,Ui.match(a,-2,6));}if(fn!=null){TextView open=button("열기 ↗",fn);card.addView(open,Ui.match(a,-2,12));}sideBody.addView(card,Ui.match(a,-2,10));}
 void refresh(){
  if(sideBody==null||page.equals("대화"))return;boolean browser=page.equals("브라우저");sideScroll.setVisibility(browser?View.GONE:View.VISIBLE);sidePage.findViewWithTag("web").setVisibility(browser?View.VISIBLE:View.GONE);if(browser)return;sideBody.removeAllViews();
  if(page.equals("탐색")){
   sideBody.addView(text("오늘, 무엇을 해볼까?",26,true));TextView intro=text("목적에 맞는 누비에게 맡겨봐.",14,false);intro.setTextColor(MUTED);sideBody.addView(intro,Ui.match(a,-2,8));
   String[] ids={"fitness","love","grades","home"};for(String id:ids){GoalRules.Preset p=GoalRules.preset(id);add(p.name+" · "+p.title,p.topic,()->{if(id.equals(c.character)){select("대화");c.draft(GoalWorkspaceUi.suggestions(id)[0]);}else c.switchAgent(id);});}
   add("실제 브라우저", "Qwen이 검색하고 원문을 여는 화면",this::browser);
  }else if(page.equals("작업")){
   sideBody.addView(text("작업과 파일",26,true));add(c.running?"진행 중":"최근 실행",c.progress.getText().toString(),null);
   JSONArray steps=latestSteps();for(int n=0;n<steps.length();n++)add(String.format(java.util.Locale.ROOT,"%02d",n+1),steps.optString(n),null);
   int files=0;for(JSONObject doc:documents()){JSONObject manifest=doc.optJSONObject("manifest");JSONArray list=manifest==null?null:manifest.optJSONArray("files");for(int n=0;list!=null&&n<list.length();n++){JSONObject file=list.optJSONObject(n);if(file==null)continue;String name=file.optString("name");if(!name.endsWith(".docx")&&!name.endsWith(".hwpx"))continue;files++;add(name,doc.optString("state").equals("uploaded")?"업로드 검증 완료":"생성된 초안 · 제출 상태는 답변 확인",()->c.openDocument(doc,file));}}
   if(files==0)add("아직 생성한 파일이 없어","문서를 요청하면 이 대화의 파일이 여기에 모여.",null);
   add("목표 일정·저장한 콘텐츠",a.store.goal(c.goalId).optString("title"),()->a.startActivity(new Intent(a,CharacterWorkspaceActivity.class).putExtra("goal_id",c.goalId).putExtra("tab",3)));
   add("실제 브라우저","탐색 중에도 화면을 확인할 수 있어.",this::browser);
  }else{
   sideBody.addView(text("나의 누비",26,true));add(c.preset.name,a.store.goal(c.goalId).optString("title"),this::purposePicker);add("연결된 Qwen",a.remoteStatus.getText().toString(),a::pair);add("내 목표별 대화","목표마다 대화·기록·파일을 따로 보관해.",()->GoalWorkspaceUi.conversations(c));add("화면 선택","누비 / 작업공간 / 기존 화면",c::chooseLayout);add("목표 관리","목표와 일정을 수정해.",this::manage);
  }
 }
 JSONArray latestSteps(){if(c.running||c.submitting)return c.steps;for(int n=c.history.length()-1;n>=0;n--){JSONObject m=c.history.optJSONObject(n);if(m!=null&&m.optString("role").equals("assistant")){JSONArray steps=m.optJSONArray("steps");return steps==null?new JSONArray():steps;}}return new JSONArray();}
 List<JSONObject> documents(){List<JSONObject> docs=new ArrayList<>();for(int n=c.history.length()-1;n>=0;n--){JSONObject m=c.history.optJSONObject(n);JSONObject d=m==null?null:m.optJSONObject("document");if(d!=null)docs.add(d);}return docs;}
 static final class Glyph extends View {
  final Paint p=new Paint(3);final String kind;final boolean fill;
  Glyph(Context c,String kind,boolean fill){super(c);this.kind=kind;this.fill=fill;}
  protected void onDraw(Canvas canvas){super.onDraw(canvas);canvas.save();canvas.translate(getWidth()/2f,getHeight()/2f);float s=Math.min(getWidth(),getHeight())/32f;canvas.scale(s,s);p.setColor(Color.BLACK);p.setStrokeWidth(1.7f);p.setStyle(Paint.Style.STROKE);p.setStrokeCap(Paint.Cap.ROUND);switch(kind){
   case "menu":canvas.drawLine(-6,-3,6,-3,p);canvas.drawLine(-6,3,6,3,p);break;
   case "plus":canvas.drawLine(-6,0,6,0,p);canvas.drawLine(0,-6,0,6,p);break;
   case "chat":p.setStyle(Paint.Style.FILL);canvas.drawOval(-9,-8,9,6,p);Path tail=new Path();tail.moveTo(-5,4);tail.lineTo(-7,9);tail.lineTo(1,5);canvas.drawPath(tail,p);break;
   case "compass":canvas.drawCircle(0,0,9,p);Path arrow=new Path();arrow.moveTo(-4,4);arrow.lineTo(1,-2);arrow.lineTo(4,-4);arrow.lineTo(2,2);arrow.close();canvas.drawPath(arrow,p);break;
   case "tray":canvas.drawRoundRect(-8,-2,8,8,2,2,p);canvas.drawLine(-8,-2,-4,-8,p);canvas.drawLine(-4,-8,4,-8,p);canvas.drawLine(4,-8,8,-2,p);canvas.drawLine(-3,3,3,3,p);break;
   default:canvas.drawCircle(0,-5,4,p);canvas.drawRoundRect(-8,2,8,9,4,4,p);
  }canvas.restore();}
 }
}
