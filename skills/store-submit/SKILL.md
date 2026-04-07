---
name: store-submit
description: "Submit app binary to App Store and Google Play via EAS Submit. Handles submission configuration and post-submission metadata upload."
argument-hint: "[ios|android|both]"
---

## Step 1: Check Build

Run `eas build:list --limit 3 --platform {platform}` to find the latest successful build.

If no build found, suggest running `/store-build` first.

## Step 2: Check eas.json Submit Config

Verify `eas.json` has submit profiles with proper iOS credentials:

```json
"ios": {
  "appleId": "blue_eng@hanmail.net",
  "ascApiKeyPath": "/Users/seungmanchoi/works/common/AuthKey_6FD6879KFW.p8",
  "ascApiKeyIssuerId": "69a6de87-13e2-47e3-e053-5b8c7c11a4d1",
  "ascApiKeyId": "6FD6879KFW"
}
```

**IMPORTANT: `ascApiKeyPath`는 반드시 절대 경로를 사용해야 합니다.**
- `~/works/common/...` (X) — EAS CLI가 `~`를 resolve하지 못해 "File does not exist" 에러 발생
- `/Users/seungmanchoi/works/common/...` (O) — 절대 경로 사용

If `ascAppId` is needed and missing, 첫 제출 시 `eas submit`이 인터랙티브 모드에서 자동으로 ASC 앱을 생성할 수 있습니다.

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
