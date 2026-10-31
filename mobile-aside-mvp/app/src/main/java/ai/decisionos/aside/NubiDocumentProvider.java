package ai.decisionos.aside;
import android.content.*;import android.database.*;import android.net.Uri;import android.os.ParcelFileDescriptor;import android.provider.OpenableColumns;import java.io.*;
/** Grants read access to one hash-verified generated file; no directory/write access. */
public final class NubiDocumentProvider extends ContentProvider {
 public boolean onCreate(){return true;}
 private File file(Uri uri)throws FileNotFoundException{String n=uri.getLastPathSegment();if(uri.getPathSegments().size()!=1||n==null||!n.matches("[0-9a-f]{64}\\.(docx|hwpx)"))throw new FileNotFoundException();File f=new File(new File(getContext().getFilesDir(),"documents"),n);if(!f.isFile())throw new FileNotFoundException();return f;}
 public String getType(Uri u){return u.toString().endsWith(".docx")?"application/vnd.openxmlformats-officedocument.wordprocessingml.document":"application/vnd.hancom.hwpx";}
 public ParcelFileDescriptor openFile(Uri u,String mode)throws FileNotFoundException{if(!"r".equals(mode))throw new FileNotFoundException("read only");return ParcelFileDescriptor.open(file(u),ParcelFileDescriptor.MODE_READ_ONLY);}
 public Cursor query(Uri u,String[] projection,String selection,String[] args,String sort){try{File f=file(u);String[] cols=projection==null?new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE}:projection;MatrixCursor c=new MatrixCursor(cols);Object[] row=new Object[cols.length];for(int i=0;i<cols.length;i++)row[i]=OpenableColumns.DISPLAY_NAME.equals(cols[i])?"누비_예산서"+(f.getName().endsWith("docx")?".docx":".hwpx"):OpenableColumns.SIZE.equals(cols[i])?f.length():null;c.addRow(row);return c;}catch(FileNotFoundException e){return null;}}
 public Uri insert(Uri u,ContentValues v){throw new UnsupportedOperationException();}public int update(Uri u,ContentValues v,String s,String[] a){throw new UnsupportedOperationException();}public int delete(Uri u,String s,String[] a){throw new UnsupportedOperationException();}
}
