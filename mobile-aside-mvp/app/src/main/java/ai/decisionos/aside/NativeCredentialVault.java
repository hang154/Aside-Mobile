package ai.decisionos.aside;

import android.content.Context;
import android.os.Build;
import android.security.keystore.*;
import android.util.AtomicFile;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.Arrays;
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;

/** Native-only encrypted storage; AndroidKeyStore AES-GCM platform pattern.
 * Reference: https://developer.android.com/privacy-and-security/keystore
 * No JS/MCP API. UI confirmation is separate from the unlocked-device key restriction. */
final class NativeCredentialVault {
 private static final Object LOCK=new Object();
 private static final String PREFIX="nubi-native-vault-v1-";
 private final Context context;
 NativeCredentialVault(Context c){context=c.getApplicationContext();}
 private static void validate(String slot){if(!Arrays.asList("school","test_one","test_two").contains(slot))throw new IllegalArgumentException("Unknown credential slot");}
 private String alias(String slot){validate(slot);return PREFIX+slot;}
 File file(String slot){validate(slot);return new File(context.getNoBackupFilesDir(),"auth-vault-"+slot+".bin");}
 private SecretKey key(String slot,boolean create)throws Exception{
  KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);String alias=alias(slot);
  if(ks.containsAlias(alias))return ((KeyStore.SecretKeyEntry)ks.getEntry(alias,null)).getSecretKey();
  if(!create)throw new IOException("Key unavailable; reconnect account");
  KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
  KeyGenParameterSpec.Builder b=new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setKeySize(256).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).setRandomizedEncryptionRequired(true);
  if(Build.VERSION.SDK_INT>=28)b.setUnlockedDeviceRequired(true);
  generator.init(b.build());return generator.generateKey();
 }
 private byte[] aad(String slot){return (context.getPackageName()+"|vault-v1|"+slot).getBytes(StandardCharsets.UTF_8);}
 void save(String slot,JSONObject credential)throws Exception{synchronized(LOCK){saveLocked(slot,credential);}}
 private void saveLocked(String slot,JSONObject credential)throws Exception{
  validate(slot);byte[] plain=credential.toString().getBytes(StandardCharsets.UTF_8);if(plain.length>16384)throw new IllegalArgumentException("Credential too large");
  byte[] encrypted;
  try{Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,key(slot,true));c.updateAAD(aad(slot));byte[] body=c.doFinal(plain);ByteArrayOutputStream out=new ByteArrayOutputStream();out.write(1);out.write(c.getIV().length);out.write(c.getIV());out.write(body);encrypted=out.toByteArray();}finally{Arrays.fill(plain,(byte)0);}
  AtomicFile target=new AtomicFile(file(slot));FileOutputStream stream=null;
  try{stream=target.startWrite();stream.write(encrypted);target.finishWrite(stream);}catch(Exception e){if(stream!=null)target.failWrite(stream);throw e;}
 }
 JSONObject load(String slot)throws Exception{synchronized(LOCK){return loadLocked(slot);}}
 private JSONObject loadLocked(String slot)throws Exception{
  validate(slot);if(!exists(slot))return null;byte[] raw=new AtomicFile(file(slot)).readFully();if(raw.length<30||raw.length>16480||raw[0]!=1||raw[1]!=12)throw new IOException("Invalid encrypted credential");
  Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,key(slot,false),new GCMParameterSpec(128,Arrays.copyOfRange(raw,2,14)));c.updateAAD(aad(slot));byte[] plain=c.doFinal(Arrays.copyOfRange(raw,14,raw.length));
  try{return new JSONObject(new String(plain,StandardCharsets.UTF_8));}finally{Arrays.fill(plain,(byte)0);}
 }
 synchronized boolean exists(String slot){return file(slot).exists()||new File(file(slot)+".bak").exists();}
 void delete(String slot)throws Exception{synchronized(LOCK){deleteLocked(slot);}}
 private void deleteLocked(String slot)throws Exception{
  validate(slot);new AtomicFile(file(slot)).delete();if(exists(slot))throw new IOException("Credential deletion failed");KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);ks.deleteEntry(alias(slot));
 }
 boolean hardwareBacked(String slot)throws Exception{return ((KeyInfo)SecretKeyFactory.getInstance("AES","AndroidKeyStore").getKeySpec(key(slot,false),KeyInfo.class)).isInsideSecureHardware();}
}
