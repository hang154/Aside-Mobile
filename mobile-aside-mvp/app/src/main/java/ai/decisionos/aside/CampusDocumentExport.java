package ai.decisionos.aside;
import android.app.Activity;import android.content.*;import android.net.Uri;import java.io.*;import java.security.MessageDigest;
/** User-selected Android document provider export. Google Drive handles its own account. */
final class CampusDocumentExport {
 static final int REQUEST=8246;static final String PREF="campus_document_export";
 static String mime(String name){String ext=name.substring(name.lastIndexOf('.')+1);String type=android.webkit.MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext);return type==null?"application/octet-stream":type;}
 static void start(GoalAgentActivity a,Uri source,String name){try{
  validate(a,source);if(!name.matches("[A-Za-z0-9._-]{1,100}\\.(pdf|docx|pptx|hwpx)"))throw new IOException();
  SharedPreferences p=a.getSharedPreferences(PREF,0);if(!p.getString("source","").isEmpty()&&System.currentTimeMillis()-p.getLong("started",0)<1800000){a.toast("진행 중인 저장 창을 먼저 마쳐 주세요.");return;}
  p.edit().putString("source",source.toString()).putString("name",name).putLong("started",System.currentTimeMillis()).commit();
  Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType(mime(name)).putExtra(Intent.EXTRA_TITLE,name).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
  try{a.startActivityForResult(intent,REQUEST);}catch(Exception e){p.edit().clear().commit();throw e;}
 }catch(Exception e){a.toast("문서 저장 창을 열지 못했어요.");}}
 static File validate(Context a,Uri source)throws Exception{
  if(!"content".equals(source.getScheme())||!(a.getPackageName()+".documents").equals(source.getAuthority())||source.getPathSegments().size()!=1)throw new IOException("invalid source");
  String name=source.getLastPathSegment();if(name==null||!name.matches("[0-9a-f]{64}\\.(pdf|docx|pptx|hwpx)"))throw new IOException("invalid source");
  File f=new File(new File(a.getFilesDir(),"documents"),name);if(!f.isFile()||f.length()==0||f.length()>8388608)throw new IOException("invalid length");
  try(InputStream in=new FileInputStream(f)){if(!digest(in).equals(name.substring(0,64)))throw new IOException("source hash mismatch");}return f;
 }
 static String digest(InputStream in)throws Exception{MessageDigest md=MessageDigest.getInstance("SHA-256");byte[] buf=new byte[8192];int n,total=0;while((n=in.read(buf))!=-1){total+=n;if(total>8388608)throw new IOException("too large");md.update(buf,0,n);}StringBuilder hash=new StringBuilder();for(byte b:md.digest())hash.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return hash.toString();}
 static void writeVerified(Context context,Uri source,Uri destination)throws Exception{
  File file=validate(context,source);if(destination==null||!"content".equals(destination.getScheme())||source.getAuthority().equals(destination.getAuthority()))throw new IOException("invalid destination");
  try(InputStream in=new FileInputStream(file);OutputStream out=context.getContentResolver().openOutputStream(destination,"wt")){if(out==null)throw new IOException("destination unavailable");byte[] buf=new byte[8192];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);out.flush();}
  try(InputStream in=context.getContentResolver().openInputStream(destination)){if(in==null||!digest(in).equals(source.getLastPathSegment().substring(0,64)))throw new IOException("destination readback mismatch");}
 }
 static void result(GoalAgentActivity a,int result,Intent data){SharedPreferences pending=a.getSharedPreferences(PREF,0);String saved=pending.getString("source","");long began=pending.getLong("started",0);pending.edit().clear().commit();
  if(result!=Activity.RESULT_OK){a.toast("문서 저장을 취소했어요.");return;}if(saved.isEmpty()||System.currentTimeMillis()-began>1800000||data==null||data.getData()==null){a.toast("저장 요청이 만료됐어요. 다시 선택해 주세요.");return;}
  Uri source=Uri.parse(saved),destination=data.getData();new Thread(()->{String message;try{writeVerified(a,source,destination);a.getSharedPreferences("campus_export_receipts",0).edit().putString("source_sha256",source.getLastPathSegment().substring(0,64)).putString("provider",destination.getAuthority()).putLong("verified_at",System.currentTimeMillis()).commit();message="선택한 저장소에 저장하고 파일 내용을 확인했어요. 클라우드 동기화 상태는 해당 앱에서 확인해 주세요.";}catch(Exception e){message="저장 완료를 확인하지 못했어요. 선택한 저장소를 확인한 뒤 재시도해 주세요.";}final String text=message;a.runOnUiThread(()->{if(!a.isDestroyed())a.toast(text);});},"nubi-document-export").start();
 }
}
