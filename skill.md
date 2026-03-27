---
name: store-deploy
description: "Full App Store/Google Play publisher for Expo apps. Use when deploying apps to stores, generating screenshots, uploading metadata, filling store forms, or setting up AdMob. Handles the entire pipeline: EAS build, screenshot generation, metadata, store form submission, and binary upload."
argument-hint: "[action] [platform]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

You are an expert mobile app publisher that automates the entire pipeline from Expo app to live store listing. You handle builds, screenshots, metadata, store forms, AdMob setup, and binary submission.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-03-27 | Full rewrite: 9 actions (setup, build, screenshots, metadata, store-forms, submit, admob, full, status). Added simulator/AI screenshot generation with Pillow post-processing (resize + text overlay). Added Playwright MCP browser automation for store forms (age rating, privacy, data safety, export compliance, IDFA). Added AdMob app creation and ad unit setup. Added agent-browser support. Migrated to SKILL.md format with frontmatter. Added scripts/process_screenshots.py. Credential management via fastlane/keys/ symlinks. |
| 1.0.0 | 2026-03-26 | Initial release: 5 actions (build, submit, metadata, screenshots, full). Basic EAS + Fastlane integration. |

## Step 1: Detect the current project

Read `app.json` or `app.config.ts` in the current working directory to extract:
- `name` — the app display name
- `slug` — the app slug
- `expo.ios.bundleIdentifier` — iOS bundle ID
- `expo.android.package` — Android package name
- `expo.version` — app version
- `expo.ios.buildNumber` — iOS build number
- `expo.android.versionCode` — Android version code

Also read `eas.json` to confirm build/submit profiles exist.

If `app.json` is not found, stop and tell the developer:
> "No app.json found. Please run this command from the root of your Expo project."

For `app.config.ts`, parse with:
```bash
node -e "const c = require('./app.config.ts').default || require('./app.config.ts'); console.log(JSON.stringify(c, null, 2))"
```

## Step 2: Present menu and ask the developer

Present detected project info and ask:

```
Detected app: {name}
  iOS: {bundleIdentifier}
  Android: {package}
  Version: {version}

Which action? (type number or name)
  1. setup        — Install prerequisites & setup fastlane
  2. build        — EAS build (local or cloud)
  3. screenshots  — Generate & process store screenshots
  4. metadata     — Generate & upload store metadata
  5. store-forms  — Fill store forms via browser (age rating, privacy, etc.)
  6. submit       — Upload binary via EAS Submit
  7. admob        — Set up AdMob app & ad units
  8. full         — Full pipeline (1→6 in sequence)
  9. status       — Check current deployment status
```

If `$ARGUMENTS` is provided, use it to select the action directly. Examples:
- `$ARGUMENTS` = "screenshots" → run screenshots action
- `$ARGUMENTS` = "build ios" → run build for iOS
- `$ARGUMENTS` = "full" → run full pipeline
- `$ARGUMENTS` = "3" → run screenshots action

Wait for the developer's response before proceeding (unless arguments already specify the action).

Also ask **platform** if not specified in arguments:
```
Which platform?
  1. ios
  2. android
  3. both
```

## Step 3: Action — setup

### 3-1. Check prerequisites

Run these checks and report results:

```bash
eas --version 2>/dev/null || echo "NOT INSTALLED"
fastlane --version 2>/dev/null | head -1 || echo "NOT INSTALLED"
python3 -c "from PIL import Image; print('Pillow OK')" 2>/dev/null || echo "NOT INSTALLED"
agent-browser --version 2>/dev/null || echo "NOT INSTALLED"
```

For any missing tool, offer to install:
- EAS CLI: `npm install -g eas-cli`
- Fastlane: `brew install fastlane`
- Pillow: `pip3 install Pillow`
- agent-browser: `brew install agent-browser && agent-browser install`

After installation, run `eas login` if not already logged in.

### 3-2. Create fastlane directory structure

If `fastlane/` does not exist, create it with the following structure. Replace `{BUNDLE_ID}` and `{PACKAGE_NAME}` with actual values from `app.json`.

#### fastlane/keys/ (symlinks)

```bash
mkdir -p fastlane/keys
ln -sf ~/works/common/AuthKey_6FD6879KFW.p8 fastlane/keys/AuthKey_6FD6879KFW.p8
ln -sf ~/works/common/works-488915-4f58ab8044c4.json fastlane/keys/play-store-service-account.json
```

#### fastlane/Appfile

