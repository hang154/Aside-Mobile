package ai.decisionos.aside;
import android.webkit.*;
import android.view.View;
/** Shared app-owned WebView cookie profile; portal credentials are captured natively and saved after authenticated evidence. */
final class WebSessionPolicy {
 static void attach(WebView web){CookieManager.getInstance().setAcceptCookie(true);CookieManager.getInstance().setAcceptThirdPartyCookies(web,true);web.getSettings().setDomStorageEnabled(true);web.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_YES);PortalCredentialCapture.attach(web);}
 static void checkpoint(){CookieManager.getInstance().flush();}
}
