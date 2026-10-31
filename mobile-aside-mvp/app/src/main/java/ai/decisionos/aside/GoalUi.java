package ai.decisionos.aside;
import android.app.*;import android.content.*;import android.graphics.*;import android.view.*;import android.widget.*;
/** Original native character art and shared adaptive page frame. */
public abstract class GoalUi extends Activity {
 static final int BG=0xfff7f5f1,INK=0xff29293b,MUTED=0xff747584,PURPLE=0xff7568ba;
 LinearLayout shell,body,root; ScrollView scroll;
 void frame(String title,String caption){getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);root=Ui.vertical(this,BG,0);shell=new LinearLayout(this);boolean wide=getResources().getConfiguration().screenWidthDp>=600;
  if(wide){LinearLayout rail=Ui.vertical(this,0xffeeebf3,12);rail.addView(txt("nubi",24,PURPLE,true));for(String t:new String[]{"홈","쇼핑·전문가","내 활동","프로필"}){Button b=button(t,false);b.setOnClickListener(v->nav(t));rail.addView(b,Ui.match(this,56,16));}shell.addView(rail,new LinearLayout.LayoutParams(Ui.dp(this,126),-1));}
  scroll=new ScrollView(this);scroll.setId(0x401);scroll.setFillViewport(true);body=Ui.vertical(this,BG,wide?28:20);body.addView(txt(title,30,INK,true));if(!caption.isEmpty())body.addView(txt(caption,14,MUTED,false),Ui.match(this,-2,8));scroll.addView(body,new android.widget.FrameLayout.LayoutParams(wide?Ui.dp(this,Math.min(900,getResources().getConfiguration().screenWidthDp-126)):-1,-2,Gravity.CENTER_HORIZONTAL));shell.addView(scroll,new LinearLayout.LayoutParams(0,-1,1));root.addView(shell,new LinearLayout.LayoutParams(-1,0,1));
  if(!wide){LinearLayout bar=new LinearLayout(this);for(String t:new String[]{"홈","쇼핑·전문가","내 활동","프로필"}){Button b=button(t,false);b.setTextSize(11);b.setOnClickListener(v->nav(t));bar.addView(b,new LinearLayout.LayoutParams(0,Ui.dp(this,56),1));}root.addView(bar);}setContentView(root);
 }
 void nav(String t){Intent i=new Intent(this,CampusActivity.class);i.putExtra("section",t);if(t.equals("홈"))i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);startActivity(i);}
 TextView txt(String s,int n,int color,boolean bold){return Ui.text(this,s,n,color,bold);}
 void note(LinearLayout p,String text){p.addView(txt(text,13,MUTED,false),Ui.match(this,-2,8));}
 LinearLayout card(){LinearLayout p=Ui.vertical(this,Color.WHITE,18);p.setBackground(Ui.bg(Color.WHITE,20,this));body.addView(p,Ui.match(this,-2,14));return p;}
 Button button(String t,boolean fill){Button b=new Button(this);b.setAllCaps(false);b.setText(t);b.setTextSize(14);b.setTextColor(fill?Color.WHITE:PURPLE);b.setBackground(Ui.bg(fill?PURPLE:0xffefedf7,13,this));b.setPadding(Ui.dp(this,10),Ui.dp(this,7),Ui.dp(this,10),Ui.dp(this,7));return b;}
 void action(LinearLayout p,String text,Runnable fn){Button b=button(text,false);b.setOnClickListener(v->fn.run());p.addView(b,Ui.match(this,-2,8));}
 EditText edit(LinearLayout p,String hint,String value){EditText e=new EditText(this);e.setSingleLine();e.setTextSize(15);e.setTextColor(INK);e.setHintTextColor(MUTED);e.setHint(hint);e.setText(value);e.setBackground(Ui.bg(BG,10,this));e.setPadding(14,8,14,8);p.addView(e,Ui.match(this,52,8));return e;}
 void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}
 void open(String url){if(!GoalRules.safe(url)){toast("연결을 지원하는 HTTPS 출처만 열 수 있어요.");return;}Intent i=new Intent(this,BrowserWorkspaceActivity.class);i.putExtra("start_url",url);startActivity(i);}
 static final class Buddy extends View {
  final Paint p=new Paint(3);final int color; final String label;
  Buddy(Context c,int color,String label){super(c);this.color=color;this.label=label;setContentDescription(label+" 누비 캐릭터");}
  protected void onDraw(Canvas c){super.onDraw(c);float x=getWidth()/2f,y=getHeight()/2f,r=Math.min(getWidth(),getHeight())*.34f;p.setColor(color);c.drawOval(x-r,y-r*.8f,x+r,y+r,p);c.drawCircle(x-r*.65f,y-r*.65f,r*.37f,p);c.drawCircle(x+r*.65f,y-r*.65f,r*.37f,p);p.setColor(0xff29293b);c.drawCircle(x-r*.34f,y-r*.05f,r*.065f,p);c.drawCircle(x+r*.34f,y-r*.05f,r*.065f,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(r*.045f);c.drawArc(x-r*.18f,y+r*.12f,x+r*.18f,y+r*.37f,10,160,false,p);p.setStyle(Paint.Style.FILL);p.setColor(0x66ffffff);c.drawOval(x-r*.68f,y+r*.16f,x-r*.3f,y+r*.34f,p);c.drawOval(x+r*.3f,y+r*.16f,x+r*.68f,y+r*.34f,p);}
 }
 void hero(LinearLayout p,GoalRules.Preset a,String title){LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);row.addView(new Buddy(this,a.color,a.name),new LinearLayout.LayoutParams(Ui.dp(this,100),Ui.dp(this,100)));LinearLayout text=Ui.vertical(this,Color.TRANSPARENT,10);text.addView(txt(a.name+" · "+a.emoji,16,a.color,true));text.addView(txt(title,24,INK,true));row.addView(text,new LinearLayout.LayoutParams(0,-2,1));p.addView(row);}
}
