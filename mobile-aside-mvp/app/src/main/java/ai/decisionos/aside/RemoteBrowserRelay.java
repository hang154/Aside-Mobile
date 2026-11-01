package ai.decisionos.aside;

import android.app.Activity;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.webkit.WebView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import javax.net.ssl.*;

/** Foreground proof of concept: explicit pairing, pinned TLS, bounded read-only commands. */
final class RemoteBrowserRelay {
    interface Status { void show(String text); }
    private final Activity activity; private final WebView web; private final Status status;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private volatile boolean active; private volatile long generation; private String endpoint,token,pin; private SSLSocketFactory sockets;
    RemoteBrowserRelay(Activity activity, WebView web, Status status){this.activity=activity;this.web=web;this.status=status;}
    void connect(String value) throws Exception {
        String[] parts=value.trim().split("\\|",-1); if(parts.length!=3)throw new IllegalArgumentException("주소|연결키|인증서 지문 형식이 필요해요");
        Uri uri=Uri.parse(parts[0]);if(!"https".equals(uri.getScheme())||uri.getHost()==null||uri.getUserInfo()!=null||uri.getQuery()!=null||uri.getFragment()!=null||!(uri.getPath()==null||uri.getPath().isEmpty()))throw new IllegalArgumentException("HTTPS 서버 주소를 확인해 주세요");
        if(parts[1].length()<32||!parts[1].matches("[A-Za-z0-9_-]+")||!parts[2].matches("(?i)[0-9a-f]{64}"))throw new IllegalArgumentException("연결키 또는 인증서 지문을 확인해 주세요");
        stop();endpoint=parts[0].replaceAll("/$","");token=parts[1];pin=parts[2].toLowerCase();
        TrustManager[] trust={new X509TrustManager(){public X509Certificate[] getAcceptedIssuers(){return new X509Certificate[0];} public void checkClientTrusted(X509Certificate[] c,String a) throws java.security.cert.CertificateException {throw new java.security.cert.CertificateException("client certificate not supported");} public void checkServerTrusted(X509Certificate[] c,String a) throws java.security.cert.CertificateException {try{if(c==null||c.length==0)throw new Exception(); byte[] hash=MessageDigest.getInstance("SHA-256").digest(c[0].getEncoded());StringBuilder h=new StringBuilder();for(byte b:hash)h.append(String.format(java.util.Locale.ROOT,"%02x",b&255));if(!MessageDigest.isEqual(h.toString().getBytes(StandardCharsets.US_ASCII),pin.getBytes(StandardCharsets.US_ASCII)))throw new Exception();c[0].checkValidity();}catch(Exception e){throw new java.security.cert.CertificateException("Server certificate pin mismatch",e);}}}};
        SSLContext context=SSLContext.getInstance("TLS");context.init(null,trust,null);sockets=context.getSocketFactory();active=true;long current=++generation;status.show("원격 연결 중 · 공개 위키 조회만 허용");new Thread(()->loop(current),"nubi-relay").start();
    }
    void stop(){active=false;generation++;}
    private JSONObject post(String path,JSONObject payload) throws Exception{
        HttpsURLConnection c=(HttpsURLConnection)new URL(endpoint+path).openConnection();c.setSSLSocketFactory(sockets);c.setHostnameVerifier((host,session)->true);c.setInstanceFollowRedirects(false);c.setConnectTimeout(7000);c.setReadTimeout(22000);c.setRequestMethod("POST");c.setDoOutput(true);c.setRequestProperty("Authorization","Bearer "+token);c.setRequestProperty("Content-Type","application/json");byte[] out=payload.toString().getBytes(StandardCharsets.UTF_8);c.setFixedLengthStreamingMode(out.length);try(OutputStream o=c.getOutputStream()){o.write(out);}if(c.getResponseCode()!=200)throw new IOException("relay HTTP "+c.getResponseCode());ByteArrayOutputStream data=new ByteArrayOutputStream();try(InputStream in=c.getInputStream()){byte[] buf=new byte[4096];int n;while((n=in.read(buf))!=-1){data.write(buf,0,n);if(data.size()>32768)throw new IOException("response too large");}}finally{c.disconnect();}return new JSONObject(data.toString("UTF-8"));
    }
    private void loop(long current){try{while(active&&generation==current){JSONObject cmd=post("/poll",new JSONObject()).optJSONObject("command");if(!active||generation!=current)break;if(cmd==null)continue;JSONObject result=execute(cmd);if(active&&generation==current)post("/result",result);}}catch(Exception e){if(active&&generation==current)ui.post(()->status.show("원격 연결 종료: "+e.getClass().getSimpleName()));}finally{if(generation==current)active=false;}}
    private static boolean allowed(String s){try{Uri u=Uri.parse(s);return "https".equals(u.getScheme())&&"en.wikipedia.org".equalsIgnoreCase(u.getHost())&&u.getPort()==-1&&u.getUserInfo()==null&&u.getQuery()==null&&u.getFragment()==null&&u.getPath()!=null&&u.getPath().startsWith("/wiki/")&&!u.getPath().contains(":");}catch(Exception e){return false;}}
    private static boolean observable(String s){if(allowed(s))return true;try{Uri u=Uri.parse(s);return "https".equals(u.getScheme())&&"en.wikipedia.org".equalsIgnoreCase(u.getHost())&&u.getPort()==-1&&u.getUserInfo()==null&&"/w/index.php".equals(u.getPath())&&u.getQueryParameter("search")!=null&&u.getFragment()==null;}catch(Exception e){return false;}}
    private JSONObject execute(JSONObject cmd) throws Exception{
        String id=cmd.optString("id"),op=cmd.optString("op");JSONObject out=new JSONObject();out.put("id",id);out.put("op",op);if(!id.matches("[0-9a-f]{24}")){out.put("error","invalid command id");return out;}
        if("search".equals(op)){String query=cmd.optString("query").trim();if(query.isEmpty()||query.length()>100){out.put("error","invalid query");return out;}String url=new Uri.Builder().scheme("https").authority("en.wikipedia.org").path("/w/index.php").appendQueryParameter("search",query).build().toString();CountDownLatch latch=new CountDownLatch(1);ui.post(()->{if(active){web.loadUrl(url);status.show("원격 검색 · 위키백과");}latch.countDown();});if(!latch.await(5,TimeUnit.SECONDS)){out.put("error","UI timeout");return out;}out.put("state","search_requested");return out;}
        if("navigate".equals(op)){String url=cmd.optString("url");if(!allowed(url)){out.put("error","URL not allowed");return out;}CountDownLatch latch=new CountDownLatch(1);ui.post(()->{if(active){web.loadUrl(url);status.show("원격 웹 열기 · 위키백과");}latch.countDown();});if(!latch.await(5,TimeUnit.SECONDS)){out.put("error","UI timeout");return out;}out.put("state","navigation_requested");return out;}
        if(!"observe".equals(op)){out.put("error","unsupported action");return out;}
        CountDownLatch latch=new CountDownLatch(1);String[] answer={null};ui.post(()->{if(!active||!observable(web.getUrl())){latch.countDown();return;}String script="(()=>JSON.stringify({url:location.origin+location.pathname+location.search,title:document.title,text:(document.querySelector('main')?.innerText||'').slice(0,1000),links:Array.from(document.querySelectorAll('main a[href^=\"/wiki/\"]')).slice(0,8).map(a=>({title:(a.innerText||'').slice(0,80),path:a.getAttribute('href')}))}))()";web.evaluateJavascript(script,v->{answer[0]=v;latch.countDown();});});
        if(!latch.await(8,TimeUnit.SECONDS)||answer[0]==null){out.put("error","no allowed page or UI timeout");return out;}
        String json=new JSONArray("["+answer[0]+"]").getString(0);JSONObject page=new JSONObject(json);if(!observable(page.optString("url"))){out.put("error","page redirected outside allowlist");return out;}out.put("state","observed");out.put("page",page);return out;
    }
}
