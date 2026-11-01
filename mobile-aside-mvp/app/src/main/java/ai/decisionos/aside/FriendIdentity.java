package ai.decisionos.aside;
import android.content.Context;import android.security.keystore.*;import android.util.Base64;import javax.crypto.*;import javax.crypto.spec.GCMParameterSpec;import java.security.KeyStore;import java.nio.charset.StandardCharsets;
/** App-private encrypted pairing; neither credentials nor model bearer tokens enter chat. */
final class FriendIdentity {
 static final String ALIAS="nubi-friend-identity-v1";
 static SecretKey key()throws Exception{KeyStore k=KeyStore.getInstance("AndroidKeyStore");k.load(null);if(k.containsAlias(ALIAS))return ((KeyStore.SecretKeyEntry)k.getEntry(ALIAS,null)).getSecretKey();KeyGenerator g=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");g.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());return g.generateKey();}
 static void save(Context c,String value)throws Exception{Cipher x=Cipher.getInstance("AES/GCM/NoPadding");x.init(Cipher.ENCRYPT_MODE,key());String data=Base64.encodeToString(x.getIV(),Base64.NO_WRAP)+":"+Base64.encodeToString(x.doFinal(value.getBytes(StandardCharsets.UTF_8)),Base64.NO_WRAP);if(!c.getSharedPreferences("nubi_friend_identity",0).edit().putString("encrypted",data).commit())throw new java.io.IOException("pairing save failed");}
 static String load(Context c)throws Exception{String data=c.getSharedPreferences("nubi_friend_identity",0).getString("encrypted","");if(data.isEmpty())return null;String[] a=data.split(":",2);Cipher x=Cipher.getInstance("AES/GCM/NoPadding");x.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,Base64.decode(a[0],Base64.NO_WRAP)));return new String(x.doFinal(Base64.decode(a[1],Base64.NO_WRAP)),StandardCharsets.UTF_8);}
 static void clear(Context c){c.getSharedPreferences("nubi_friend_identity",0).edit().clear().commit();}
}
