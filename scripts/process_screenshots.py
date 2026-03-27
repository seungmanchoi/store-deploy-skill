#!/usr/bin/env python3
"""
Store Screenshot Processor
- Resizes screenshots to exact App Store / Google Play dimensions
- Adds localized text overlay at the top
- Reads config from screenshots/config.json
- Outputs to fastlane-compatible directory structure

Usage:
  python3 process_screenshots.py [--platform ios|android|both] [--source DIR] [--config PATH]
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip3 install Pillow")
    sys.exit(1)

# Store screenshot dimensions
SIZES = {
    "ios_67": {"name": "iPhone 6.7\"", "width": 1290, "height": 2796},
    "ios_65": {"name": "iPhone 6.5\"", "width": 1242, "height": 2688},
    "ios_55": {"name": "iPhone 5.5\"", "width": 1242, "height": 2208},
    "android_phone": {"name": "Android Phone", "width": 1080, "height": 1920},
}

DEFAULT_CONFIG = {
    "texts": {
        "en-US": [],
        "ko": []
    },
    "fontSize": 56,
    "fontColor": "#FFFFFF",
    "overlayHeight": 200,
    "overlayColor": "rgba(0,0,0,0.6)",
    "font": None
}

FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def find_font(config_font=None, size=56):
    """Find a usable font."""
    if config_font and os.path.exists(config_font):
        return ImageFont.truetype(config_font, size)

    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue

    return ImageFont.load_default()


def add_text_overlay(img, text, config):
    """Add text overlay at the top of the image."""
    if not text:
        return img

    draw = ImageDraw.Draw(img)
    w, h = img.size
    font_size = config.get("fontSize", 56)
    font = find_font(config.get("font"), font_size)
    overlay_h = config.get("overlayHeight", 200)

    # Semi-transparent overlay background
    overlay = Image.new("RGBA", (w, overlay_h), (0, 0, 0, 160))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img.paste(overlay, (0, 0), overlay)

    # Draw text centered
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = (overlay_h - th) // 2
    draw.text((x, y), text, fill=config.get("fontColor", "#FFFFFF"), font=font)

    return img.convert("RGB")


def process_platform(platform_key, source_dir, config, project_root):
    """Process screenshots for a specific platform and size."""
    size_info = SIZES[platform_key]
    w, h = size_info["width"], size_info["height"]
    is_ios = platform_key.startswith("ios")

    source = Path(source_dir)
    if not source.exists():
        print(f"  [!] Source directory not found: {source}")
        return 0

    images = sorted([
        f for f in source.iterdir()
        if f.suffix.lower() in (".png", ".jpg", ".jpeg")
    ])

    if not images:
        print(f"  [!] No images found in {source}")
        return 0

    processed = 0
    texts = config.get("texts", {})

    for lang, lang_texts in texts.items():
        if is_ios:
            # fastlane deliver format: fastlane/screenshots/{lang}/
            out_dir = project_root / "fastlane" / "screenshots" / lang
        else:
            # fastlane supply format
            out_dir = project_root / "fastlane" / "metadata" / "android" / lang / "images" / "phoneScreenshots"

        out_dir.mkdir(parents=True, exist_ok=True)

        for i, img_path in enumerate(images):
            img = Image.open(img_path)

            # Resize to exact dimensions
            img = img.resize((w, h), Image.LANCZOS)

            # Add text overlay
            text = lang_texts[i] if i < len(lang_texts) else ""
            if text:
                img = add_text_overlay(img, text, config)

            # Save with sequential naming
            out_name = f"{i + 1:02d}_{img_path.stem}.png"
            out_path = out_dir / out_name

            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(out_path, "PNG")
            processed += 1
            print(f"  [{lang}] {out_name} → {w}x{h}")

    # If no texts/langs configured, process without overlay
    if not texts:
        if is_ios:
            out_dir = project_root / "fastlane" / "screenshots" / "en-US"
        else:
            out_dir = project_root / "fastlane" / "metadata" / "android" / "en-US" / "images" / "phoneScreenshots"

        out_dir.mkdir(parents=True, exist_ok=True)

        for i, img_path in enumerate(images):
            img = Image.open(img_path)
            img = img.resize((w, h), Image.LANCZOS)
            out_name = f"{i + 1:02d}_{img_path.stem}.png"
            out_path = out_dir / out_name
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(out_path, "PNG")
            processed += 1
            print(f"  [en-US] {out_name} → {w}x{h}")

    return processed


def main():
    parser = argparse.ArgumentParser(description="Process store screenshots")
    parser.add_argument("--platform", choices=["ios", "android", "both"], default="both")
    parser.add_argument("--source-ios", default="screenshots/ios", help="iOS source directory")
    parser.add_argument("--source-android", default="screenshots/android", help="Android source directory")
    parser.add_argument("--config", default="screenshots/config.json", help="Config file path")
    parser.add_argument("--project", default=".", help="Project root directory")
    args = parser.parse_args()

    project_root = Path(args.project).resolve()

    # Load config
    config_path = project_root / args.config
    if config_path.exists():
        with open(config_path) as f:
            config = {**DEFAULT_CONFIG, **json.load(f)}
        print(f"[✓] Loaded config from {config_path}")
    else:
        config = DEFAULT_CONFIG.copy()
        print(f"[!] No config found at {config_path}, using defaults (no text overlay)")

    total = 0

    if args.platform in ("ios", "both"):
        print(f"\n=== iOS Screenshots (1290×2796 - iPhone 6.7\") ===")
        source = project_root / args.source_ios
        total += process_platform("ios_67", source, config, project_root)

    if args.platform in ("android", "both"):
        print(f"\n=== Android Screenshots (1080×1920) ===")
        source = project_root / args.source_android
        total += process_platform("android_phone", source, config, project_root)

    print(f"\n[✓] Processed {total} screenshots total")

    if total > 0:
        print(f"\nOutput directories:")
        if args.platform in ("ios", "both"):
            print(f"  iOS:     {project_root}/fastlane/screenshots/")
        if args.platform in ("android", "both"):
            print(f"  Android: {project_root}/fastlane/metadata/android/*/images/phoneScreenshots/")


if __name__ == "__main__":
    main()
