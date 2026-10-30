package ai.decisionos.aside;

import android.content.Context;
import android.net.Uri;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;

/** Local, user-initiated text inference. No shell, network, or screen access. */
public final class LocalModel {
    public interface Callback { void done(String result); }
    private static final long MAX_BYTES = 2L * 1024 * 1024 * 1024;
    private static volatile boolean busy;
    public static File model(Context c) { return new File(c.getFilesDir(), "local-model.gguf"); }
    public static synchronized boolean begin() { if (busy) return false; busy = true; return true; }
    private static synchronized void finish() { busy = false; }
    public static void importModel(Context context, Uri uri, Callback cb) {
        Context c=context.getApplicationContext();
        if (!begin()) { cb.done("다른 모델 작업이 진행 중입니다."); return; }
        new Thread(() -> {
            File tmp=new File(c.getFilesDir(),"local-model.tmp");
            try (InputStream in=c.getContentResolver().openInputStream(uri);
                 OutputStream out=new FileOutputStream(tmp)) {
                if(in==null) throw new IOException("파일을 열 수 없습니다.");
                byte[] b=new byte[65536]; long total=0; int n;
                while((n=in.read(b))!=-1){total+=n;if(total>MAX_BYTES)throw new IOException("모델은 2GB 이하여야 합니다.");out.write(b,0,n);}
                if(total<4)throw new IOException("모델 파일이 비어 있습니다.");
                out.flush();
                try(FileInputStream check=new FileInputStream(tmp)) {
                    if(check.read()!='G'||check.read()!='G'||check.read()!='U'||check.read()!='F') throw new IOException("GGUF 파일이 아닙니다.");
                }
                if(!tmp.renameTo(model(c)))throw new IOException("모델 저장 실패");
                cb.done("모델 준비 완료 ("+(total/1024/1024)+" MB). 질문을 입력하세요.");
            } catch(Exception e) { tmp.delete(); cb.done("모델 불러오기 실패: "+e.getMessage()); }
            finally { finish(); }
        },"aside-model-import").start();
    }
    public static void infer(Context context,String prompt,Callback cb) {
        Context c=context.getApplicationContext();
        if(!model(c).isFile()){cb.done("먼저 GGUF 모델 파일을 선택하세요.");return;}
        if(prompt.trim().isEmpty()||prompt.length()>2000){cb.done("질문을 1~2000자로 입력하세요.");return;}
        if(!begin()){cb.done("다른 모델 작업이 진행 중입니다.");return;}
        new Thread(() -> {
            Process p=null;
            try {
                String libs=c.getApplicationInfo().nativeLibraryDir;
                File binary=new File(libs,"libllama_exec.so");
                ProcessBuilder pb=new ProcessBuilder(binary.getAbsolutePath(),"-m",model(c).getAbsolutePath(),"--offline","-ngl","0","-t","4","-c","2048","-n","160","--reasoning","off","-st","--simple-io","--no-display-prompt","--log-disable","-p",prompt);
                pb.directory(new File(libs));pb.environment().put("LD_LIBRARY_PATH",libs);pb.redirectErrorStream(true);
                p=pb.start(); Process process=p;
                ByteArrayOutputStream captured=new ByteArrayOutputStream();
                Thread reader=new Thread(() -> { try(InputStream in=process.getInputStream()){byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1){if(captured.size()<512000)captured.write(b,0,n);}}catch(IOException ignored){} });reader.start();
                if(!p.waitFor(120,TimeUnit.SECONDS)){p.destroyForcibly();reader.join(3000);throw new IOException("추론 시간 초과");}
                reader.join(3000); String all=captured.toString(StandardCharsets.UTF_8.name());
                if(p.exitValue()!=0)throw new IOException("엔진 종료 코드 "+p.exitValue()+": "+all.substring(Math.max(0,all.length()-500)));
                int start=all.lastIndexOf("> "+prompt); if(start<0)throw new IOException("엔진 응답 형식을 확인할 수 없습니다.");
                String answer=all.substring(start+2+prompt.length()).trim();
                int end=answer.indexOf("[ Prompt:");if(end>=0)answer=answer.substring(0,end).trim();
                if(answer.isEmpty())throw new IOException("빈 응답");
                cb.done(answer);
            } catch(Exception e){cb.done("로컬 추론 실패: "+e.getMessage());}
            finally {if(p!=null)p.destroy();finish();}
        },"aside-local-inference").start();
    }
    private LocalModel(){}
}
