package ai.decisionos.aside;
import android.webkit.*;
import android.view.View;
/** Shared app-owned WebView cookie profile; passwords are managed by Android Autofill. */
final class WebSessionPolicy {
 static void attach(WebView web){CookieManager.getInstance().setAcceptCookie(true);CookieManager.getInstance().setAcceptThirdPartyCookies(web,true);web.getSettings().setDomStorageEnabled(true);web.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_YES);}
 static void checkpoint(){CookieManager.getInstance().flush();}
}
