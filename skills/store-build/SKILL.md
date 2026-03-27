---
name: store-build
description: "Build Expo app for production using EAS Build. Supports local and cloud builds for iOS and Android."
argument-hint: "[ios|android|both] [--local]"
---

## Step 1: Pre-build Checks

1. Run `git status` — warn if uncommitted changes
2. Read `eas.json` — confirm `production` profile exists
3. Check version: read `app.json` for `version`, `buildNumber`, `versionCode`
4. If `eas.json` has `"autoIncrement": true`, inform it's automatic. Otherwise ask:
   > "Current: v{version} (iOS build {buildNumber}, Android code {versionCode}). Bump version? (y/n)"

## Step 2: Ask Build Type

```
Build type?
  1. cloud  — EAS cloud build (default, no local SDK needed)
  2. local  — EAS local build (requires Xcode / Android SDK)
```

Parse from `$ARGUMENTS` if `--local` flag present.

## Step 3: Execute Build

**iOS:**
```bash
eas build --platform ios --profile production
# or with --local flag:
eas build --local --platform ios --profile production
```

**Android:**
```bash
eas build --platform android --profile production
# or with --local flag:
eas build --local --platform android --profile production
```

For "both", launch two builds. Cloud builds can run in parallel.

## Step 4: Report

Note the build ID, dashboard URL, or local artifact path.

```
Build Complete
==============
iOS:    {build_id or file path}
Android: {build_id or file path}
Dashboard: https://expo.dev/accounts/{account}/builds
```
