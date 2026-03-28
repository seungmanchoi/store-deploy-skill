---
name: store-admob
description: "Set up AdMob app and create ad units (banner, interstitial, rewarded) via Python+Playwright automation. Saves ad unit IDs to project config."
argument-hint: "[ios|android|both]"
---

This skill sets up AdMob using **Python scripts with Playwright** (NOT Playwright MCP).
Zero LLM token cost for browser automation.

## Step 1: Ensure Credentials

```bash
python3 ${PLUGIN_DIR}/scripts/credentials_manager.py --show
```

If not configured:
```bash
python3 ${PLUGIN_DIR}/scripts/credentials_manager.py --setup
```

## Step 2: Determine Setup Parameters

Read `app.json` to extract:
- App name (expo.name)
- Bundle ID (expo.ios.bundleIdentifier)
- Package name (expo.android.package)

Ask the developer:
- Which ad types? (banner, interstitial, rewarded) — default: all three
- Is the app already published? (affects AdMob app linking)
- Output format? (json or typescript)

## Step 3: Run AdMob Setup Script

**IMPORTANT**: Tell the user:
> "Browser will open. Please log into AdMob (https://apps.admob.com) if prompted."

### Both platforms:
```bash
python3 ${PLUGIN_DIR}/scripts/admob_setup.py \
  --app-name "{APP_NAME}" \
  --platform both \
  --bundle-id {BUNDLE_ID} \
  --package-name {PACKAGE_NAME} \
  --project .
```

### iOS only:
```bash
python3 ${PLUGIN_DIR}/scripts/admob_setup.py \
  --app-name "{APP_NAME}" \
  --platform ios \
  --bundle-id {BUNDLE_ID} \
  --project .
```

### Android only:
```bash
python3 ${PLUGIN_DIR}/scripts/admob_setup.py \
  --app-name "{APP_NAME}" \
  --platform android \
  --package-name {PACKAGE_NAME} \
  --project .
```

### Custom ad types:
```bash
python3 ${PLUGIN_DIR}/scripts/admob_setup.py \
  --app-name "{APP_NAME}" \
  --platform both \
  --bundle-id {BUNDLE_ID} \
  --package-name {PACKAGE_NAME} \
  --ad-types banner,interstitial \
  --project .
```

### With TypeScript output:
```bash
python3 ${PLUGIN_DIR}/scripts/admob_setup.py \
  --app-name "{APP_NAME}" \
  --platform both \
  --bundle-id {BUNDLE_ID} \
  --package-name {PACKAGE_NAME} \
  --output typescript \
  --project .
```

### Dry run:
```bash
python3 ${PLUGIN_DIR}/scripts/admob_setup.py --app-name "My App" --dry-run
```

## Step 4: Verify Output

The script saves AdMob IDs to `store-deploy.json`:
```json
{
  "admob": {
    "ios": {
      "app_id": "ca-app-pub-XXXXX~XXXXX",
      "ad_units": {
        "banner": "ca-app-pub-XXXXX/XXXXX",
        "interstitial": "ca-app-pub-XXXXX/XXXXX",
        "rewarded": "ca-app-pub-XXXXX/XXXXX"
      }
    },
    "android": {
      "app_id": "ca-app-pub-XXXXX~XXXXX",
      "ad_units": {
        "banner": "ca-app-pub-XXXXX/XXXXX",
        "interstitial": "ca-app-pub-XXXXX/XXXXX",
        "rewarded": "ca-app-pub-XXXXX/XXXXX"
      }
    }
  }
}
```

If `--output typescript` was used, also check `src/shared/config/admob.ts`.

Read the output file and confirm the IDs are populated. If any are empty, the script encountered issues — check `~/.store-deploy/error-screenshots/`.

## Step 5: Integrate into App

If the project uses `react-native-google-mobile-ads`, help configure:

1. Add app IDs to `app.json`:
```json
{
  "expo": {
    "plugins": [
      ["react-native-google-mobile-ads", {
        "androidAppId": "ca-app-pub-XXXXX~XXXXX",
        "iosAppId": "ca-app-pub-XXXXX~XXXXX"
      }]
    ]
  }
}
```

2. Use ad unit IDs from the generated config in the app code.

## Step 6: Report

```
AdMob Setup Complete
====================
iOS App ID:     ca-app-pub-XXXXX~XXXXX
Android App ID: ca-app-pub-XXXXX~XXXXX

Ad Units:
  banner:       ca-app-pub-XXXXX/XXXXX (iOS) / ca-app-pub-XXXXX/XXXXX (Android)
  interstitial: ca-app-pub-XXXXX/XXXXX (iOS) / ca-app-pub-XXXXX/XXXXX (Android)
  rewarded:     ca-app-pub-XXXXX/XXXXX (iOS) / ca-app-pub-XXXXX/XXXXX (Android)

Config saved to: store-deploy.json
```
