package ai.decisionos.aside;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.net.Uri;
import android.os.Bundle;
import android.widget.*;
import java.text.DateFormat;
import java.util.Date;

/** Locally saved user tasks. Changes are explicit user decisions. */
public class TaskActivity extends Activity {
    private Store store; private EditText title; private Spinner type; private LinearLayout list; private TextView status;
    private static final String[] TYPES={"검색·비교","전화 준비","예약 준비","쇼핑 준비","모임 준비"};
    @Override public void onCreate(Bundle saved){super.onCreate(saved);store=new Store(this);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);LinearLayout root=Ui.vertical(this,Ui.BG,22);scroll.addView(root);
        root.addView(Ui.text(this,"내가 맡긴 일",27,Ui.WHITE,true),Ui.match(this,-2,6));
        root.addView(Ui.text(this,"할 일을 기기에 저장하고 검색을 이어가요. 완료는 직접 확인해 표시합니다.",14,Ui.MUTED,false),Ui.match(this,-2,8));
        type=new Spinner(this);type.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,TYPES));type.setBackground(Ui.bg(Ui.PRIMARY,8,this));root.addView(type,Ui.match(this,48,10));
        title=new EditText(this);title.setSingleLine(true);title.setTextColor(Ui.WHITE);title.setHintTextColor(Ui.MUTED);title.setHint("예: 서울 공연 근처 숙소 찾기");title.setBackground(Ui.bg(Ui.PANEL,8,this));title.setPadding(Ui.dp(this,12),0,Ui.dp(this,12),0);root.addView(title,Ui.match(this,52,10));
        Button add=Ui.button(this,"할 일 저장");add.setOnClickListener(v->addTask());root.addView(add,Ui.match(this,48,10));
        status=Ui.text(this,"",13,Ui.MUTED,false);root.addView(status,Ui.match(this,-2,8));
        root.addView(Ui.text(this,"저장된 할 일",19,Ui.WHITE,true),Ui.match(this,-2,15));
        list=Ui.vertical(this,Ui.BG,0);root.addView(list,Ui.match(this,-2,4));setContentView(scroll);render();
    }
    private void addTask(){String t=title.getText().toString().trim();if(t.isEmpty()||t.length()>150){status.setText("할 일은 1~150자로 입력해 주세요.");return;}
        ContentValues v=new ContentValues();v.put("title",t);v.put("kind",TYPES[type.getSelectedItemPosition()]);v.put("state","대기");v.put("updated",System.currentTimeMillis());long id=store.getWritableDatabase().insert("tasks",null,v);if(id<0){status.setText("저장하지 못했어요.");return;}title.setText("");status.setText("기기에 저장했어요.");render();}
    private void render(){list.removeAllViews();try(Cursor c=store.getReadableDatabase().rawQuery("SELECT _id,title,kind,state,updated FROM tasks ORDER BY updated DESC,_id DESC LIMIT 100",null)){
        if(c.getCount()==0){list.addView(Ui.text(this,"아직 저장된 할 일이 없어요.",14,Ui.MUTED,false));return;}
        while(c.moveToNext()){long id=c.getLong(0);String t=c.getString(1),kind=c.getString(2),state=c.getString(3);long time=c.getLong(4);
            Button item=Ui.button(this,kind+" · "+state+"\n"+t);item.setOnClickListener(v->details(id,t,kind,state,time));list.addView(item,Ui.match(this,66,8));}
        }}
    private void details(long id,String t,String kind,String state,long time){String stamp=DateFormat.getDateTimeInstance(DateFormat.SHORT,DateFormat.SHORT).format(new Date(time));
        String[] actions={"관련 정보 검색","진행 중으로 표시","직접 확인 후 완료 표시","삭제"};
        new AlertDialog.Builder(this).setTitle(t).setMessage(kind+" · "+state+"\n마지막 변경: "+stamp+"\n완료 표시는 사용자의 기록이며 실제 예약·주문을 증명하지 않아요.").setItems(actions,(d,which)->{
            if(which==0){Uri uri=Uri.parse("https://www.google.com/search").buildUpon().appendQueryParameter("q",t).build();Intent i=new Intent(this,BrowserWorkspaceActivity.class);i.putExtra("start_url",uri.toString());startActivity(i);}
            else if(which==1)update(id,"진행 중");else if(which==2)new AlertDialog.Builder(this).setTitle("직접 완료를 확인했나요?").setMessage("외부 서비스의 실제 결과는 이 표시와 별개입니다.").setNegativeButton("취소",null).setPositiveButton("완료로 표시",(dialog,w)->update(id,"완료")).show();
            else new AlertDialog.Builder(this).setTitle("이 할 일을 삭제할까요?").setNegativeButton("취소",null).setPositiveButton("삭제",(dialog,w)->{store.getWritableDatabase().delete("tasks","_id=?",new String[]{Long.toString(id)});status.setText("삭제했어요.");render();}).show();
        }).setNegativeButton("닫기",null).show();}
    private void update(long id,String state){ContentValues v=new ContentValues();v.put("state",state);v.put("updated",System.currentTimeMillis());store.getWritableDatabase().update("tasks",v,"_id=?",new String[]{Long.toString(id)});status.setText("상태를 변경했어요.");render();}
    @Override protected void onDestroy(){store.close();super.onDestroy();}
    private static final class Store extends SQLiteOpenHelper {Store(Context c){super(c,"aside_tasks.db",null,1);}public void onCreate(SQLiteDatabase db){db.execSQL("CREATE TABLE tasks (_id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,kind TEXT NOT NULL,state TEXT NOT NULL,updated INTEGER NOT NULL)");}public void onUpgrade(SQLiteDatabase db,int oldV,int newV){}}
}
