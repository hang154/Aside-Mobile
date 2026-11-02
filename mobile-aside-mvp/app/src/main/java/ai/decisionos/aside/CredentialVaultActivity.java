package ai.decisionos.aside;

import android.app.*;
import android.content.Intent;
import android.os.Bundle;
import android.text.InputType;
import android.view.*;
import android.widget.*;
import org.json.JSONObject;

/** Device-confirmed native editor. No page, AI, clipboard, logging or network access to secrets. */
public final class CredentialVaultActivity extends Activity {
 private static final int UNLOCK=3811;
 private NativeCredentialVault vault;private EditText account,password;private TextView status;private boolean authorized=false;
 public void onCreate(Bundle state){super.onCreate(state);getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);vault=new NativeCredentialVault(this);locked();}
 private LinearLayout root(){LinearLayout l=new LinearLayout(this);l.setOrientation(1);l.setPadding(48,64,48,32);l.setBackgroundColor(0xfffafbfc);setContentView(l);return l;}
 private void text(LinearLayout l,String s,int size){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setPadding(0,18,0,18);l.addView(t);}
 private void button(LinearLayout l,String s,Runnable action){Button b=new Button(this);b.setFilterTouchesWhenObscured(true);b.setText(s);b.setOnClickListener(v->action.run());l.addView(b,new LinearLayout.LayoutParams(-1,-2));}
 private void clear(){if(account!=null)account.setText("");if(password!=null)password.setText("");account=null;password=null;authorized=false;}
 private void locked(){clear();LinearLayout l=root();text(l,"학교 계정 보관함",24);text(l,"입력한 정보는 이 앱의 기기 키로 암호화해 보관해요. AI와 웹페이지에는 전달하지 않아요. 저장만으로 학교 로그인이 되거나 만료된 세션이 갱신되지는 않아요.",16);text(l,vault.exists("school")?"암호화된 정보가 있어요":"아직 저장한 정보가 없어요",15);button(l,"기기 인증하고 열기",()->{KeyguardManager k=(KeyguardManager)getSystemService(KEYGUARD_SERVICE);if(k==null||!k.isDeviceSecure()){Toast.makeText(this,"먼저 기기 화면 잠금을 설정해 주세요.",Toast.LENGTH_LONG).show();return;}Intent i=k.createConfirmDeviceCredentialIntent("누비 인증정보 보관함","저장된 정보를 열려면 기기 잠금을 인증해 주세요.");if(i==null)return;startActivityForResult(i,UNLOCK);});button(l,"닫기",this::finish);}
 protected void onActivityResult(int req,int result,Intent data){super.onActivityResult(req,result,data);if(req==UNLOCK&&result==RESULT_OK){authorized=true;editor();}else locked();}
 private void editor(){LinearLayout l=root();text(l,"학교 계정 · 기기 내 보관",22);text(l,"포털 비밀번호와 MFA 코드는 달라요. 일회용 인증 코드는 저장하지 마세요.",15);account=new EditText(this);account.setHint("학교 계정");account.setSingleLine(true);account.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);password=new EditText(this);password.setHint("비밀번호 또는 보관할 인증정보");password.setSingleLine(true);password.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);account.setSaveEnabled(false);password.setSaveEnabled(false);account.setFilterTouchesWhenObscured(true);password.setFilterTouchesWhenObscured(true);account.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO);password.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO);l.addView(account);l.addView(password);status=new TextView(this);l.addView(status);
  button(l,"암호화해서 저장",()->{if(!authorized)return;if(account.getText().length()==0||password.getText().length()==0){status.setText("계정과 보관할 정보를 입력해 주세요.");return;}try{vault.save("school",new JSONObject().put("account",account.getText().toString()).put("secret",password.getText().toString()));password.setText("");status.setText("기기 안에 암호화해 저장했어요.");}catch(Exception e){status.setText("저장하지 못했어요. 기기 잠금 상태와 저장 공간을 확인해 주세요.");}});
  button(l,"저장된 정보 불러오기",()->{if(!authorized)return;try{JSONObject j=vault.load("school");if(j==null){status.setText("저장된 정보가 없어요.");return;}account.setText(j.optString("account"));password.setText(j.optString("secret"));status.setText("기기 안에서만 불러왔어요. 비밀번호는 가려져 있어요.");}catch(Exception e){status.setText("복호화할 수 없어요. 손상되었거나 기기 키가 사라졌을 수 있어요. 삭제 후 다시 저장해 주세요.");}});
  button(l,"보관한 정보 삭제",()->new AlertDialog.Builder(this).setTitle("인증정보를 삭제할까요?").setMessage("암호화 파일과 기기 키를 함께 삭제해요. 학교 서비스의 로그인 세션은 별도로 유지돼요.").setNegativeButton("취소",null).setPositiveButton("삭제",(d,w)->{try{vault.delete("school");clear();locked();}catch(Exception e){status.setText("삭제를 완료하지 못했어요.");}}).show());button(l,"잠그기",this::locked);
 }
 protected void onPause(){super.onPause();if(authorized)locked();}
 protected void onSaveInstanceState(Bundle state){super.onSaveInstanceState(state);}
}
