---
name: store-submit
description: "Submit app binary to App Store and Google Play via EAS Submit. Handles submission configuration and post-submission metadata upload."
argument-hint: "[ios|android|both]"
---

## Step 1: Check Build

Run `eas build:list --limit 3 --platform {platform}` to find the latest successful build.

If no build found, suggest running `/store-build` first.

## Step 2: Check eas.json Submit Config

Verify `eas.json` has submit profiles. If `ascAppId` is "ASK_DEVELOPER" or missing, ask the developer.

## Step 3: Submit Binary

**iOS:**
```bash
eas submit --platform ios --profile production
```

**Android:**
```bash
eas submit --platform android --profile production
```

If submitting a specific build:
```bash
eas submit --platform {platform} --profile production --id {BUILD_ID}
```

## Step 4: Post-Submission

After binary upload, also upload metadata and screenshots if they exist:

```bash
# iOS
fastlane ios upload_all

# Android
fastlane android upload_metadata
fastlane android upload_screenshots
```

## Step 5: Report

```
Submission Complete
===================
iOS:     Binary submitted to App Store Connect
Android: AAB submitted to Google Play Console

Next:
- iOS: Review at https://appstoreconnect.apple.com
- Android: Review at https://play.google.com/console
```
