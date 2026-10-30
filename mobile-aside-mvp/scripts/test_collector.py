#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
java=root/'app/src/main/java/ai/decisionos/aside'
service=(java/'EngagementService.java').read_text()
store=(java/'CollectorStore.java').read_text()
config=ET.parse(root/'app/src/main/res/xml/aside_engagement.xml').getroot()
ns='{http://schemas.android.com/apk/res/android}'
assert config.attrib[ns+'canRetrieveWindowContent']=='false'
for forbidden in ('getText(', 'getContentDescription(', 'getSource(', 'getRootInActiveWindow(', 'TYPE_VIEW_TEXT_CHANGED'):
    assert forbidden not in service, forbidden
assert 'k.isKeyguardLocked()' in store and 'p.isInteractive()' in store
assert 'getBoolean(ACTIVE,false)' in store and 'serviceEnabled(c)' in store
assert '5000' in store and 'RETAIN_MS' in store
assert 'http' not in store.lower()
print('PASS collector metadata boundary and opt-in checks')
