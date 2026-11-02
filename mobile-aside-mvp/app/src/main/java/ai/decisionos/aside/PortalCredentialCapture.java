package ai.decisionos.aside;

import android.os.SystemClock;
import android.webkit.WebView;
import android.widget.Toast;
import org.json.JSONObject;

/** Native polling only: no page-callable bridge, disk plaintext, or relay response. */
final class PortalCredentialCapture implements Runnable {
 private final java.lang.ref.WeakReference<WebView> ref;
 private String account,secret; private long expires; private boolean busy;
 private static final String PROBE="(()=>{if(location.origin!=='https://portal.unist.ac.kr')return '{}';const visible=e=>!!(e.getClientRects().length)&&!e.disabled;const pw=[...document.querySelectorAll('input[type=password]')].filter(visible);if(!pw.length){const ok=[...document.querySelectorAll('a,button,input[type=button],input[type=submit]')].some(e=>visible(e)&&/^(로그아웃|log\\s*out|sign\\s*out)$/i.test((e.innerText||e.value||'').trim()));return JSON.stringify({ok});}if(pw.length!==1)return '{}';const p=pw[0],f=p.form;if(!f||new URL(f.action||location.href,location.href).origin!==location.origin)return '{}';const users=[...f.querySelectorAll('input')].filter(e=>visible(e)&&/^(text|email)$/.test(e.type)&&/user|uid|login|account|id/i.test(e.name+' '+e.id)&&!/otp|token|code|인증/i.test(e.name+' '+e.id));if(users.length!==1||/otp|token|code|one.time/i.test(p.name+' '+p.id+' '+p.autocomplete))return '{}';return JSON.stringify({account:users[0].value,secret:p.value});})()";
 static void attach(WebView web){PortalCredentialCapture c=new PortalCredentialCapture(web);web.postDelayed(c,200);}
 PortalCredentialCapture(WebView web){ref=new java.lang.ref.WeakReference<>(web);}
 private void clear(){account=null;secret=null;expires=0;}
 // The caller supplies only locally evaluated metadata; never return credentials to a page.
 boolean accept(JSONObject value,long now){
  if(now>expires&&expires!=0)clear();
  if(value.optBoolean("ok")&&account!=null&&secret!=null)return true;
  String a=value.optString("account"),s=value.optString("secret");
  if(!a.isEmpty()&&!s.isEmpty()&&a.length()<512&&s.length()<4096){account=a;secret=s;expires=now+120000;}
  else if(value.has("account"))clear();
  return false;
 }
 public void run(){WebView web=ref.get();if(web==null)return;
  if(!web.isAttachedToWindow()){clear();web.postDelayed(this,500);return;}
  if(!web.hasWindowFocus()||!web.isShown()){clear();web.postDelayed(this,500);return;}
  String url=web.getUrl();
  if(!CredentialVaultActivity.portalOrigin(url)){clear();web.postDelayed(this,250);return;}
  if(!busy){busy=true;final String observed=url;web.evaluateJavascript(PROBE,result->{busy=false;
   if(!web.hasWindowFocus()||!CredentialVaultActivity.portalOrigin(web.getUrl())||!observed.equals(web.getUrl()))return;
   try{Object decoded=new org.json.JSONTokener(result).nextValue();JSONObject value=new JSONObject(String.valueOf(decoded));
    if(accept(value,SystemClock.elapsedRealtime())){
     new NativeCredentialVault(web.getContext()).save("school",new JSONObject().put("account",account).put("secret",secret));
     clear();Toast.makeText(web.getContext(),"학교 로그인 정보를 암호화해 저장했어요",Toast.LENGTH_SHORT).show();
    }
   }catch(Exception ignored){/* No credential values or evaluator output in logs. */}
  });}
  web.postDelayed(this,200);
 }
}
