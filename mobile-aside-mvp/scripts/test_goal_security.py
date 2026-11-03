"""Check release manifest and native boundaries. Fixture tests complement real-device checks."""
from pathlib import Path
import xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1];b=r/'app/src/main/java/ai/decisionos/aside';ns='{http://schemas.android.com/apk/res/android}'
m=ET.parse(r/'app/src/main/AndroidManifest.xml').getroot()
services=m.findall('.//service')
assert {x.attrib[ns+'name'] for x in services}=={'.CampusNoticeMonitor','.BlackboardNoticeMonitor','.ChatWork'}
debug=ET.parse(r/'app/src/debug/AndroidManifest.xml').getroot()
assert debug.find('.//service').attrib[ns+'permission']=='android.permission.BIND_ACCESSIBILITY_SERVICE'
assert 'getRootInActiveWindow' not in (b/'EngagementService.java').read_text()
for service in services:
 if service.attrib[ns+'name'] in {'.CampusNoticeMonitor','.BlackboardNoticeMonitor','.ChatWork'}:
  assert service.attrib.get(ns+'exported')=={'.CampusNoticeMonitor':'false','.BlackboardNoticeMonitor':'true','.ChatWork':'false'}[service.attrib[ns+'name']]
  assert service.attrib.get(ns+'permission')=='android.permission.BIND_JOB_SERVICE'
 else:
  assert service.attrib.get(ns+'permission')=='android.permission.BIND_ACCESSIBILITY_SERVICE'
  config=ET.parse(r/'app/src/main/res/xml/aside_engagement.xml').getroot()
  assert config.attrib[ns+'canRetrieveWindowContent']=='false'
  source=(b/'EngagementService.java').read_text()
  assert 'getRootInActiveWindow' not in source and 'getText()' not in source
for activity in m.findall('.//activity')+m.findall('.//activity-alias'):
 if 'Goal' in activity.attrib[ns+'name'] or 'CharacterWorkspace' in activity.attrib[ns+'name']:assert activity.attrib.get(ns+'exported')=='false'
s=(b/'GoalDiscoveryActivity.java').read_text();assert 'addJavascriptInterface' not in s;assert 'setAllowFileAccess(false)' in s and 'setAllowContentAccess(false)' in s;assert 'MIXED_CONTENT_NEVER_ALLOW' in s;assert 'searchMatches' in s;assert 'seenGeneration!=generation' in s;assert 'request!=generation' in s
s=(b/'GoalStore.java').read_text();assert "owner='device'" in s;assert 'Foreign goal record' in s;assert 'Deleted or foreign goal' in s;assert 'if(!analytics)return' in s;assert 'ON DELETE CASCADE' in s
s=(b/'CompanionGoalTools.java').read_text();assert 'manual_only' in s;assert 'conditionsVerified' in s;assert 'self_reported' in s;assert '"state","verified"' not in s;assert 'Intent.ACTION_SEND' not in s
print('PASS release manifest, read-only browser, stale selection, ownership and purchase boundary checks')

for name in ['MainActivity','GoalHomeActivity','CharacterWorkspaceActivity','GoalDiscoveryActivity','CampusToolsActivity','UnistCalendarActivity','CollectorActivity','TaskActivity','BrowserWorkspaceActivity','ConcertTripActivity','AppRegistryActivity','PlanAssistantActivity','LifeActivity','UnifiedToolsActivity']:
 aliases=[x for x in m.findall('.//activity-alias') if x.get(ns+'name')=='.'+name]
 assert len(aliases)==1 and aliases[0].get(ns+'targetActivity')=='.CompanionEntryActivity',name
 assert not any(x.get(ns+'name')=='.'+name for x in m.findall('.//activity')),name
assert 'return true;' in (b/'GoalChatUi.java').read_text().split('boolean companionMode()')[1].split('boolean modern()')[0]
# Session checkpoints may use lifecycle callbacks, but must not restore legacy navigation
# wrappers, inspect content or start passive microphone/network collection.
application=(b/'NubiApplication.java').read_text()
assert 'WebSessionPolicy.checkpoint()' in application
assert 'WeakReference' in application
for forbidden in ('startActivity(', 'new Intent(', 'getText(', 'getUrl(', 'SpeechRecognizer', 'AudioRecord', 'HttpURLConnection', 'addJavascriptInterface'):
 assert forbidden not in application,forbidden
print('PASS companion-only launcher aliases and absence of legacy wrapper')
