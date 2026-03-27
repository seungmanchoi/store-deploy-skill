---
name: store-admob
description: "Set up AdMob app and create ad units (banner, interstitial, rewarded) via browser automation. Saves ad unit IDs to project config."
argument-hint: "[ios|android|both]"
disable-model-invocation: true
---

This skill sets up AdMob for the app using browser automation.

## Prerequisites

Ask the developer:
> "Please log into AdMob (https://apps.admob.com) in your browser, then tell me when ready."

## Step 1: Navigate to AdMob

Use Playwright MCP or agent-browser to navigate to `https://apps.admob.com/v2/home`.
Take a snapshot to check if the app already exists.

## Step 2: Create App (if not exists)

1. Click "Add app" or "Apps" > "Add app"
2. Select platform (iOS or Android)
3. If app is published: search by name or bundle ID
4. If not published: select "No, it's not listed" and enter app name
5. Complete creation

Repeat for the other platform if "both" selected.

## Step 3: Create Ad Units

For each ad type the developer wants (ask which ones):

### Banner
- Navigate to Ad Units > Add ad unit > Banner
- Name: `{app_name}_banner`
- Save and note the ad unit ID

### Interstitial
- Add ad unit > Interstitial
- Name: `{app_name}_interstitial`
- Save and note the ad unit ID

### Rewarded
- Add ad unit > Rewarded
- Name: `{app_name}_rewarded`
- Save and note the ad unit ID

## Step 4: Save Config

Write ad unit IDs to the project. Check if the project uses a config pattern:

**Option A**: `src/shared/config/admob.ts` (FSD pattern)
```typescript
export const ADMOB_CONFIG = {
  ios: {
    banner: "ca-app-pub-XXXXX/XXXXX",
    interstitial: "ca-app-pub-XXXXX/XXXXX",
    rewarded: "ca-app-pub-XXXXX/XXXXX",
  },
  android: {
    banner: "ca-app-pub-XXXXX/XXXXX",
    interstitial: "ca-app-pub-XXXXX/XXXXX",
    rewarded: "ca-app-pub-XXXXX/XXXXX",
  },
};
```

**Option B**: `app.json` extras
```json
{
  "expo": {
    "extra": {
      "admob": {
        "ios": { "banner": "...", "interstitial": "...", "rewarded": "..." },
        "android": { "banner": "...", "interstitial": "...", "rewarded": "..." }
      }
    }
  }
}
```

## Step 5: Report

```
AdMob Setup Complete
====================
iOS App ID:     ca-app-pub-XXXXX~XXXXX
Android App ID: ca-app-pub-XXXXX~XXXXX

Ad Units:
  banner:       ca-app-pub-XXXXX/XXXXX (iOS) / ca-app-pub-XXXXX/XXXXX (Android)
  interstitial: ca-app-pub-XXXXX/XXXXX (iOS) / ca-app-pub-XXXXX/XXXXX (Android)
  rewarded:     ca-app-pub-XXXXX/XXXXX (iOS) / ca-app-pub-XXXXX/XXXXX (Android)

Config saved to: {file_path}
```
