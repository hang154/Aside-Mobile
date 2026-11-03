package ai.decisionos.aside;

import android.os.SystemClock;
import android.webkit.WebView;
import android.widget.Toast;
import org.json.JSONObject;

/** Native polling only: no page-callable bridge, disk plaintext, or relay response. */
final class PortalCredentialCapture implements Runnable {
 private static final java.util.WeakHashMap<WebView,PortalCredentialCapture> CAPTURES=new java.util.WeakHashMap<>();
 private final java.lang.ref.WeakReference<WebView> ref;
 private String account,secret; private long expires; private boolean busy; private String filledDocument=""; private boolean schoolFlow; private String schoolHint="",filledMsDocument="";
 private static final String PROBE="(()=>{if(location.origin!=='https://portal.unist.ac.kr')return '{}';const visible=e=>!!(e.getClientRects().length)&&!e.disabled;const pw=[...document.querySelectorAll('input[type=password]')].filter(visible);if(!pw.length){const ok=[...document.querySelectorAll('a,button,input[type=button],input[type=submit]')].some(e=>visible(e)&&/^(로그아웃|log\\s*out|sign\\s*out)$/i.test((e.innerText||e.value||'').trim()));return JSON.stringify({ok});}if(pw.length!==1)return '{}';const p=pw[0],f=p.form;if(!f||new URL(f.action||location.href,location.href).origin!==location.origin)return '{}';const users=[...f.querySelectorAll('input')].filter(e=>visible(e)&&/^(text|email)$/.test(e.type)&&/user|uid|login|account|id/i.test(e.name+' '+e.id)&&!/otp|token|code|인증/i.test(e.name+' '+e.id));if(users.length!==1||/otp|token|code|one.time/i.test(p.name+' '+p.id+' '+p.autocomplete))return '{}';return JSON.stringify({account:users[0].value,secret:p.value});})()";
 private static final String MS_PROBE="(()=>{if(location.origin!=='https://login.microsoftonline.com')return '{}';const visible=e=>!!e.getClientRects().length&&!e.disabled;const identity=[document.querySelector('#i0116')?.value,document.querySelector('#displayName')?.textContent,document.querySelector('.identity')?.textContent].filter(Boolean).map(x=>x.trim()).find(x=>/@/.test(x))||'';const p=[...document.querySelectorAll('input[type=password]')].filter(visible);const secret=p.length===1&&!/otp|token|code|one.time/i.test(p[0].name+' '+p[0].id+' '+p[0].autocomplete)?p[0].value:'';return JSON.stringify({account:identity,secret});})()";
 static boolean schoolIdentity(String value){return value!=null&&value.matches("(?i)[a-z0-9._%+-]+@unist[.]ac[.]kr");}
 static void attach(WebView web){PortalCredentialCapture c=new PortalCredentialCapture(web);CAPTURES.put(web,c);web.postDelayed(c,200);}
 static void authorizeSchool(WebView web){PortalCredentialCapture c=CAPTURES.get(web);if(c!=null)c.schoolFlow=true;}
 PortalCredentialCapture(WebView web){ref=new java.lang.ref.WeakReference<>(web);}
 private void clear(){account=null;secret=null;expires=0;}
 void expire(long now){if(expires!=0&&now>expires)clear();}
 boolean pending(){return account!=null&&secret!=null;}
 static boolean trustedContinuation(String url){return SchoolSignIn.allowed(url);}
 // The caller supplies only locally evaluated metadata; never return credentials to a page.
 boolean accept(JSONObject value,long now){
  if(now>expires&&expires!=0)clear();
  if(value.optBoolean("ok")&&account!=null&&secret!=null)return true;
  String a=value.optString("account"),s=value.optString("secret");
  if(!a.isEmpty()&&!s.isEmpty()&&a.length()<512&&s.length()<4096){account=a;secret=s;expires=now+300000;}
  else if(value.has("account"))clear();
  return false;
 }
 public void run(){WebView web=ref.get();if(web==null)return;
  expire(SystemClock.elapsedRealtime());
  if(!web.isAttachedToWindow()){web.postDelayed(this,500);return;}
  if(!web.hasWindowFocus()||!web.isShown()){web.postDelayed(this,500);return;}
  String url=web.getUrl();
  if(CredentialVaultActivity.portalOrigin(url)||"blackboard.unist.ac.kr".equals(android.net.Uri.parse(url==null?"":url).getHost()))schoolFlow=true;
  if(!CredentialVaultActivity.portalOrigin(url)){
   if(!trustedContinuation(url)){clear();schoolFlow=false;schoolHint="";filledMsDocument="";filledDocument="";web.postDelayed(this,500);return;}
   filledDocument="";
   if(schoolFlow&&"login.microsoftonline.com".equals(android.net.Uri.parse(url).getHost())&&!busy){
    busy=true;final String observed=url;web.evaluateJavascript(MS_PROBE,raw->{busy=false;if(!observed.equals(web.getUrl())||!web.hasWindowFocus())return;
     try{JSONObject value=new JSONObject(String.valueOf(new org.json.JSONTokener(raw).nextValue()));String identity=value.optString("account");if(schoolIdentity(identity))schoolHint=identity;else if(!identity.isEmpty()){schoolHint="";clear();return;}
      if(schoolIdentity(identity)&&!value.optString("secret").isEmpty())accept(new JSONObject().put("account",schoolHint).put("secret",value.getString("secret")),SystemClock.elapsedRealtime());
      else if(value.optString("secret").isEmpty())fillSavedMicrosoft(web,observed);
     }catch(Exception ignored){}
    });web.postDelayed(this,200);return;
   }
   if(pending()&&!busy){busy=true;final String observed=url;
    web.evaluateJavascript("(()=>{const visible=e=>!!e.getClientRects().length;const auth=[...document.querySelectorAll('input[type=password],input[type=email]')].some(visible);const h=location.hostname;const bb=h==='blackboard.unist.ac.kr'&&!!document.querySelector('a[href*=\"/ultra/courses/\"]');const mail=/^(outlook[.]office[.]com|outlook[.]office365[.]com|outlook[.]cloud[.]microsoft)$/.test(h)&&[...document.querySelectorAll('button,[role=button]')].some(e=>visible(e)&&/^(New mail|새 메일 작성)$/i.test((e.innerText||e.getAttribute('aria-label')||'').trim()));return JSON.stringify({ok:!auth&&(bb||mail)})})()",raw->{busy=false;if(!observed.equals(web.getUrl())||!trustedContinuation(web.getUrl()))return;try{JSONObject value=new JSONObject(String.valueOf(new org.json.JSONTokener(raw).nextValue()));if(accept(value,SystemClock.elapsedRealtime()))commit(web);}catch(Exception ignored){}});
   }
   web.postDelayed(this,250);return;
  }
  if(!busy){busy=true;final String observed=url;web.evaluateJavascript(PROBE,result->{busy=false;
   if(!web.hasWindowFocus()||!CredentialVaultActivity.portalOrigin(web.getUrl())||!observed.equals(web.getUrl()))return;
   try{Object decoded=new org.json.JSONTokener(result).nextValue();JSONObject value=new JSONObject(String.valueOf(decoded));
    if(accept(value,SystemClock.elapsedRealtime())){
     commit(web);
    }
    else if(!pending()&&!value.optString("secret").isEmpty()){} // Never replace user input.
    else if(!pending()&&value.has("account")&&value.optString("account").isEmpty())fillSaved(web,observed);
   }catch(Exception ignored){/* No credential values or evaluator output in logs. */}
  });}
  web.postDelayed(this,200);
 }
 private void commit(WebView web)throws Exception{
  new NativeCredentialVault(web.getContext()).save("school",new JSONObject().put("account",account).put("secret",secret));
  clear();WebSessionPolicy.checkpoint();Toast.makeText(web.getContext(),"학교 로그인 정보를 암호화해 저장했어요",Toast.LENGTH_SHORT).show();
 }
 private void fillSavedMicrosoft(WebView web,String observed){
  String key=observed+"|"+schoolHint;if(key.equals(filledMsDocument)||!schoolFlow)return;
  try{JSONObject j=new NativeCredentialVault(web.getContext()).load("school");if(j==null||!schoolIdentity(j.optString("account")))return;
   String code="(()=>{if(location.origin!=='https://login.microsoftonline.com')return false;const account="+JSONObject.quote(j.getString("account"))+",secret="+JSONObject.quote(j.getString("secret"))+";const visible=e=>!!e?.getClientRects().length&&!e.disabled;const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;const emit=e=>{e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));};const email=document.querySelector('#i0116');if(visible(email)&&!email.value){set.call(email,account);emit(email);return true;}const identity=(document.querySelector('#displayName')?.textContent||document.querySelector('.identity')?.textContent||'').trim();const p=[...document.querySelectorAll('input[type=password]')].filter(visible);if(identity.toLowerCase()!==account.toLowerCase()||p.length!==1||p[0].value||/otp|token|code|one.time/i.test(p[0].name+' '+p[0].id+' '+p[0].autocomplete))return false;set.call(p[0],secret);emit(p[0]);return true})()";
   web.evaluateJavascript(code,r->{if("true".equals(r))filledMsDocument=key;});
  }catch(Exception ignored){}
 }
 private void fillSaved(WebView web,String observed){
  if(observed.equals(filledDocument)||!CredentialVaultActivity.portalOrigin(web.getUrl()))return;
  try{JSONObject j=new NativeCredentialVault(web.getContext()).load("school");if(j==null)return;
   String code="(()=>{if(location.origin!=='https://portal.unist.ac.kr')return false;const visible=e=>!!e.getClientRects().length&&!e.disabled;const p=[...document.querySelectorAll('input[type=password]')].filter(visible);if(p.length!==1||p[0].value||/otp|token|code|one.time/i.test(p[0].name+' '+p[0].id+' '+p[0].autocomplete))return false;const f=p[0].form;if(!f||new URL(f.action||location.href,location.href).origin!==location.origin)return false;const u=[...f.querySelectorAll('input')].filter(e=>visible(e)&&/^(text|email)$/.test(e.type)&&/user|uid|login|account|id/i.test(e.name+' '+e.id));if(u.length!==1||u[0].value)return false;const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;set.call(u[0],"+JSONObject.quote(j.getString("account"))+");set.call(p[0],"+JSONObject.quote(j.getString("secret"))+");for(const e of [u[0],p[0]]){e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));}return true})()";
   filledDocument=observed;web.evaluateJavascript(code,r->{});
  }catch(Exception ignored){}
 }

}
