---
name: store-setup
description: "Install deployment prerequisites and create fastlane directory structure for Expo apps. Use when setting up a new project for store deployment."
---

## Step 1: Check Prerequisites

Run each check and report:

```bash
eas --version 2>/dev/null || echo "MISSING"
fastlane --version 2>/dev/null | head -1 || echo "MISSING"
python3 -c "from PIL import Image; print('OK')" 2>/dev/null || echo "MISSING"
agent-browser --version 2>/dev/null || echo "MISSING"
xcrun simctl list devices 2>/dev/null | head -1 || echo "NO XCODE"
```

Install missing tools:
- EAS CLI: `npm install -g eas-cli` then `eas login`
- Fastlane: `brew install fastlane`
- Pillow: `pip3 install Pillow`
- agent-browser: `brew install agent-browser && agent-browser install`

## Step 2: Read App Config

Read `app.json` or `app.config.ts`. Extract `bundleIdentifier` as `{BUNDLE_ID}` and `package` as `{PACKAGE_NAME}`.

## Step 3: Create Fastlane Structure

### 3-1. Keys (symlinks)
```bash
mkdir -p fastlane/keys
ln -sf ~/works/common/AuthKey_6FD6879KFW.p8 fastlane/keys/AuthKey_6FD6879KFW.p8
ln -sf ~/works/common/works-488915-4f58ab8044c4.json fastlane/keys/play-store-service-account.json
```

### 3-2. Appfile
```ruby
app_identifier("{BUNDLE_ID}")
apple_id("blue_eng@hanmail.net")
itc_team_id("117885592")
team_id("6Y6T9LPHH3")
json_key_file("./fastlane/keys/play-store-service-account.json")
package_name("{PACKAGE_NAME}")
```

### 3-3. Fastfile
```ruby
default_platform(:ios)

platform :ios do
  desc "Upload metadata to App Store Connect"
  lane :upload_metadata do
    app_store_connect_api_key(
      key_id: "6FD6879KFW",
      issuer_id: "69a6de87-13e2-47e3-e053-5b8c7c11a4d1",
      key_filepath: "./fastlane/keys/AuthKey_6FD6879KFW.p8"
    )
    deliver(
      skip_binary_upload: true, skip_screenshots: true, force: true,
      metadata_path: "./fastlane/metadata",
      precheck_include_in_app_purchases: false,
      app_review_information: {
        first_name: "Seungman", last_name: "Choi",
        phone_number: "", email_address: "blueng.choi@gmail.com"
      }
    )
  end

  desc "Upload screenshots to App Store Connect"
  lane :upload_screenshots do
    app_store_connect_api_key(
      key_id: "6FD6879KFW",
      issuer_id: "69a6de87-13e2-47e3-e053-5b8c7c11a4d1",
      key_filepath: "./fastlane/keys/AuthKey_6FD6879KFW.p8"
    )
    deliver(
      skip_binary_upload: true, skip_metadata: true,
      overwrite_screenshots: true, force: true,
      screenshots_path: "./fastlane/screenshots",
      precheck_include_in_app_purchases: false
    )
  end

  desc "Upload all"
  lane :upload_all do
    app_store_connect_api_key(
      key_id: "6FD6879KFW",
      issuer_id: "69a6de87-13e2-47e3-e053-5b8c7c11a4d1",
      key_filepath: "./fastlane/keys/AuthKey_6FD6879KFW.p8"
    )
    deliver(
      skip_binary_upload: true, overwrite_screenshots: true, force: true,
      metadata_path: "./fastlane/metadata",
      screenshots_path: "./fastlane/screenshots",
      precheck_include_in_app_purchases: false,
      app_review_information: {
        first_name: "Seungman", last_name: "Choi",
        phone_number: "", email_address: "blueng.choi@gmail.com"
      }
    )
  end
end

platform :android do
  desc "Upload metadata to Google Play"
  lane :upload_metadata do
    upload_to_play_store(
      skip_upload_apk: true, skip_upload_aab: true,
      skip_upload_images: true, skip_upload_screenshots: true,
      metadata_path: "./fastlane/metadata/android"
    )
  end

  desc "Upload screenshots to Google Play"
  lane :upload_screenshots do
    upload_to_play_store(
      skip_upload_apk: true, skip_upload_aab: true, skip_upload_metadata: true,
      json_key: "./fastlane/keys/play-store-service-account.json",
      package_name: "{PACKAGE_NAME}",
      screenshots_path: "./fastlane/metadata/android"
    )
  end

  desc "Upload AAB to internal track"
  lane :internal do |options|
    upload_to_play_store(
      track: "internal", release_status: "draft", aab: options[:aab],
      skip_upload_apk: true, skip_upload_images: true, skip_upload_screenshots: true,
      json_key: "./fastlane/keys/play-store-service-account.json"
    )
  end

  desc "Upload AAB to production"
  lane :production do |options|
    upload_to_play_store(
      track: "production", aab: options[:aab],
      skip_upload_apk: true, skip_upload_images: true, skip_upload_screenshots: true,
      json_key: "./fastlane/keys/play-store-service-account.json"
    )
  end
end
```

### 3-4. Deliverfile
```ruby
app_identifier("{BUNDLE_ID}")
username("blue_eng@hanmail.net")
api_key_path("./fastlane/keys/AuthKey_6FD6879KFW.p8")
languages(["en-US", "ko"])
automatic_release(false)
```

### 3-5. Metadata Directories
```bash
mkdir -p fastlane/metadata/{en-US,ko}
mkdir -p fastlane/metadata/android/{en-US,ko-KR}/changelogs
mkdir -p fastlane/screenshots/{en-US,ko}
mkdir -p screenshots/{ios,android}
```

Create placeholder files (name.txt, subtitle.txt, description.txt, keywords.txt, promotional_text.txt, release_notes.txt, support_url.txt, marketing_url.txt) for each iOS language.

Create placeholder files (title.txt, short_description.txt, full_description.txt, changelogs/default.txt) for each Android language.

## Step 4: Update eas.json

If `eas.json` has no `submit` section, merge:
```json
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "blue_eng@hanmail.net",
        "ascApiKeyPath": "/Users/seungmanchoi/works/common/AuthKey_6FD6879KFW.p8",
        "ascApiKeyIssuerId": "69a6de87-13e2-47e3-e053-5b8c7c11a4d1",
        "ascApiKeyId": "6FD6879KFW"
      },
      "android": {
        "serviceAccountKeyPath": "./fastlane/keys/play-store-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

**IMPORTANT: `ascApiKeyPath`는 반드시 절대 경로를 사용해야 합니다.**
- `~/works/common/...` (X) — EAS CLI가 `~`를 resolve하지 못함
- `/Users/seungmanchoi/works/common/...` (O) — 절대 경로 사용

Ask developer for `ascAppId` if missing (첫 제출 시 EAS가 자동 생성 가능).

## Step 5: Report

```
Setup Complete
==============
- [x] Prerequisites installed
- [x] fastlane/ directory created
- [x] Credential symlinks configured
- [x] Metadata structure ready
- [x] eas.json submit profile configured
```
