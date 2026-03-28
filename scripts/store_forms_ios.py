#!/usr/bin/env python3
"""
App Store Connect Form Automation
Fills forms that fastlane/EAS cannot handle:
1. Age Rating
2. App Privacy
3. App Review Information
4. Export Compliance
5. IDFA Declaration

Usage:
  python3 store_forms_ios.py --app-id 123456789 --bundle-id com.example.app
  python3 store_forms_ios.py --app-id 123456789 --config forms_config.json
  python3 store_forms_ios.py --app-id 123456789 --dry-run
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from browser_base import BrowserSession, StepLogger
from credentials_manager import ensure_credentials, load_merged

ASC_BASE = "https://appstoreconnect.apple.com"


def load_forms_config(config_path: str = None, project_root: str = ".") -> dict:
    """Load form answers from config file or defaults."""
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            return json.load(f)

    # Try project-level store-deploy.json
    p = Path(project_root) / "store-deploy.json"
    if p.exists():
        with open(p) as f:
            data = json.load(f)
            return data.get("forms_ios", data.get("defaults", {}))

    return {}


async def fill_age_rating(browser: BrowserSession, app_id: str, config: dict, log: StepLogger):
    """
    Fill Age Rating questionnaire.
    Path: App > App Information > Age Rating > Edit
    """
    log.step("Age Rating")

    url = f"{ASC_BASE}/apps/{app_id}/appinfo"
    await browser.navigate(url)
    await asyncio.sleep(3)

    log.info("Navigating to Age Rating section...")

    # Click "Edit" next to Age Rating or find the Age Rating section
    clicked = await browser.click_text("Edit Age Rating", exact=False)
    if not clicked:
        clicked = await browser.click_text("Set Age Rating", exact=False)
    if not clicked:
        # Try clicking the Age Rating row to expand it
        clicked = await browser.click_text("Age Rating", exact=False)

    if not clicked:
        log.warn("Could not find Age Rating edit button")
        await browser.pause_for_manual("Navigate to Age Rating and click Edit")

    await asyncio.sleep(2)

    # Age rating questionnaire — for most utility/productivity apps, all answers are "None"
    # The questionnaire has categories like: Cartoon/Fantasy Violence, Realistic Violence, etc.
    # Each has options: None, Infrequent/Mild, Frequent/Intense
    has_violence = config.get("has_violence", False)
    has_sexual = config.get("has_sexual", False)
    has_profanity = config.get("has_profanity", False)
    has_drugs = config.get("has_drugs", False)
    has_gambling = config.get("has_gambling", False)
    has_horror = config.get("has_horror", False)
    has_ugc = config.get("has_ugc", False)

    # Try to select "None" for all categories by finding radio buttons
    none_options = await browser.page.get_by_text("None", exact=True).all()
    if none_options:
        log.info(f"Found {len(none_options)} 'None' options, selecting all...")
        for opt in none_options:
            try:
                await opt.click()
                await asyncio.sleep(0.3)
            except Exception:
                pass
        log.success("Selected 'None' for all categories")
    else:
        log.warn("Could not find 'None' radio buttons — UI may have changed")
        await browser.pause_for_manual("Select appropriate age rating options")

    # If app has UGC, check the unrestricted web access option
    if has_ugc:
        await browser.click_text("Unrestricted Web Access", exact=False)

    await asyncio.sleep(1)

    # Click Done / Save / Submit
    saved = await browser.click_role("button", "Done")
    if not saved:
        saved = await browser.click_role("button", "Save")
    if not saved:
        saved = await browser.click_role("button", "Submit")

    if saved:
        log.success("Age Rating saved")
    else:
        log.warn("Could not find Save button")
        await browser.pause_for_manual("Save age rating manually")


async def fill_app_privacy(browser: BrowserSession, app_id: str, config: dict, creds: dict, log: StepLogger):
    """
    Fill App Privacy declarations.
    Path: App > App Privacy
    """
    log.step("App Privacy")

    url = f"{ASC_BASE}/apps/{app_id}/privacy"
    await browser.navigate(url)
    await asyncio.sleep(3)

    privacy_url = config.get("privacy_url", creds.get("defaults", {}).get("privacy_url", ""))

    # Enter privacy policy URL
    if privacy_url:
        filled = await browser.wait_and_fill(
            'input[placeholder*="privacy"], input[name*="privacy"], input[type="url"]',
            privacy_url,
            "Privacy Policy URL"
        )
        if not filled:
            # Try by label
            try:
                el = browser.page.get_by_label("Privacy Policy URL", exact=False).first
                await el.fill(privacy_url)
                log.success(f"Privacy URL: {privacy_url}")
            except Exception:
                log.warn("Could not find privacy URL field")
                await browser.pause_for_manual(f"Enter privacy URL: {privacy_url}")

    # Data collection declarations
    has_ads = config.get("has_ads", creds.get("defaults", {}).get("has_ads", False))
    data_collection = config.get("data_collection", [])

    if not has_ads and not data_collection:
        # No data collection — try to click "No, we do not collect data"
        log.info("Declaring: No data collected")
        clicked = await browser.click_text("does not collect", exact=False)
        if not clicked:
            clicked = await browser.click_text("No,", exact=False)
        if not clicked:
            await browser.pause_for_manual("Select 'No data collected' option")
    else:
        log.info(f"Data collection types: {data_collection or ['ads/analytics']}")
        await browser.pause_for_manual(
            "Fill data collection declarations based on:\n"
            f"         Has ads: {has_ads}\n"
            f"         Data types: {data_collection}"
        )

    # Save
    saved = await browser.click_role("button", "Save")
    if not saved:
        saved = await browser.click_role("button", "Publish")
    if saved:
        log.success("App Privacy saved")


async def fill_review_info(browser: BrowserSession, app_id: str, config: dict, creds: dict, log: StepLogger):
    """
    Fill App Review Information.
    Path: App > Version > App Review Information
    """
    log.step("App Review Information")

    # Navigate to the app's current version page
    url = f"{ASC_BASE}/apps/{app_id}/appstore"
    await browser.navigate(url)
    await asyncio.sleep(3)

    contact = creds.get("contact", {})
    first_name = contact.get("first_name", "")
    last_name = contact.get("last_name", "")
    email = contact.get("email", "")
    phone = contact.get("phone", "")

    log.info(f"Contact: {first_name} {last_name} / {email}")

    # Scroll down to App Review Information section
    await browser.click_text("App Review Information", exact=False)
    await asyncio.sleep(1)

    # Fill contact fields
    fields = [
        ("First Name", first_name),
        ("Last Name", last_name),
        ("Email", email),
        ("Phone", phone),
    ]

    for label, value in fields:
        if not value:
            continue
        try:
            el = browser.page.get_by_label(label, exact=False).first
            await el.fill(value)
            log.success(f"{label}: {value}")
        except Exception:
            log.warn(f"Could not fill {label}")

    # Review notes
    notes = config.get("review_notes", "")
    if notes:
        try:
            el = browser.page.get_by_label("Notes", exact=False).first
            await el.fill(notes)
            log.success("Review notes filled")
        except Exception:
            pass

    # Save
    saved = await browser.click_role("button", "Save")
    if saved:
        log.success("Review info saved")
    else:
        await browser.pause_for_manual("Save review info manually")


async def fill_export_compliance(browser: BrowserSession, app_id: str, config: dict, log: StepLogger):
    """
    Fill Export Compliance.
    This is usually on the version submission page.
    """
    log.step("Export Compliance")

    has_encryption = config.get("has_encryption", False)

    url = f"{ASC_BASE}/apps/{app_id}/appstore"
    await browser.navigate(url)
    await asyncio.sleep(3)

    # Find export compliance section
    await browser.click_text("Export Compliance", exact=False)
    await asyncio.sleep(1)

    if not has_encryption:
        log.info("No encryption — selecting 'No'")
        # Select "No" for encryption usage
        clicked = await browser.click_text("No", exact=True)
        if not clicked:
            # Try radio/checkbox approach
            no_options = await browser.page.locator('input[type="radio"][value="false"], input[type="radio"][value="no"]').all()
            if no_options:
                await no_options[0].click()
                log.success("Selected: No encryption")
            else:
                await browser.pause_for_manual("Select 'No' for encryption")
    else:
        log.info("Has encryption — selecting standard exemption")
        await browser.pause_for_manual("Select appropriate encryption declaration")

    # Save
    saved = await browser.click_role("button", "Save")
    if not saved:
        saved = await browser.click_role("button", "Done")
    if saved:
        log.success("Export Compliance saved")


async def fill_idfa(browser: BrowserSession, app_id: str, config: dict, log: StepLogger):
    """
    Fill IDFA (Advertising Identifier) declaration.
    """
    log.step("IDFA Declaration")

    has_ads = config.get("has_ads", False)

    url = f"{ASC_BASE}/apps/{app_id}/appstore"
    await browser.navigate(url)
    await asyncio.sleep(3)

    # Find IDFA section
    await browser.click_text("Advertising Identifier", exact=False)
    await asyncio.sleep(1)

    if has_ads:
        log.info("App has ads — declaring IDFA usage")
        clicked = await browser.click_text("Yes", exact=True)
        if clicked:
            # Check "Serve advertisements" checkbox
            await browser.click_text("Serve advertisements", exact=False)
            log.success("IDFA: Yes, for serving ads")
        else:
            await browser.pause_for_manual("Declare IDFA for advertising")
    else:
        log.info("No ads — declaring no IDFA usage")
        clicked = await browser.click_text("No", exact=True)
        if clicked:
            log.success("IDFA: No")
        else:
            await browser.pause_for_manual("Select 'No' for IDFA")

    # Save
    saved = await browser.click_role("button", "Save")
    if not saved:
        saved = await browser.click_role("button", "Done")
    if saved:
        log.success("IDFA saved")


async def run(args):
    creds = ensure_credentials(args.project)
    config = load_forms_config(args.config, args.project)

    # Merge defaults from credentials
    defaults = creds.get("defaults", {})
    for k, v in defaults.items():
        if k not in config:
            config[k] = v

    app_id = args.app_id

    if args.dry_run:
        print("\n[DRY RUN] Would fill the following forms:")
        print(f"  App ID: {app_id}")
        print(f"  Config: {json.dumps(config, indent=2)}")
        print(f"  Contact: {creds.get('contact', {})}")
        return

    log = StepLogger("App Store Connect Forms")

    async with BrowserSession(headless=False, slow_mo=150) as browser:
        # Navigate to ASC and check login
        await browser.navigate(f"{ASC_BASE}/apps/{app_id}")
        await asyncio.sleep(3)

        # Check if we need to log in
        if "idmsa.apple.com" in browser.page.url or "signin" in browser.page.url.lower():
            log.warn("Not logged in to App Store Connect")
            await browser.wait_for_login("appstoreconnect.apple.com/apps", "App Store Connect")

        await asyncio.sleep(2)

        # Run each form
        steps = {
            "age_rating": (fill_age_rating, [browser, app_id, config, log]),
            "app_privacy": (fill_app_privacy, [browser, app_id, config, creds, log]),
            "review_info": (fill_review_info, [browser, app_id, config, creds, log]),
            "export_compliance": (fill_export_compliance, [browser, app_id, config, log]),
            "idfa": (fill_idfa, [browser, app_id, config, log]),
        }

        # Filter to requested forms
        selected = args.forms.split(",") if args.forms else list(steps.keys())

        for form_name in selected:
            if form_name in steps:
                func, func_args = steps[form_name]
                try:
                    await func(*func_args)
                except Exception as e:
                    log.error(f"{form_name} failed: {e}")
                    await browser.save_error_screenshot(f"ios_{form_name}")
                    await browser.pause_for_manual(f"Complete {form_name} manually")

        log.done()

    print("\niOS Store Forms — Complete")
    print("=" * 40)
    for form_name in selected:
        print(f"  [✓] {form_name.replace('_', ' ').title()}")
    print()


def main():
    parser = argparse.ArgumentParser(description="App Store Connect Form Automation")
    parser.add_argument("--app-id", required=True, help="App Store Connect App ID (numeric)")
    parser.add_argument("--bundle-id", help="Bundle identifier (for reference)")
    parser.add_argument("--config", help="Path to forms config JSON")
    parser.add_argument("--project", default=".", help="Project root directory")
    parser.add_argument("--forms", help="Comma-separated form names to fill (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without opening browser")
    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
