package ai.decisionos.aside;
import android.app.*;import android.os.Bundle;import android.content.Intent;import android.view.WindowManager;import org.json.JSONObject;import java.nio.file.*;import java.nio.charset.StandardCharsets;import java.util.*;
final class NativeVaultChecks {
 static void run(GoalInstrumentation i,Bundle args){Bundle out=new Bundle();NativeCredentialVault v=new NativeCredentialVault(i.getTargetContext());CredentialVaultActivity activity=null;String phase=args.getString("vaultPhase","");try{
  String marker="SYNTHETIC_ONLY_NUBI_SECRET_1429";
  if(phase.equals("write")){v.save("test_one",new JSONObject().put("secret",marker));out.putString("stream","PASS persisted synthetic credential for next process\n");i.finish(-1,out);return;}
  if(phase.equals("read")){i.check(v.load("test_one").getString("secret").equals(marker),"survives process restart");v.delete("test_one");out.putString("stream","PASS decrypt after process restart; synthetic data deleted\n");i.finish(-1,out);return;}
  v.delete("test_one");v.delete("test_two");JSONObject j=new JSONObject().put("account","synthetic@example.invalid").put("secret",marker);
  i.check(!v.exists("test_one"),"initial empty");v.save("test_one",j);i.check(v.exists("test_one"),"saved");i.check(v.load("test_one").getString("secret").equals(marker),"roundtrip");
  byte[] first=Files.readAllBytes(v.file("test_one").toPath());i.check(!new String(first,StandardCharsets.ISO_8859_1).contains(marker),"plaintext absent");
  v.save("test_one",j);byte[] second=Files.readAllBytes(v.file("test_one").toPath());i.check(!Arrays.equals(first,second),"fresh random IV");i.check(v.load("test_two")==null,"slot isolation");
  v.save("test_two",j);Files.write(v.file("test_two").toPath(),second);boolean bound=false;try{v.load("test_two");}catch(Exception e){bound=true;}i.check(bound,"cross-slot copy rejected");
  second[second.length-1]^=1;Files.write(v.file("test_one").toPath(),second);boolean corrupt=false;try{v.load("test_one");}catch(Exception e){corrupt=true;}i.check(corrupt,"tamper rejected");
  v.save("test_one",j);i.check(!v.file("test_one").getCanonicalPath().contains("shared_prefs"),"no preference secret");i.check(v.file("test_one").getCanonicalPath().startsWith(i.getTargetContext().getNoBackupFilesDir().getCanonicalPath()),"backup-excluded location");boolean hw=v.hardwareBacked("test_one");
  v.delete("test_one");i.check(v.load("test_one")==null,"delete removes data");Files.write(v.file("test_one").toPath(),first);boolean lost=false;try{v.load("test_one");}catch(Exception e){lost=true;}i.check(lost,"missing key fails closed");
  boolean scope=false;try{v.load("../../other");}catch(IllegalArgumentException e){scope=true;}i.check(scope,"invalid slot rejected");
  activity=(CredentialVaultActivity)i.startActivitySync(new Intent(i.getTargetContext(),CredentialVaultActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));final CredentialVaultActivity a=activity;
  i.check((a.getWindow().getAttributes().flags&WindowManager.LayoutParams.FLAG_SECURE)!=0,"screen capture blocked");i.check(!i.getTargetContext().getPackageManager().getActivityInfo(new android.content.ComponentName(i.getTargetContext(),CredentialVaultActivity.class),0).exported,"native editor not exported");
  out.putString("stream","PASS "+i.checks+" native vault checks; AndroidKeyStore hardware-backed="+hw+"; production UI device-confirmation success not automated\n");
 }catch(Throwable e){out.putString("stream","FAIL native vault check: "+e.getClass().getSimpleName()+"\n");}finally{if(activity!=null){final CredentialVaultActivity a=activity;i.runOnMainSync(a::finish);}if(!phase.equals("write"))try{v.delete("test_one");v.delete("test_two");}catch(Exception ignored){}}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
