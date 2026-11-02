package ai.decisionos.aside;
import android.view.*;import android.widget.*;import org.json.*;
/** Reusable action rows: one primary action, explicit scope and honest status. */
final class CompanionCards {
 static LinearLayout row(NubiCompanionUi ui,String title,String detail,String action,Runnable click){
  LinearLayout box=ui.c.box(NubiCompanionUi.PANEL,16);box.setBackground(ui.pill(NubiCompanionUi.PANEL,20,false));
  LinearLayout line=new LinearLayout(ui.a);line.setGravity(Gravity.CENTER_VERTICAL);LinearLayout copy=ui.c.box(NubiCompanionUi.PANEL,0);
  TextView heading=ui.text(title,16,true);heading.setMaxLines(2);heading.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(heading);
  if(!detail.isEmpty()){TextView note=ui.text(detail,13,false);note.setTextColor(NubiCompanionUi.MUTED);copy.addView(note,Ui.match(ui.a,-2,6));}
  line.addView(copy,new LinearLayout.LayoutParams(0,-2,1));
  if(click!=null){TextView button=ui.button("›",click);button.setTextSize(26);button.setTextColor(NubiCompanionUi.MUTED);button.setPadding(0,0,0,0);button.setBackgroundColor(android.graphics.Color.TRANSPARENT);button.setContentDescription(title+" · "+action);line.addView(button,new LinearLayout.LayoutParams(ui.dp(44),ui.dp(48)));box.setOnClickListener(v->click.run());box.setContentDescription(title+" · "+action);}
  box.addView(line);ui.sideBody.addView(box,Ui.match(ui.a,-2,12));return box;
 }

 static String state(String state){switch(state){case "RUNNING":case "running":return "탐색 중";case "QUEUED":return "전달 중";case "STOP_REQUESTED":return "중지 확인 중";case "STOPPED":case "cancelled":return "중지 확인됨";case "SUCCEEDED":case "completed":return "응답 완료 · 결과 확인";case "OUTCOME_UNKNOWN":return "결과 확인 필요";case "WAITING_USER":return "사용자 확인 필요";case "FAILED":case "failed":return "실행 실패";default:return "이전 실행 기록";}}
 static String documentState(JSONObject doc){return "uploaded".equals(doc.optString("state"))?"서버 보고: 업로드됨 · 제출 근거는 답변 확인":"문서 생성 · 자동 제출 미확인";}
}
