---
name: store-forms
description: "Fill App Store Connect and Google Play Console forms via Python+Playwright automation. Handles age rating, privacy, data safety, content rating, export compliance, IDFA, target audience, and ads declaration."
argument-hint: "[ios|android|both]"
---

This skill fills store forms using **Python scripts with Playwright** (NOT Playwright MCP).
Zero LLM token cost for browser automation — the scripts run deterministically.

## Step 1: Ensure Credentials

Run the credential manager to check/setup saved credentials:

```bash
python3 ${PLUGIN_DIR}/scripts/credentials_manager.py --show
```

If not configured:
```bash
python3 ${PLUGIN_DIR}/scripts/credentials_manager.py --setup
```

Credentials are saved globally at `~/.store-deploy/credentials.json` and reused across projects.

## Step 2: Analyze App for Form Answers

Read the project to determine form answers:

1. Read `app.json` / `app.config.ts` — extract bundleIdentifier, package name
2. Read `package.json` — check for ad SDKs (`react-native-google-mobile-ads`, `expo-ads-admob`), analytics, UGC features
3. Check `app.json` for `ITSAppUsesNonExemptEncryption`

Generate a `forms_config.json` in the project root:

```json
{
  "has_ads": false,
  "has_ugc": false,
  "has_encryption": false,
  "has_violence": false,
  "has_sexual": false,
  "has_profanity": false,
  "has_drugs": false,
  "has_gambling": false,
  "has_iap": false,
  "privacy_url": "https://example.com/privacy",
  "data_collection": [],
  "review_notes": "",
  "iarc_category": "utility",
  "min_age": 18
}
```

Set `has_ads: true` if ad SDK found. Set `data_collection: ["analytics", "advertising"]` as appropriate.

## Step 3: Run Automation Scripts

**IMPORTANT**: Tell the user:
> "Browser will open. Please log into the store console if prompted. The script will fill forms automatically."

### iOS:
```bash
python3 ${PLUGIN_DIR}/scripts/store_forms_ios.py \
  --app-id {ASC_APP_ID} \
  --bundle-id {BUNDLE_ID} \
  --config forms_config.json \
  --project .
```

### Android:
```bash
python3 ${PLUGIN_DIR}/scripts/store_forms_android.py \
  --package-name {PACKAGE_NAME} \
  --config forms_config.json \
  --project .
```

### Run specific forms only:
```bash
# iOS: only age_rating and review_info
python3 ${PLUGIN_DIR}/scripts/store_forms_ios.py --app-id 123 --forms age_rating,review_info

# Android: only content_rating and ads_declaration
python3 ${PLUGIN_DIR}/scripts/store_forms_android.py --package-name com.x.y --forms content_rating,ads_declaration
```

### Dry run (preview without browser):
```bash
python3 ${PLUGIN_DIR}/scripts/store_forms_ios.py --app-id 123 --config forms_config.json --dry-run
```

## Step 4: Handle Failures

If a form step fails (selector changed, page layout updated):
- The script pauses and asks the user to complete that step manually
- Error screenshots are saved to `~/.store-deploy/error-screenshots/`
- The script continues to the next form after manual completion

If selectors need updating, edit the Python scripts directly in `${PLUGIN_DIR}/scripts/`.

## Step 5: Report

```
Store Forms Complete
====================
iOS:
- [x] Age Rating
- [x] App Privacy
- [x] Review Info
- [x] Export Compliance
- [x] IDFA

Android:
- [x] Content Rating (IARC)
- [x] Data Safety
- [x] Target Audience
- [x] Ads Declaration
```

## Available iOS Forms

| Form | CLI name | Description |
|------|----------|-------------|
| Age Rating | `age_rating` | Violence, sexual content, profanity questionnaire |
| App Privacy | `app_privacy` | Privacy policy URL + data collection declarations |
| Review Info | `review_info` | App review contact info (auto-filled from credentials) |
| Export Compliance | `export_compliance` | Encryption usage declaration |
| IDFA | `idfa` | Advertising identifier declaration |

## Available Android Forms

| Form | CLI name | Description |
|------|----------|-------------|
| Content Rating | `content_rating` | IARC questionnaire |
| Data Safety | `data_safety` | Data collection, sharing, encryption declarations |
| Target Audience | `target_audience` | Age group selection |
| Ads Declaration | `ads_declaration` | Whether app contains ads |
