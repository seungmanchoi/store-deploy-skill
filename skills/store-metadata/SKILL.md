---
name: store-metadata
description: "Generate and upload store metadata (title, description, keywords, release notes) for App Store and Google Play in multiple languages."
argument-hint: "[ios|android|both]"
---

## Step 1: Read Existing Metadata

Check `fastlane/metadata/` for existing files. Read app.json for app info.

## Step 2: Generate Metadata

Generate compelling, store-optimized metadata in all configured languages (minimum: en-US, ko).

### iOS (fastlane/metadata/{lang}/)

| File | Max Length | Content |
|------|-----------|---------|
| `name.txt` | 30 chars | App name |
| `subtitle.txt` | 30 chars | Short tagline |
| `description.txt` | 4000 chars | Full description with features, benefits |
| `keywords.txt` | 100 chars | Comma-separated, no spaces after commas |
| `promotional_text.txt` | 170 chars | Current promotion or highlight |
| `release_notes.txt` | 4000 chars | What's new in this version |
| `support_url.txt` | - | Support URL |
| `marketing_url.txt` | - | Optional marketing URL |

### Android (fastlane/metadata/android/{lang}/)

| File | Max Length | Content |
|------|-----------|---------|
| `title.txt` | 30 chars | App title |
| `short_description.txt` | 80 chars | Brief description |
| `full_description.txt` | 4000 chars | Full description |
| `changelogs/default.txt` | 500 chars | Release notes |

**Write actual content, not placeholders.** Use the app's features and purpose to create compelling copy.

For Korean (`ko` / `ko-KR`), write natural Korean — not machine-translated.

## Step 3: Upload

**iOS:**
```bash
fastlane ios upload_metadata
```

**Android:**
```bash
fastlane android upload_metadata
```

Note: Google Play requires at least one AAB upload before metadata. If upload fails with "app not found", inform the user to run `/store-submit` first.

## Step 4: Report

```
Metadata Complete
=================
Languages: en-US, ko
iOS:     fastlane ios upload_metadata ✓
Android: fastlane android upload_metadata ✓
```
