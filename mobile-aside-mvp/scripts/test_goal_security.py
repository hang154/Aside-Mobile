"""Check release manifest and native boundaries. Fixture tests complement real-device checks."""
from pathlib import Path
import xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1];b=r/'app/src/main/java/ai/decisionos/aside';ns='{http://schemas.android.com/apk/res/android}'
m=ET.parse(r/'app/src/main/AndroidManifest.xml').getroot()
services=m.findall('.//service')
assert len(services)==1, 'Only the campus JobService belongs in this release'
service=services[0]
assert service.attrib[ns+'name']=='.CampusNoticeMonitor'
assert service.attrib.get(ns+'exported')=='false'
assert service.attrib.get(ns+'permission')=='android.permission.BIND_JOB_SERVICE'
for activity in m.findall('.//activity'):
 if 'Goal' in activity.attrib[ns+'name'] or 'CharacterWorkspace' in activity.attrib[ns+'name']:assert activity.attrib.get(ns+'exported')=='false'
s=(b/'GoalDiscoveryActivity.java').read_text();assert 'addJavascriptInterface' not in s;assert 'setAllowFileAccess(false)' in s and 'setAllowContentAccess(false)' in s;assert 'MIXED_CONTENT_NEVER_ALLOW' in s;assert 'searchMatches' in s;assert 'seenGeneration!=generation' in s;assert 'request!=generation' in s
s=(b/'GoalStore.java').read_text();assert "owner='device'" in s;assert 'Foreign goal record' in s;assert 'Deleted or foreign goal' in s;assert 'if(!analytics)return' in s;assert 'ON DELETE CASCADE' in s
s=(b/'CharacterWorkspaceActivity.java').read_text();assert 'manual_only' in s;assert 'conditionsVerified' in s;assert 'self_reported' in s;assert '"state","verified"' not in s;assert 'Intent.ACTION_SEND' not in s
print('PASS release manifest, read-only browser, stale selection, ownership and purchase boundary checks')
