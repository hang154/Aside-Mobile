# English investor filming build — 2026-11-02

Branch: `demo/investor-en-20261102`, based on production `f72911f`.
English filming entry point: `InvestorDemoActivity`. Existing production activities and shared school WebView profile are preserved. Korean demo source is preserved at `demo/investor-ko-20261102`; original production APKs and Korean takes remain local.

## Verified live work

- English request → actual Qwen3.8-27B-abliterated-AWQ-W4A16 → four successful campus MCP calls → UNIST scholarship notice body → English source-backed summary. No personal eligibility assumption.
- English request → actual university Outlook search and selected email body → English DOCX draft → file attached to a recipient-free Outlook draft → saved subject and attachment verified by Outlook search. No sending.
- Existing login profile opened the official academic board, Blackboard Courses with actual courses, and Outlook inbox without another login. This verifies reuse of the currently valid session, not indefinite SSO lifetime.
- Native preview reads the generated DOCX bytes. Unprovided applicant facts remain explicitly blank. The draft is not the university's completed official application form.

## English build and checks

- App-authored filming UI, default requests, progress labels, document headings and draft content use English. Original school sites and Android system surfaces retain their original language.
- English task-intent gates preserve document/mail/notice tools. Final output instructions prohibit treating attachment-name metadata as attachment content.
- Outlook uses desktop user agent and a persistent CDP viewport for reliable DOM access. Existing selectors now support the observed `신규` compose button. Reuses the already authenticated Outlook URL instead of repeatedly traversing a temporarily failing school SSO endpoint.
- Python syntax checks passed; English DOCX missing-data/heading check passed; filming Activity contains no Korean UI strings.
- Gradle groupchat debug build passed; APK signature and unchanged ZIP payload entries verified. Installed final APK SHA-256 equals delivered APK: `5267360903504b331bffd6a4ac1933645d52f952f5d360fa07ddd6b8ae27d219`.
- Android launcher resolves to the English filming Activity. No app uninstall/data clear or credential extraction occurred.

## Local footage

Root: `/home/user-btc/다운로드/usf/nubi-investor-demo/`.
`english-originals/` is the delivery set, with raw uncut/unretimed Android screenrecord files (1080×2340, H.264, variable frame timestamps, no narration). `english-media-manifest.json` records duration and SHA-256. These are edit sources, not the finished 2:30 founder film.

- EN01: live scholarship request, navigation and English answer.
- EN02: actual portal/Blackboard/Outlook service-switching B-roll; manually operated navigation, not a claimed autonomous Qwen run.
- EN03: actual email-to-DOCX-to-Outlook-draft run.
- EN03B: separately recorded verified tool receipt and actual generated DOCX preview.
- EN04: large controls and hamburger benefit-use example, persistently labelled PRODUCT VISION.
- EN05: train boarding guidance concept, persistently labelled PRODUCT VISION; no real ticket/platform claimed.
- EN06: family app screens, persistently labelled PRODUCT VISION. The contact-containing native share chooser take is retained privately and excluded from delivery.
- EN07: Nubi closing logo/message.

The first EN03 model response overstated reading the source attachment; the tool only listed its name. The original trace is retained. EN03B explicitly states that attachment contents were not read; use this verified result rather than the unsupported response sentence. The generated application is a generic review draft, with missing personal facts, not a completed original attachment form. The runner now derives the displayed mail completion scope from successful tool receipts and retains the original model response separately.

Failed narrow-viewport, SSO-empty-response and changed-compose-button takes are retained under local `private/rejected/`; they are not delivery takes. EN01, EN03, and final vision footage used successive builds with the same English UI; private filming APK snapshots retain their exact bytes. Final APK additionally restores the launcher intent filter and direct Outlook entry.

## Remaining boundaries

Qwen/MCP runs on the Azrael host bridge; the APK is not an embedded/offline Qwen model. The USB/CDP bridge and configured Qwen service are needed for further live requests. Voice example buttons were filmed; live microphone transcription was not validated. Family linking, real coupon issuance, train booking/payment and in-store ordering are product-vision previews. No message, order or payment was sent.

Raw mail/service footage can contain account and academic information. It stays local; anonymize it before publishing the finished film. No capture, private receipt, credentials or video is included in Git.
