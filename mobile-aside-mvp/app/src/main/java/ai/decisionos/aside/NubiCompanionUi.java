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
 LinearLayout sidebar,composer; boolean wide; String category="전체",libraryTab="아티팩트";
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
  LinearLayout shell=new LinearLayout(a);shell.setOrientation(LinearLayout.HORIZONTAL);outer.addView(shell,new android.widget.FrameLayout.LayoutParams(-1,-1));
  wide=a.getResources().getConfiguration().screenWidthDp>=840;
  sidebar=c.box(WHITE,16);sidebar.setPadding(dp(16),dp(42),dp(16),dp(16));shell.addView(sidebar,new LinearLayout.LayoutParams(dp((int)(a.getResources().getConfiguration().screenWidthDp*.216f)),-1));sidebar.setVisibility(wide?View.VISIBLE:View.GONE);buildSidebar();
  LinearLayout root=c.box(WHITE,16);shell.addView(root,new LinearLayout.LayoutParams(0,-1,1));root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(dp(16),dp(8)+insets.getSystemWindowInsetTop(),dp(16),dp(8)+insets.getSystemWindowInsetBottom());return insets;});

  LinearLayout header=new LinearLayout(a);header.setGravity(Gravity.CENTER_VERTICAL);
  View menu=icon("menu","메뉴 열기",()->{if(wide)sidebar.setVisibility(sidebar.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE);else new AlertDialog.Builder(a).setTitle("누비").setItems(new String[]{"기본 채팅","목적별 누비","둘러보기","보관함","나의 누비"},(d,w)->select(new String[]{"대화","목적","탐색","작업","내 정보"}[w])).show();},false);
  header.addView(menu,new LinearLayout.LayoutParams(dp(46),dp(46)));
  LinearLayout identity=c.box(WHITE,0);identity.setGravity(Gravity.CENTER);GoalUi.Buddy buddy=new GoalUi.Buddy(a,c.preset.color,c.preset.name);identity.addView(buddy,new LinearLayout.LayoutParams(dp(52),dp(52)));
  TextView name=button(c.preset.name+" ⌄",this::purposePicker);name.setPadding(dp(12),0,dp(12),0);name.setMinHeight(0);name.setTextSize(15);name.setTypeface(null,1);LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(-2,dp(34));np.gravity=Gravity.CENTER;identity.addView(name,np);header.addView(identity,new LinearLayout.LayoutParams(0,-2,1));
  header.addView(button("목적",this::purposePicker),new LinearLayout.LayoutParams(dp(64),dp(44)));root.addView(header,Ui.match(a,90,4));
  LinearLayout pages=c.box(WHITE,0);chatPage=c.box(WHITE,0);sidePage=c.box(WHITE,0);
  c.thread=new ScrollView(a);c.thread.setId(0x501);c.thread.setFillViewport(true);c.messages=c.box(WHITE,8);c.thread.addView(c.messages);chatPage.addView(c.thread,new LinearLayout.LayoutParams(-1,0,1));
  c.progress=text("",11,false);c.progress.setTextColor(MUTED);chatPage.addView(c.progress,Ui.match(a,-2,4));
  HorizontalScrollView suggestions=new HorizontalScrollView(a);suggestions.setHorizontalScrollBarEnabled(false);LinearLayout chips=new LinearLayout(a);for(String q:GoalWorkspaceUi.suggestions(c.character)){TextView chip=button(q,()->c.draft(q));chip.setTextSize(12);LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-2,dp(40));cp.setMargins(dp(3),0,dp(3),0);chips.addView(chip,cp);}suggestions.addView(chips);suggestions.setVisibility(View.GONE);chatPage.addView(suggestions,Ui.match(a,-2,6));
  sideScroll=new ScrollView(a);sideBody=c.box(WHITE,12);sideScroll.addView(sideBody);sidePage.addView(sideScroll,new LinearLayout.LayoutParams(-1,0,1));
  // The same live WebView is kept mounted across tabs. Only its visibility changes.
  LinearLayout webPanel=c.box(WHITE,0);webPanel.setTag("web");c.address=text("실제 브라우저",12,true);webPanel.addView(c.address,Ui.match(a,-2,8));webPanel.addView(a.remoteStatus,Ui.match(a,-2,6));webPanel.addView(a.web,new LinearLayout.LayoutParams(-1,0,1));sidePage.addView(webPanel,new LinearLayout.LayoutParams(-1,0,1));webPanel.setVisibility(View.GONE);
  pages.addView(chatPage,new LinearLayout.LayoutParams(-1,-1));pages.addView(sidePage,new LinearLayout.LayoutParams(-1,-1));sidePage.setVisibility(View.GONE);root.addView(pages,new LinearLayout.LayoutParams(-1,0,1));
  composer=new LinearLayout(a);composer.setGravity(Gravity.CENTER_VERTICAL);composer.setPadding(dp(8),dp(5),dp(6),dp(5));composer.setBackground(pill(0xfff0f0f0,32,false));
  composer.addView(icon("plus","문서와 실행 기록",()->select("작업"),false),new LinearLayout.LayoutParams(dp(42),dp(44)));
  c.input=new EditText(a);c.input.setId(0x502);c.input.setContentDescription("에이전트에게 메시지");c.input.setHint("메시지 보내기");c.input.setTextColor(INK);c.input.setHintTextColor(0xffb8b8b8);c.input.setTextSize(16);c.input.setPadding(dp(6),dp(6),dp(6),dp(6));c.input.setBackgroundColor(Color.TRANSPARENT);c.input.setMaxLines(4);c.input.setInputType(131073);c.input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(1500)});c.input.setText(a.store.goal(c.goalId).optString("chatDraft"));composer.addView(c.input,new LinearLayout.LayoutParams(0,-2,1));
  c.send=new Button(a);c.send.setId(0x503);c.send.setAllCaps(false);c.send.setText(c.running?"■":"↑");c.send.setTextColor(Color.WHITE);c.send.setTextSize(23);c.send.setPadding(0,0,0,0);c.send.setBackground(pill(Color.BLACK,30,false));c.send.setContentDescription(c.running?"탐색 중지":"메시지 전송");c.send.setOnClickListener(v->{if(c.running||c.submitting)c.cancel();else{select("대화");c.submit();}});composer.addView(c.send,new LinearLayout.LayoutParams(dp(46),dp(46)));root.addView(composer,Ui.match(a,-2,8));
  LinearLayout dock=new LinearLayout(a);dock.setPadding(dp(8),dp(4),dp(8),dp(4));dock.setGravity(Gravity.CENTER);dock.setBackground(pill(0xfffafafa,40,true));String[] labels={"대화","탐색","작업","내 정보"},icons={"chat","compass","tray","person"};for(int n=0;n<labels.length;n++){final String label=labels[n];LinearLayout item=c.box(Color.TRANSPARENT,0);item.setGravity(Gravity.CENTER);item.addView(icon(icons[n],label,()->select(label),false),new LinearLayout.LayoutParams(dp(42),dp(31)));TextView caption=text(label,10,false);caption.setGravity(Gravity.CENTER);item.addView(caption);tabs.put(label,caption);item.setOnClickListener(v->select(label));dock.addView(item,new LinearLayout.LayoutParams(0,dp(48),1));}
  LinearLayout.LayoutParams dockParams=new LinearLayout.LayoutParams(dp(300),dp(60));dockParams.gravity=Gravity.CENTER_HORIZONTAL;dockParams.topMargin=dp(12);root.addView(dock,dockParams);dock.setVisibility(wide?View.GONE:View.VISIBLE);
  a.setContentView(outer);root.requestApplyInsets();c.render();select("대화");
 }
 View icon(String kind,String description,Runnable action,boolean fill){View v=new Glyph(a,kind,fill);v.setContentDescription(description);v.setBackground(pill(WHITE,30,true));v.setOnClickListener(w->action.run());return v;}
 void manage(){a.startActivity(new Intent(a,CampusActivity.class).putExtra("section","홈"));}
 void purposePicker(){new AlertDialog.Builder(a).setTitle("어떤 목적을 맡길까?").setItems(new String[]{"건강이 · 운동","다정이 · 연애","똑똑이 · 학점","차곡이 · 집 사기"},(d,w)->c.switchAgent(new String[]{"fitness","love","grades","home"}[w])).setNeutralButton("내 목표별 대화",(d,w)->GoalWorkspaceUi.conversations(c)).setNegativeButton("닫기",null).show();}
 void select(String next){page=next;updateSidebar();boolean chat=next.equals("대화");composer.setVisibility(chat?View.VISIBLE:View.GONE);chatPage.setVisibility(chat?View.VISIBLE:View.GONE);sidePage.setVisibility(chat?View.GONE:View.VISIBLE);for(Map.Entry<String,TextView> e:tabs.entrySet()){e.getValue().setTextColor(e.getKey().equals(next)?INK:MUTED);e.getValue().setTypeface(null,e.getKey().equals(next)?1:0);}if(!chat)refresh();}
 void browser(){composer.setVisibility(View.GONE);page="브라우저";chatPage.setVisibility(View.GONE);sidePage.setVisibility(View.VISIBLE);refresh();}
 void add(String title,String description,Runnable fn){LinearLayout card=c.box(0xfffafafa,16);card.setBackground(pill(0xfffafafa,22,true));card.addView(text(title,17,true));if(!description.isEmpty()){TextView desc=text(description,13,false);desc.setTextColor(MUTED);card.addView(desc,Ui.match(a,-2,6));}if(fn!=null){TextView open=button("열기 ↗",fn);card.addView(open,Ui.match(a,-2,12));}sideBody.addView(card,Ui.match(a,-2,10));}
 void refresh(){
  if(sideBody==null||page.equals("대화"))return;boolean browser=page.equals("브라우저");sideScroll.setVisibility(browser?View.GONE:View.VISIBLE);sidePage.findViewWithTag("web").setVisibility(browser?View.VISIBLE:View.GONE);if(browser)return;sideBody.removeAllViews();
  if(page.equals("탐색")){
   sideBody.addView(text("둘러보기",22,true));
   HorizontalScrollView filters=new HorizontalScrollView(a);filters.setHorizontalScrollBarEnabled(false);LinearLayout chips=new LinearLayout(a);for(String label:new String[]{"전체","운동","연애","학점","집","쇼핑","일·서류"}){TextView chip=button(label,()->{category=label;refresh();});chip.setBackground(pill(label.equals(category)?INK:0xfff4f4f4,26,false));chip.setTextColor(label.equals(category)?WHITE:INK);LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-2,dp(40));cp.setMargins(0,0,dp(8),0);chips.addView(chip,cp);}filters.addView(chips);sideBody.addView(filters,Ui.match(a,-2,16));
   muted("지금 누비에게 맡겨볼 일");
   String[][] recipes={{"운동","초보 스트레칭, 나에게 맞는 영상 찾아줘","오늘 따라 할 영상을 비교하고 원문까지 확인해요.","초보자 스트레칭 영상 2개를 찾아 제목과 출처를 알려줘. 하나는 직접 열어서 확인해줘."},{"연애","비 오는 날에도 괜찮은 데이트","부산 실내 데이트 후보와 이동 계획을 찾아요.","부산 비 오는 날 실내 데이트 장소 2개를 찾아 원문을 확인하고 출처를 알려줘."},{"학점","파이썬 공부, 어디서 시작할까?","입문 자료를 찾아 읽고 비교해요.","파이썬 입문 학습 자료 2개를 찾아 하나는 원문을 열고 제목과 출처를 알려줘."},{"집","내 집 마련, 준비부터 차근차근","공개 자료와 영상에서 준비할 일을 확인해요.","내 집 마련 준비 영상 2개를 찾아 하나는 열고 제목과 출처를 알려줘."},{"쇼핑","필요한 준비물, 판매처에서 비교","상품 검색 결과와 옵션은 판매처에서 확인해요.","요가 매트를 검색해서 실제 상품 후보와 출처를 보여줘. 결제는 하지 마."},{"일·서류","학교 메일에서 필요한 서류까지","연결된 메일과 문서 작업을 대화로 요청해요.","UNIST 학사 공지에서 최근 장학 공고를 찾아 제목과 출처를 알려줘."}};
   for(String[] r:recipes)if(category.equals("전체")||category.equals(r[0]))recipe(r[1],r[2],r[3]);
   recipe("원하는 일을 직접 부탁하기","검색부터 원문 확인까지, 조건을 알려주세요.","");
  }else if(page.equals("목적")){
   sideBody.addView(text("목적별 누비",22,true));muted("목적마다 대화와 기록을 따로 보관해요.");for(String id:new String[]{"fitness","love","grades","home"}){GoalRules.Preset p=GoalRules.preset(id);add(p.name+" · "+p.title,p.topic,()->{c.switchAgent(id);if(id.equals(c.character))select("대화");});}
  }else if(page.equals("작업")){
   sideBody.addView(text("보관함",22,true));LinearLayout segments=new LinearLayout(a);for(String tab:new String[]{"아티팩트","미디어","실행 기록"}){TextView item=button(tab,()->{libraryTab=tab;refresh();});item.setBackground(pill(tab.equals(libraryTab)?WHITE:0xfff2f2f2,24,false));segments.addView(item,new LinearLayout.LayoutParams(0,dp(44),1));}segments.setBackground(pill(0xfff2f2f2,26,false));sideBody.addView(segments,Ui.match(a,-2,18));int count=0;
   if(libraryTab.equals("실행 기록")){JSONArray steps=latestSteps();for(int n=0;n<steps.length();n++)add(String.format(java.util.Locale.ROOT,"%02d",n+1),steps.optString(n),null);count=steps.length();add("실제 브라우저","누비가 탐색하는 페이지 확인",this::browser);}
   else if(libraryTab.equals("미디어")){for(JSONObject item:a.store.list("contents",c.goalId))if(item.optBoolean("saved")&&!item.optBoolean("hidden")){count++;add(item.optString("title"),item.optString("provider"),()->c.showSource(item.optString("url")));}}
   else for(JSONObject doc:documents()){JSONObject manifest=doc.optJSONObject("manifest");JSONArray list=manifest==null?null:manifest.optJSONArray("files");for(int n=0;list!=null&&n<list.length();n++){JSONObject file=list.optJSONObject(n);if(file==null)continue;String name=file.optString("name");if(!name.endsWith(".docx")&&!name.endsWith(".hwpx"))continue;count++;add(name,doc.optString("state").equals("uploaded")?"업로드 검증 완료":"생성된 문서 · 제출 상태는 답변 확인",()->c.openDocument(doc,file));}}
   if(count==0){TextView empty=text(libraryTab.equals("미디어")?"아직 저장한 미디어가 없어요":libraryTab.equals("실행 기록")?"아직 실행 기록이 없어요":"아직 생성한 문서가 없어요",18,true);empty.setGravity(Gravity.CENTER);empty.setPadding(0,dp(100),0,dp(12));sideBody.addView(empty);muted("누비와 함께 필요한 자료를 찾아보세요.");}
   TextView create=button("+  새로 부탁하기",()->{select("대화");c.draft(libraryTab.equals("아티팩트")?"문서를 만들어줘. ":"");});sideBody.addView(create,Ui.match(a,-2,24));
   add("목표 일정·저장한 콘텐츠",a.store.goal(c.goalId).optString("title"),()->a.startActivity(new Intent(a,CharacterWorkspaceActivity.class).putExtra("goal_id",c.goalId).putExtra("tab",3)));
  }else{
   sideBody.addView(text("나의 누비",22,true));add(c.preset.name,a.store.goal(c.goalId).optString("title"),this::purposePicker);add("누비에 연결된 앱 및 서비스",a.remoteStatus.getText().toString(),()->new AlertDialog.Builder(a).setTitle("연결할 서비스").setItems(new String[]{"에이전트 연결","학교 메일·포털","브라우저"},(d,w)->{if(w==0)a.pair();if(w==1)a.startActivity(new Intent(a,CampusToolsActivity.class));if(w==2)browser();}).show());add("내 목표별 대화","목표마다 대화·기록·파일을 따로 보관해요.",()->GoalWorkspaceUi.conversations(c));add("화면 및 디자인","누비 / 작업공간 / 기존 화면",c::chooseLayout);add("목표 관리","목표와 일정을 수정해요.",this::manage);
  }
 }
 void muted(String value){TextView v=text(value,13,false);v.setTextColor(MUTED);sideBody.addView(v,Ui.match(a,-2,16));}
 void recipe(String title,String desc,String prompt){LinearLayout row=c.box(WHITE,12);row.addView(text(title+"  ›",18,true));TextView note=text(desc,14,false);note.setTextColor(MUTED);row.addView(note,Ui.match(a,-2,8));row.setContentDescription(title);row.setOnClickListener(v->{select("대화");c.draft(prompt);});sideBody.addView(row,Ui.match(a,-2,10));View line=new View(a);line.setBackgroundColor(0xffeeeeee);sideBody.addView(line,new LinearLayout.LayoutParams(-1,dp(1)));}
 void buildSidebar(){LinearLayout brand=new LinearLayout(a);brand.setGravity(Gravity.CENTER_VERTICAL);brand.addView(text("누비",23,true),new LinearLayout.LayoutParams(0,dp(60),1));brand.addView(button("⌕",this::searchConversations),new LinearLayout.LayoutParams(dp(46),dp(46)));sidebar.addView(brand);String[] labels={"기본 채팅","목적별 누비","둘러보기","보관함","나의 누비"},pages={"대화","목적","탐색","작업","내 정보"},icons={"chat","person","compass","tray","person"};for(int i=0;i<labels.length;i++){String next=pages[i];LinearLayout row=new LinearLayout(a);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(10),0,dp(10),0);row.setTag(next);row.addView(new Glyph(a,icons[i],false),new LinearLayout.LayoutParams(dp(28),dp(28)));TextView label=text(labels[i],16,true);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,-2);lp.leftMargin=dp(12);row.addView(label,lp);row.setContentDescription(labels[i]);row.setOnClickListener(v->select(next));sidebar.addView(row,Ui.match(a,48,0));}View line=new View(a);line.setBackgroundColor(0xffeeeeee);sidebar.addView(line,Ui.match(a,1,22));TextView section=text("내 목표별 대화",13,false);section.setTextColor(MUTED);sidebar.addView(section);ScrollView goals=new ScrollView(a);LinearLayout list=c.box(WHITE,0);for(JSONObject goal:a.store.goals()){String title=goal.optString("title");if(title.contains("FIXTURE")||title.startsWith("INSTRUMENTATION"))continue;TextView item=text(title,14,false);item.setPadding(dp(8),dp(12),dp(8),dp(12));item.setOnClickListener(v->c.switchGoal(goal.optString("id")));list.addView(item);}goals.addView(list);sidebar.addView(goals,new LinearLayout.LayoutParams(-1,0,1));}
 void updateSidebar(){if(sidebar==null)return;for(int n=0;n<sidebar.getChildCount();n++){View v=sidebar.getChildAt(n);if(v.getTag() instanceof String)v.setBackground(pill(v.getTag().equals(page)?0xffeeeeee:WHITE,24,false));}}
 void searchConversations(){EditText query=new EditText(a);query.setHint("대화에서 검색");new AlertDialog.Builder(a).setTitle("대화 검색").setView(query).setPositiveButton("검색",(d,w)->{String key=query.getText().toString().trim();List<String> names=new ArrayList<>(),ids=new ArrayList<>();for(JSONObject goal:a.store.goals())if(goal.optString("title").contains(key)||goal.optString("chatMessages").contains(key)){names.add(goal.optString("title"));ids.add(goal.optString("id"));}if(ids.isEmpty()){a.toast("검색 결과가 없어요.");return;}new AlertDialog.Builder(a).setTitle("검색 결과").setItems(names.toArray(new String[0]),(dialog,n)->c.switchGoal(ids.get(n))).setNegativeButton("닫기",null).show();}).setNegativeButton("취소",null).show();}

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
