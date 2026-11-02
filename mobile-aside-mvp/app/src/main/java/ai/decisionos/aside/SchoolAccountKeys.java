package ai.decisionos.aside;
import android.content.Context;
import android.security.keystore.*;
import android.util.Base64;
import java.nio.charset.StandardCharsets;
import java.security.*;
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;
import org.json.JSONObject;
/** Native-only account credential vault. No WebView JavascriptInterface or model access. */
final class SchoolAccountKeys {
 private static final String PREFIX="nubi-school-account-v1-";
 private static String account(String subject)throws Exception{
  if(subject==null||subject.trim().isEmpty()||subject.length()>320)throw new IllegalArgumentException("School account identity required");
  byte[] digest=MessageDigest.getInstance("SHA-256").digest(subject.trim().toLowerCase(java.util.Locale.ROOT).getBytes(StandardCharsets.UTF_8));
  StringBuilder s=new StringBuilder();for(byte b:digest)s.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return s.toString();
 }
 private static String scope(String service){if(!java.util.Arrays.asList("portal","blackboard","mail").contains(service))throw new IllegalArgumentException("Unknown school service");return service;}
 private static SecretKey key(String id,boolean create)throws Exception{
  KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);String alias=PREFIX+id;
  if(ks.containsAlias(alias))return ((KeyStore.SecretKeyEntry)ks.getEntry(alias,null)).getSecretKey();
  if(!create)throw new java.io.IOException("Account key unavailable; sign in again");
  KeyGenerator gen=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
  gen.init(new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());return gen.generateKey();
 }
 static synchronized void save(Context c,String subject,String service,JSONObject grant)throws Exception{
  String id=account(subject),slot=scope(service);byte[] plain=grant.toString().getBytes(StandardCharsets.UTF_8);
  if(plain.length>65536)throw new IllegalArgumentException("Account grant too large");
  Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key(id,true));cipher.updateAAD((id+"|"+slot).getBytes(StandardCharsets.UTF_8));
  String value=Base64.encodeToString(cipher.getIV(),Base64.NO_WRAP)+":"+Base64.encodeToString(cipher.doFinal(plain),Base64.NO_WRAP);
  if(!c.getSharedPreferences("school_account_keys_v1",0).edit().putString(id+"."+slot,value).commit())throw new java.io.IOException("Account grant write failed");
 }
 static synchronized JSONObject load(Context c,String subject,String service)throws Exception{
  String id=account(subject),slot=scope(service),value=c.getSharedPreferences("school_account_keys_v1",0).getString(id+"."+slot,"");if(value.isEmpty())return null;
  String[] parts=value.split(":",2);if(parts.length!=2)throw new java.io.IOException("Invalid account grant");
  Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,key(id,false),new GCMParameterSpec(128,Base64.decode(parts[0],Base64.NO_WRAP)));cipher.updateAAD((id+"|"+slot).getBytes(StandardCharsets.UTF_8));
  return new JSONObject(new String(cipher.doFinal(Base64.decode(parts[1],Base64.NO_WRAP)),StandardCharsets.UTF_8));
 }
 static synchronized void clearAll(Context c)throws Exception{KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);java.util.List<String> aliases=new java.util.ArrayList<>();java.util.Enumeration<String> entries=ks.aliases();while(entries.hasMoreElements()){String alias=entries.nextElement();if(alias.startsWith(PREFIX))aliases.add(alias);}for(String alias:aliases)ks.deleteEntry(alias);if(!c.getSharedPreferences("school_account_keys_v1",0).edit().clear().commit())throw new java.io.IOException("Account vault deletion failed");}
 static synchronized void clear(Context c,String subject)throws Exception{
  String id=account(subject);android.content.SharedPreferences.Editor e=c.getSharedPreferences("school_account_keys_v1",0).edit();for(String s:new String[]{"portal","blackboard","mail"})e.remove(id+"."+s);if(!e.commit())throw new java.io.IOException("Account grant deletion failed");KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);ks.deleteEntry(PREFIX+id);
 }
}
