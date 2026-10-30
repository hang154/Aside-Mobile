# Aside Mobile private backup

Backup of `mobile-aside-mvp/` and the Android build workflow from `hang154/OpenCLI`, branch `mobile-aside/mvp-android`, at commit `425cc8ee8bc82214e6533da8911d541a914f50f9`. This repository includes the later, sanitized real-device verification report `mobile-aside-mvp/reports/DEVICE_TEST_2026-10-30.md`.

The original workflow is retained unchanged. Its push trigger targets `mobile-aside/**`, not this backup's `main` branch; the workflow can be started manually via Actions. Its release-publishing step is conditional on the original branch name. The existing verification artifacts describe the earlier source snapshot and do not cover this new report or the newer workflow; see the device report for the APK tested.

Screenshots are kept locally and are not included in this repository. Some contain sensitive information.
