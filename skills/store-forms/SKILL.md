---
name: store-forms
description: "Fill App Store Connect and Google Play Console forms that cannot be automated via CLI: age rating, privacy policy, data safety, export compliance, IDFA, content rating, target audience. Uses Playwright MCP or agent-browser."
argument-hint: "[ios|android|both]"
disable-model-invocation: true
---

This skill fills store forms that fastlane/EAS cannot handle, using browser automation.

## Prerequisites

Ask the developer:
> "Please log into the following in your browser, then tell me when ready:
> - App Store Connect: https://appstoreconnect.apple.com
> - Google Play Console: https://play.google.com/console"

## Automation Strategy

**Try Playwright MCP first** (`mcp__playwright__browser_*`). If unavailable, fall back to **agent-browser CLI**.

For each form:
1. Navigate to the page
2. Snapshot to understand current state
3. Fill form fields based on app analysis
4. Confirm and save

## iOS Forms (App Store Connect)

### 1. Age Rating
- Navigate to App Information > Age Rating
- Answer questionnaire based on app features:
  - Check `package.json` for content-related dependencies
  - Most utility/productivity apps: "None" for all categories
  - Apps with UGC: select appropriate levels
- Submit ratings

### 2. App Privacy
- Navigate to App Privacy section
- Enter privacy policy URL (ask developer if not known)
- Analyze `package.json` for data collection:
  - AdMob/analytics SDKs → advertising/usage data
  - Local-only storage → minimal declarations
  - Network requests → check what data is transmitted
- Fill data type declarations

### 3. App Review Information
- Navigate to version's App Review section
- Fill: First Name: Seungman, Last Name: Choi, Email: blueng.choi@gmail.com
- If login required: ask developer for test credentials
- Add review notes if needed

### 4. Export Compliance
- Check `app.json` for `ITSAppUsesNonExemptEncryption`
- If not set / false: "No" for encryption
- If HTTPS only: select standard encryption exemption

### 5. IDFA Declaration
- Check `package.json` for ad SDKs (react-native-google-mobile-ads, expo-ads-admob)
- Ad SDKs found → declare IDFA for advertising
- No ad SDKs → no IDFA usage

## Android Forms (Google Play Console)

### 6. Content Rating (IARC)
- Navigate to Policy > Content rating
- Start IARC questionnaire
- Answer based on app content analysis (violence: none, sexual: none, language: none for most apps)
- Submit for rating

### 7. Data Safety
- Navigate to Policy > Data safety
- Analyze app dependencies and permissions
- Declare: data types collected, sharing, encryption, deletion options
- Fill form section by section

### 8. Target Audience & Content
- Navigate to Policy > Target audience
- Set "18 and over" for general apps (or as appropriate)
- Declare ad presence based on SDK analysis

### 9. Ads Declaration
- Check for AdMob/ad SDKs in package.json
- Found → "Yes, my app contains ads"
- Not found → "No"

## Report

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
