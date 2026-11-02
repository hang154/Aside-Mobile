package ai.decisionos.aside;
import android.content.*;import org.json.*;
/** Selection is presentation state, never execution ownership. */
final class NavigationState {
 final android.content.SharedPreferences prefs;String route="대화",returnRoute="대화",libraryGoal="",libraryTab="진행";
 NavigationState(Context c){prefs=c.getSharedPreferences("nubi_navigation_v3",0);libraryGoal=prefs.getString("libraryGoal","");libraryTab=prefs.getString("libraryTab","진행");}
 void select(String goal,String conversation,String agent){prefs.edit().putString("lastGoal",goal).putString("lastConversation",conversation).putString("agent."+agent,conversation).apply();}
 void filter(String goal,String tab){libraryGoal=goal;libraryTab=tab;prefs.edit().putString("libraryGoal",goal).putString("libraryTab",tab).apply();}
 static String title(String route){switch(route){case "탐색":return "둘러보기";case "작업":return "보관함";case "내 정보":return "나의 누비";case "브라우저":case "웹 브라우저":return "탐색 화면";default:return route;}}
 static boolean global(String route){return java.util.Arrays.asList("친구","탐색","작업","내 정보","연결·기기 설정","내 프로필","수집 설정","관심 앱","로컬 모델","로컬 제안").contains(route);}
}
