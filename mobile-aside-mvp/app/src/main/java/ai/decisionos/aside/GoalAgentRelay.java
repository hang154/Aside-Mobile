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
final class GoalAgentRelay {
    interface Status { void show(String text); }
    interface Reply { void send(JSONObject data); }
    interface Commands { void run(JSONObject command,Reply reply)throws Exception; }
    private final Activity activity; private final Commands commands; private final Status status;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private static String sessionPairing;
    private volatile boolean active; private volatile long generation; private String endpoint,token,pin,deviceSession; private SSLSocketFactory sockets;
    GoalAgentRelay(Activity activity,Commands commands,Status status){this.activity=activity;this.commands=commands;this.status=status;}
    void connect(String value) throws Exception {
        String[] parts=value.trim().split("\\|",-1); if(parts.length!=3)throw new IllegalArgumentException("주소|연결키|인증서 지문 형식이 필요해요");
        Uri uri=Uri.parse(parts[0]);if(!"https".equals(uri.getScheme())||uri.getHost()==null||uri.getUserInfo()!=null||uri.getQuery()!=null||uri.getFragment()!=null||!(uri.getPath()==null||uri.getPath().isEmpty()))throw new IllegalArgumentException("HTTPS 서버 주소를 확인해 주세요");
        if(parts[1].length()<32||!parts[1].matches("[A-Za-z0-9_-]+")||!parts[2].matches("(?i)[0-9a-f]{64}"))throw new IllegalArgumentException("연결키 또는 인증서 지문을 확인해 주세요");
        stop();deviceSession=java.util.UUID.randomUUID().toString();sessionPairing=value;endpoint=parts[0].replaceAll("/$","");token=parts[1];pin=parts[2].toLowerCase();
        TrustManager[] trust={new X509TrustManager(){public X509Certificate[] getAcceptedIssuers(){return new X509Certificate[0];} public void checkClientTrusted(X509Certificate[] c,String a) throws java.security.cert.CertificateException {throw new java.security.cert.CertificateException("client certificate not supported");} public void checkServerTrusted(X509Certificate[] c,String a) throws java.security.cert.CertificateException {try{if(c==null||c.length==0)throw new Exception(); byte[] hash=MessageDigest.getInstance("SHA-256").digest(c[0].getEncoded());StringBuilder h=new StringBuilder();for(byte b:hash)h.append(String.format(java.util.Locale.ROOT,"%02x",b&255));if(!MessageDigest.isEqual(h.toString().getBytes(StandardCharsets.US_ASCII),pin.getBytes(StandardCharsets.US_ASCII)))throw new Exception();c[0].checkValidity();}catch(Exception e){throw new java.security.cert.CertificateException("Server certificate pin mismatch",e);}}}};
        SSLContext context=SSLContext.getInstance("TLS");context.init(null,trust,null);sockets=context.getSocketFactory();GoalAgentPairing.save(activity,value);active=true;long current=++generation;status.show("원격 연결 중 · 목표별 공개 탐색만 허용");new Thread(()->loop(current),"nubi-goal-relay").start();
    }
    boolean connected(){return active;}
    boolean restore()throws Exception{if(sessionPairing==null)sessionPairing=GoalAgentPairing.load(activity);if(sessionPairing==null)return false;connect(sessionPairing);return true;}
    void forget(){stop();sessionPairing=null;GoalAgentPairing.clear(activity);}
    interface Response {void receive(JSONObject data);}
    void chat(String path,JSONObject payload,Response response){
        if(!path.equals("/chat-submit")&&!path.equals("/chat-status")&&!path.equals("/chat-cancel"))throw new IllegalArgumentException();
        new Thread(()->{JSONObject out;try{out=post(path,payload);}catch(Exception e){out=new JSONObject();GoalStore.put(out,"error","연결을 확인하고 다시 시도해줘. ("+e.getClass().getSimpleName()+")");}final JSONObject answer=out;ui.post(()->response.receive(answer));},"nubi-chat-request").start();
    }
    void stop(){active=false;generation++;}
    private JSONObject post(String path,JSONObject payload) throws Exception{
        if(path.equals("/poll")||path.equals("/chat-submit"))payload.put("device_session",deviceSession);
        HttpsURLConnection c=(HttpsURLConnection)new URL(endpoint+path).openConnection();c.setSSLSocketFactory(sockets);c.setHostnameVerifier((host,session)->true);c.setInstanceFollowRedirects(false);c.setConnectTimeout(7000);c.setReadTimeout(22000);c.setRequestMethod("POST");c.setDoOutput(true);c.setRequestProperty("Authorization","Bearer "+token);c.setRequestProperty("Content-Type","application/json");byte[] out=payload.toString().getBytes(StandardCharsets.UTF_8);c.setFixedLengthStreamingMode(out.length);try(OutputStream o=c.getOutputStream()){o.write(out);}if(c.getResponseCode()!=200)throw new IOException("relay HTTP "+c.getResponseCode());ByteArrayOutputStream data=new ByteArrayOutputStream();try(InputStream in=c.getInputStream()){byte[] buf=new byte[4096];int n;while((n=in.read(buf))!=-1){data.write(buf,0,n);if(data.size()>32768)throw new IOException("response too large");}}finally{c.disconnect();}return new JSONObject(data.toString("UTF-8"));
    }
    private void loop(long current){try{while(active&&generation==current){JSONObject cmd=post("/poll",new JSONObject()).optJSONObject("command");if(!active||generation!=current)break;if(cmd==null)continue;JSONObject result=execute(cmd);if(active&&generation==current)post("/result",result);}}catch(Exception e){if(active&&generation==current)ui.post(()->status.show("원격 연결 종료: "+e.getClass().getSimpleName()));}finally{if(generation==current)active=false;}}
    private JSONObject execute(JSONObject cmd)throws Exception{
        JSONObject out=new JSONObject();String id=cmd.optString("id");out.put("id",id);if(!id.matches("[0-9a-f]{24}")||cmd.optLong("expires")*1000<System.currentTimeMillis()){out.put("error","invalid or expired command");return out;}
        final long expected=generation;CountDownLatch latch=new CountDownLatch(1);JSONObject[] answer={null};ui.post(()->{if(!active||generation!=expected){latch.countDown();return;}try{commands.run(cmd,result->{if(active&&generation==expected)answer[0]=result;latch.countDown();});}catch(Exception e){answer[0]=new JSONObject();GoalStore.put(answer[0],"error",e.getClass().getSimpleName()+": "+e.getMessage());latch.countDown();}});
        if(!latch.await(12,TimeUnit.SECONDS)||answer[0]==null){out.put("error","foreground command timed out or disconnected");return out;}java.util.Iterator<String> keys=answer[0].keys();while(keys.hasNext()){String key=keys.next();out.put(key,answer[0].get(key));}return out;
    }
}
