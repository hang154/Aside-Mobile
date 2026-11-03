package ai.decisionos.aside;
import android.content.*;import android.net.Uri;import android.os.Bundle;import android.provider.MediaStore;import java.io.*;import java.nio.charset.StandardCharsets;
/** Real Android provider write/readback using synthetic data; no cloud or private document. */
final class CampusExportChecks {
 static void run(GoalInstrumentation i){Bundle out=new Bundle();Uri destination=null;File source=null;try{
  Context c=i.getTargetContext();byte[] bytes="누비 문서 저장 무결성 검증".getBytes(StandardCharsets.UTF_8);String sha=CampusDocumentExport.digest(new ByteArrayInputStream(bytes));File directory=new File(c.getFilesDir(),"documents");directory.mkdirs();source=new File(directory,sha+".docx");if(source.exists())throw new AssertionError("fixture collision");try(OutputStream stream=new FileOutputStream(source)){stream.write(bytes);}
  Uri uri=Uri.parse("content://"+c.getPackageName()+".documents/"+source.getName());
  ContentValues values=new ContentValues();values.put(MediaStore.Downloads.DISPLAY_NAME,"NUBI_EXPORT_TEST_"+System.nanoTime()+".docx");values.put(MediaStore.Downloads.MIME_TYPE,CampusDocumentExport.mime("test.docx"));destination=c.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);if(destination==null)throw new AssertionError("no destination");
  CampusDocumentExport.writeVerified(c,uri,destination);try(InputStream in=c.getContentResolver().openInputStream(destination)){i.check(sha.equals(CampusDocumentExport.digest(in)),"Android provider readback matches");}
  try{CampusDocumentExport.writeVerified(c,uri,uri);throw new AssertionError("own provider destination accepted");}catch(IOException expected){i.check(true,"own provider overwrite rejected");}
  try(OutputStream stream=new FileOutputStream(source)){stream.write("changed".getBytes(StandardCharsets.UTF_8));}
  try{CampusDocumentExport.writeVerified(c,uri,destination);throw new AssertionError("changed source accepted");}catch(IOException expected){i.check(true,"changed source rejected before export");}
  i.check(CampusDocumentExport.mime("test.pptx").contains("presentation"),"PPTX MIME");
  out.putString("stream","PASS "+i.checks+" Android provider export/readback/tamper checks; Drive sync not tested\n");
 }catch(Throwable e){out.putString("stream","FAIL "+e+"\n");}finally{if(destination!=null)i.getTargetContext().getContentResolver().delete(destination,null,null);if(source!=null)source.delete();}i.finish(out.getString("stream","").startsWith("PASS")?-1:0,out);}
}
