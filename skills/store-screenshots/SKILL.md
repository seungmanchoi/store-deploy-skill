---
name: store-screenshots
description: "Generate and process store screenshots for App Store and Google Play. Supports simulator capture, AI generation (nano-banana-mcp), and Pillow post-processing with text overlays."
argument-hint: "[ios|android|both] [--simulator|--ai|--process]"
---

## Step 1: Choose Approach

```
Screenshot approach?
  a) simulator  — Capture real app screens from iOS Simulator
  b) ai         — Generate marketing screenshots with nano-banana-mcp (Gemini)
  c) process    — Post-process only (resize/overlay existing screenshots)
```

Parse from `$ARGUMENTS` if `--simulator`, `--ai`, or `--process` flag present.

## Step 2a: Simulator Capture

1. Boot simulator:
```bash
xcrun simctl boot "iPhone 16 Pro Max" 2>/dev/null || true
open -a Simulator
```

2. Build and install:
```bash
npx expo run:ios --device "iPhone 16 Pro Max"
```

3. Capture screenshots for each key screen:
```bash
mkdir -p screenshots/ios
xcrun simctl io booted screenshot screenshots/ios/01_home.png
```

4. Ask developer to navigate to each screen, capture 4-6 screenshots.

5. For Android (if emulator running):
```bash
mkdir -p screenshots/android
adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png screenshots/android/01_home.png
```

## Step 2b: AI Generation (nano-banana-mcp)

1. Read app description from `app.json` or metadata files.
2. For each screen, use `generate_image` tool:

Prompt template:
```
iPhone 16 Pro Max screenshot of a {app_category} app showing {screen_description}.
Modern iOS UI, clean minimal design, {color_scheme} theme.
Full screen app UI, no device frame, 1290x2796 resolution.
```

3. Generate 4-6 images. Save to `screenshots/ios/` and `screenshots/android/`.

## Step 2c: Process Only

Skip generation, go directly to Step 3.

## Step 3: Post-Processing

### 3-1. Create config if missing

If `screenshots/config.json` doesn't exist, generate it from app metadata:

```json
{
  "texts": {
    "en-US": ["Track Your Calories", "Easy Food Log", "Beautiful Charts", "Set Goals"],
    "ko": ["칼로리 추적", "간편한 음식 기록", "아름다운 차트", "목표 설정"]
  },
  "fontSize": 56,
  "fontColor": "#FFFFFF",
  "overlayHeight": 200,
  "font": null
}
```

Write marketing-oriented text based on actual app features.

### 3-2. Run processor

```bash
python3 ${CLAUDE_SKILL_DIR}/../../scripts/process_screenshots.py --project . --platform both
```

This resizes to exact dimensions (iOS 1290×2796, Android 1080×1920) and adds text overlays.

## Step 4: Upload

**iOS:**
```bash
fastlane ios upload_screenshots
```

**Android:**
```bash
fastlane android upload_screenshots
```

## Step 5: Report

```
Screenshots Complete
====================
Processed: {count} images
iOS:     fastlane/screenshots/{langs}/
Android: fastlane/metadata/android/{langs}/images/phoneScreenshots/
Uploaded: {yes/no}
```