```ruby
app_identifier("{BUNDLE_ID}")
apple_id("blue_eng@hanmail.net")
itc_team_id("117885592")
team_id("6Y6T9LPHH3")

# Android
json_key_file("./fastlane/keys/play-store-service-account.json")
package_name("{PACKAGE_NAME}")
```

#### fastlane/Fastfile

Use this exact pattern (from the emotion-journal reference):

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
      skip_binary_upload: true,
      skip_screenshots: true,
      force: true,
      metadata_path: "./fastlane/metadata",
      precheck_include_in_app_purchases: false,
      app_review_information: {
        first_name: "Seungman",
        last_name: "Choi",
        phone_number: "",
        email_address: "blueng.choi@gmail.com"
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
      skip_binary_upload: true,
      skip_metadata: true,
      skip_screenshots: false,
      overwrite_screenshots: true,
      force: true,
      screenshots_path: "./fastlane/screenshots",
      precheck_include_in_app_purchases: false
    )
  end

  desc "Upload metadata and screenshots"
  lane :upload_all do
    app_store_connect_api_key(
      key_id: "6FD6879KFW",
      issuer_id: "69a6de87-13e2-47e3-e053-5b8c7c11a4d1",
      key_filepath: "./fastlane/keys/AuthKey_6FD6879KFW.p8"
    )

    deliver(
      skip_binary_upload: true,
      skip_screenshots: false,
      overwrite_screenshots: true,
      force: true,
      metadata_path: "./fastlane/metadata",
      screenshots_path: "./fastlane/screenshots",
      precheck_include_in_app_purchases: false,
      app_review_information: {
        first_name: "Seungman",
        last_name: "Choi",
        phone_number: "",
        email_address: "blueng.choi@gmail.com"
      }
    )
  end
end

platform :android do
  desc "Upload metadata to Google Play"
  lane :upload_metadata do
    upload_to_play_store(
      skip_upload_apk: true,
      skip_upload_aab: true,
      skip_upload_images: true,
      skip_upload_screenshots: true,
      metadata_path: "./fastlane/metadata/android"
    )
  end

  desc "Upload screenshots to Google Play"
  lane :upload_screenshots do
    upload_to_play_store(
      skip_upload_apk: true,
      skip_upload_aab: true,
      skip_upload_metadata: true,
      json_key: "./fastlane/keys/play-store-service-account.json",
      package_name: "{PACKAGE_NAME}",
      screenshots_path: "./fastlane/metadata/android"
    )
  end

  desc "Upload AAB to internal track"
  lane :internal do |options|
    upload_to_play_store(
      track: "internal",
      release_status: "draft",
      aab: options[:aab],
      skip_upload_apk: true,
      skip_upload_images: true,
      skip_upload_screenshots: true,
      json_key: "./fastlane/keys/play-store-service-account.json"
    )
  end

  desc "Upload AAB to production track"
  lane :production do |options|
    upload_to_play_store(
      track: "production",
      aab: options[:aab],
      skip_upload_apk: true,
      skip_upload_images: true,
      skip_upload_screenshots: true,
      json_key: "./fastlane/keys/play-store-service-account.json"
    )
  end
end
```

#### fastlane/Deliverfile

```ruby
app_identifier("{BUNDLE_ID}")
username("blue_eng@hanmail.net")
api_key_path("./fastlane/keys/AuthKey_6FD6879KFW.p8")
languages(["en-US", "ko"])
automatic_release(false)
```

#### Metadata directory structure

Create these directories and placeholder files:

```
fastlane/metadata/
  en-US/
    name.txt, subtitle.txt, description.txt, keywords.txt,
    promotional_text.txt, release_notes.txt, support_url.txt, marketing_url.txt
  ko/
    name.txt, subtitle.txt, description.txt, keywords.txt,
    promotional_text.txt, release_notes.txt, support_url.txt, marketing_url.txt
  android/
    en-US/
      title.txt, short_description.txt, full_description.txt,
      changelogs/default.txt
    ko-KR/
      title.txt, short_description.txt, full_description.txt,
      changelogs/default.txt
```

Populate `name.txt` / `title.txt` with the app name from `app.json`.

### 3-3. Update eas.json

If `eas.json` does not have a `submit` section, add it:

```json
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "blue_eng@hanmail.net",
        "ascAppId": "ASK_DEVELOPER",
        "appleTeamId": "6Y6T9LPHH3"
      },
      "android": {
        "serviceAccountKeyPath": "./fastlane/keys/play-store-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

Ask the developer for the `ascAppId` (numeric App Store app ID) if it says "ASK_DEVELOPER".

### 3-4. Create screenshot directories

```bash
mkdir -p screenshots/ios screenshots/android
```

## Step 4: Action — build

### Pre-build checklist

1. **Git status**: Run `git status`. Warn if there are uncommitted changes.
2. **Version bump**: Ask if the developer wants to increment:
   - `expo.ios.buildNumber` in `app.json`
   - `expo.android.versionCode` in `app.json`
   - If `eas.json` has `"autoIncrement": true`, inform the developer it's automatic.
3. **Build type**: Ask:
   ```
   Build type?
     1. cloud  — EAS cloud build (default)
     2. local  — EAS local build (requires Xcode/Android SDK)
   ```

### Execute build

**iOS:**
```bash
# Cloud build
eas build --platform ios --profile production

# Local build
eas build --local --platform ios --profile production
```

**Android:**
```bash
# Cloud build
eas build --platform android --profile production

# Local build
eas build --local --platform android --profile production
```

After the build starts, note the build ID and EAS dashboard URL. For local builds, note the output file path (IPA/AAB).

## Step 5: Action — screenshots

Present sub-menu:
```
Screenshot approach?
  a) simulator  — Capture real app screens from iOS simulator
  b) ai         — Generate marketing screenshots with AI (nano-banana-mcp)
  c) process    — Post-process only (resize/overlay existing screenshots)
```

### Approach (a): Simulator-based

1. Boot the simulator:
```bash
xcrun simctl boot "iPhone 16 Pro Max" 2>/dev/null || true
open -a Simulator
```

2. Build and install the app:
```bash
npx expo run:ios --device "iPhone 16 Pro Max"
```

3. Wait for the app to launch, then capture screenshots:
```bash
mkdir -p screenshots/ios
xcrun simctl io booted screenshot screenshots/ios/01_home.png
```

4. Ask the developer to navigate to each key screen, then repeat capture:
```bash
xcrun simctl io booted screenshot screenshots/ios/02_detail.png
xcrun simctl io booted screenshot screenshots/ios/03_settings.png
```

Capture 4-6 screenshots covering the app's main features.

5. For Android, if an emulator is running:
```bash
mkdir -p screenshots/android
adb shell screencap -p /sdcard/screenshot.png && adb pull /sdcard/screenshot.png screenshots/android/01_home.png
```

### Approach (b): AI-generated (nano-banana-mcp)

1. Read the app description from `app.json` or metadata files.
2. Use the nano-banana-mcp `generate_image` tool to create marketing screenshots:

For each screen, generate with a prompt like:
```
iPhone 16 Pro Max screenshot of a {app_category} app showing {screen_description}.
Modern iOS UI design, clean layout, {app_color_scheme} color scheme.
Resolution: 1290x2796 pixels, portrait orientation.
```

Generate 4-6 screenshots per platform. Save raw outputs to `screenshots/ios/` and `screenshots/android/`.

### Approach (c): Post-process only

Skip generation, proceed directly to post-processing.

### Post-processing (all approaches)

1. If `screenshots/config.json` does not exist, generate it based on the app's metadata:

```json
{
  "texts": {
    "en-US": ["Feature 1 Title", "Feature 2 Title", "Feature 3 Title", "Feature 4 Title"],
    "ko": ["기능 1 제목", "기능 2 제목", "기능 3 제목", "기능 4 제목"]
  },
  "fontSize": 56,
  "fontColor": "#FFFFFF",
  "overlayHeight": 200
}
```

Generate meaningful, marketing-oriented text for each screenshot based on the app's features.

2. Run the screenshot processor:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/process_screenshots.py --project . --platform both
```

This resizes all screenshots to exact store dimensions and adds text overlays:
- iOS 6.7": 1290×2796
- Android: 1080×1920

3. Upload screenshots via fastlane:

**iOS:**
```bash
fastlane ios upload_screenshots
```

**Android:**
```bash
fastlane android upload_screenshots
```

## Step 6: Action — metadata

### Generate metadata

Using the app's `app.json`, existing metadata files, and your knowledge, generate store metadata in all configured languages (minimum: en-US, ko).

#### iOS metadata files (fastlane/metadata/{lang}/)

| File | Constraints |
|------|-------------|
| `name.txt` | App name (max 30 chars) |
| `subtitle.txt` | App subtitle (max 30 chars) |
| `description.txt` | Full description (max 4000 chars) |
| `keywords.txt` | Comma-separated keywords (max 100 chars total) |
| `promotional_text.txt` | Promotional text (max 170 chars) |
| `release_notes.txt` | What's new in this version |
| `support_url.txt` | Support URL |
| `marketing_url.txt` | Marketing URL (optional) |

#### Android metadata files (fastlane/metadata/android/{lang}/)

| File | Constraints |
|------|-------------|
| `title.txt` | App title (max 30 chars) |
| `short_description.txt` | Short description (max 80 chars) |
| `full_description.txt` | Full description (max 4000 chars) |
| `changelogs/default.txt` | Release notes (max 500 chars) |

**Important**: Write each file with the actual metadata content, not placeholder text. Use your knowledge of the app to create compelling, store-optimized copy.

### Upload metadata

**iOS:**
```bash
fastlane ios upload_metadata
```

**Android:**
```bash
fastlane android upload_metadata
```

## Step 7: Action — store-forms

This action uses Playwright MCP tools to fill store forms that fastlane cannot handle.

**Pre-requisite**: The developer must be logged into App Store Connect / Google Play Console in a browser. Ask:
> "Please log into App Store Connect (https://appstoreconnect.apple.com) and Google Play Console (https://play.google.com/console) in your browser, then tell me when ready."

### iOS Store Forms (App Store Connect)

For each section, use Playwright MCP tools:

#### 7-1. Age Rating

1. Navigate to the app's "App Information" > "Age Rating" in ASC
2. Use `mcp__playwright__browser_navigate` to go to the rating page
3. Take a `mcp__playwright__browser_snapshot` to understand the current form state
4. Answer the questionnaire based on the app's features:
   - For most utility/productivity apps: select "None" for all violent/sexual content
   - For apps with user-generated content: select appropriate levels
   - For apps with in-app purchases: mark accordingly
5. Submit the form using `mcp__playwright__browser_click`

#### 7-2. Privacy Policy & App Privacy

1. Navigate to "App Privacy" section
2. Enter privacy policy URL
3. For data collection declarations:
   - Check `package.json` dependencies for analytics/tracking SDKs
   - If app uses AdMob → declares advertising data collection
   - If app uses analytics → declares usage data collection
   - If app stores user data locally only → minimal declarations
4. Fill each data type form as appropriate

#### 7-3. App Review Information

1. Navigate to the version's "App Review" section
2. Fill contact information:
   - First Name: Seungman
   - Last Name: Choi
   - Email: blueng.choi@gmail.com
3. If the app requires a login, ask the developer for test credentials
4. Add review notes if needed

#### 7-4. Export Compliance

1. Check `app.json` for `ITSAppUsesNonExemptEncryption`
2. If not set or false: select "No" for encryption usage
3. If true or app uses HTTPS only: select appropriate exemption

#### 7-5. IDFA Declaration

1. Check `package.json` for ad SDK dependencies (react-native-google-mobile-ads, expo-ads-admob, etc.)
2. If ad SDKs found: declare IDFA usage for advertising
3. If no ad SDKs: declare no IDFA usage

### Android Store Forms (Google Play Console)

#### 7-6. Content Rating

1. Navigate to Play Console > Policy > Content rating
2. Start the IARC questionnaire
3. Answer based on app content:
   - Violence: None for most apps
   - Sexual content: None for most apps
   - Language: None for most apps
   - Controlled substance: None for most apps
   - COPPA: select "Not designed for children" unless it is
4. Submit to receive the IARC rating

#### 7-7. Data Safety

1. Navigate to Policy > Data safety
2. Based on the app's dependencies and functionality:
   - Declare what data types are collected
   - Declare if data is shared with third parties
   - Declare data encryption status
   - Declare data deletion options
3. Fill the form section by section

#### 7-8. Target Audience & Content

1. Navigate to Policy > Target audience
2. Set target age group (typically "18 and over" for general apps)
3. Declare if app contains ads

#### 7-9. Ads Declaration

1. If app contains AdMob or other ad SDKs: select "Yes, my app contains ads"
2. Otherwise: select "No"

## Step 8: Action — submit

### Submit binary

**iOS:**
```bash
eas submit --platform ios --profile production
```

If prompted for `ascAppId`, ask the developer.

**Android:**
```bash
eas submit --platform android --profile production
```

### After submission

Upload metadata and screenshots if not already done:
```bash
# iOS
fastlane ios upload_all

# Android
fastlane android upload_metadata
fastlane android upload_screenshots
```

Report the submission status with links:
```
Submission Summary
==================
App: {name}
Version: {version}

iOS:
- [x] Binary submitted to App Store Connect
- [x] Metadata uploaded
- [x] Screenshots uploaded
- Next: https://appstoreconnect.apple.com

Android:
- [x] AAB submitted to Google Play Console
- [x] Metadata uploaded
- [x] Screenshots uploaded
- Next: https://play.google.com/console
```

## Step 9: Action — admob

This action sets up AdMob for the app using browser automation.

### Pre-requisite
Ask the developer to log into AdMob: https://apps.admob.com

### Setup flow

1. Navigate to AdMob console using Playwright MCP:
```
mcp__playwright__browser_navigate to https://apps.admob.com/v2/home
```

2. Take a snapshot to check current state:
```
mcp__playwright__browser_snapshot
```

3. **Create new app** (if not exists):
   - Click "Add app" or "Apps" > "Add app"
   - Select platform (iOS or Android)
   - Choose "No, it's not listed on a supported app store" if the app is new
   - Enter app name from `app.json`
   - Complete creation

4. **Create ad units** for each type the developer wants:
   - **Banner**: Navigate to Ad Units > Add ad unit > Banner
     - Name: `{app_name}_banner`
     - Save and copy the ad unit ID
   - **Interstitial**: Add ad unit > Interstitial
     - Name: `{app_name}_interstitial`
     - Save and copy the ad unit ID
   - **Rewarded**: Add ad unit > Rewarded
     - Name: `{app_name}_rewarded`
     - Save and copy the ad unit ID

5. **Save ad unit IDs** to the project:

Create or update a config file (e.g., `src/shared/config/admob.ts`):
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

Or add to `app.json` extras:
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

6. Report the created ad unit IDs to the developer.

## Step 10: Action — full (Full Pipeline)

Execute the full pipeline in sequence with confirmation between major steps:

```
Full Pipeline
=============
1. [setup]       — Verify prerequisites, create fastlane structure
2. [build]       — EAS build
3. [screenshots] — Generate/process screenshots
4. [metadata]    — Generate and upload metadata
5. [submit]      — Upload binary to store
6. [store-forms] — Fill store forms via browser
7. [summary]     — Final status report
```

Between each step:
1. Report results of the completed step
2. Ask: "Continue to next step? (y/n)"
3. If "n", stop and report what was completed

At the end, provide a comprehensive summary:

```
Full Pipeline Complete
======================
App: {name} v{version}

Completed:
- [x] Prerequisites verified
- [x] Fastlane configured
- [x] iOS build: {build_id}
- [x] Android build: {build_id}
- [x] Screenshots: {count} generated and uploaded
- [x] Metadata: uploaded for {languages}
- [x] Binary: submitted to both stores
- [x] Store forms: age rating, privacy, etc.

Next steps:
- iOS: Review and submit for review at https://appstoreconnect.apple.com
- Android: Review and publish at https://play.google.com/console
```

## Step 11: Action — status

Check current deployment status:

1. Run `eas build:list --limit 5` to show recent builds
2. Check if fastlane metadata exists: `ls fastlane/metadata/`
3. Check if screenshots exist: `ls fastlane/screenshots/` and `ls screenshots/`
4. Check `eas.json` submit configuration
5. Report a status summary

## Important Notes

- **API Keys**: Never log or display the contents of API key files. Reference them by path only.
- **Build profiles**: Always use `production` profile unless the developer specifies otherwise.
- **EAS login**: If EAS commands fail with authentication errors, ask the developer to run `eas login`.
- **Fastlane auth**: Use App Store Connect API key (already configured), not password-based auth.
- **Version bumping**: Before a full pipeline run, ask about version/build number changes.
- **Git status**: Before builds, remind the developer to commit all changes.
- **Google Play ordering**: Google Play requires at least one AAB upload before metadata can be submitted. Run `submit` before `metadata` for new apps.
- **Browser login**: For `store-forms` and `admob` actions, the developer must be logged into the respective console in a browser first.
- **Screenshot dimensions**: iOS requires EXACT dimensions (1290×2796 for 6.7"). The post-processing script handles this automatically.

## Credential Reference (read-only, do not modify)

| Key | Value |
|-----|-------|
| iOS API Key Path | `./fastlane/keys/AuthKey_6FD6879KFW.p8` |
| iOS Key ID | `6FD6879KFW` |
| iOS Issuer ID | `69a6de87-13e2-47e3-e053-5b8c7c11a4d1` |
| iOS Apple ID | `blue_eng@hanmail.net` |
| iOS Team ID | `6Y6T9LPHH3` |
| iOS ITC Team ID | `117885592` |
| Android Service Account JSON | `./fastlane/keys/play-store-service-account.json` |
| Android Service Account Email | `play-store-deploy@works-488915.iam.gserviceaccount.com` |
| App Review Contact | Seungman Choi / blueng.choi@gmail.com |
