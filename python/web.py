"""Playwright script using a saved login (storage state).

Best practice for auth with Playwright is to login once, save `storage_state.json`,
then reuse it for future runs. This avoids depending on your real Chrome profile.
"""
from __future__ import annotations

import os
import csv

from pathlib import Path
from typing import NamedTuple

from tqdm import tqdm  # type: ignore[import-untyped]
import re
from playwright.sync_api import (
    BrowserContext,
    Page,
    Download,
    sync_playwright,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

from const import (
    LEAGUES,
    PFF_LINK,
    NFL_WEEKS,
    NCAA_WEEKS,
    NCAA_ADD_ON,
    LEAGUE_YEARS,
    PFF_STAT_NAME,
)

STORAGE_STATE_PATH = Path(__file__).with_name("storage_state.json")


class LinkInfo(NamedTuple):
    """Information about the link to download the CSV from."""

    stat_type: str
    league: str
    year: int
    week: int



def ensure_logged_in(page: Page, context: BrowserContext, *, timeout_ms: int = 300_000) -> None:
    """Ensure we have a valid logged-in session; refresh storage state if needed.

    PFF sessions in `storage_state.json` can expire. If we detect we're on a login
    page, we give you time to log in interactively and then re-save storage state.
    """
    def looks_logged_out() -> bool:
        # Premium sometimes doesn't redirect to /login; it just shows a paywall banner.
        unlock_banner = page.get_by_text(re.compile(r"unlock\s+pff", re.I))
        if unlock_banner.is_visible():
            return True

        # Header typically shows a SIGN IN link/button when logged out.
        sign_in_btn = page.get_by_role("button", name=re.compile(r"^sign in$", re.I))
        sign_in_link = page.get_by_role("link", name=re.compile(r"^sign in$", re.I))
        return sign_in_btn.is_visible() or sign_in_link.is_visible()

    page.goto("https://premium.pff.com/", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    maybe_accept_cookies(page)

    if not looks_logged_out():
        return

    # Best-effort: click SIGN IN to bring up the auth flow.
    try:
        page.get_by_role("button", name=re.compile(r"^sign in$", re.I)).click(timeout=2000)
    except PlaywrightTimeoutError:
        try:
            page.get_by_role("link", name=re.compile(r"^sign in$", re.I)).click(timeout=2000)
        except PlaywrightTimeoutError:
            # Fall back to whatever page we're on; user can still sign in manually.
            pass

    print(
        "PFF session appears to be logged out (paywall / SIGN IN detected).\n"
        "Please complete sign-in in the opened browser window.\n"
        f"Waiting up to {timeout_ms/1000:.0f}s, then saving updated storage state..."
    )

    # Wait until paywall/sign-in affordances are gone.
    page.wait_for_function(
        """() => {
          const t = (document.body?.innerText || '').toLowerCase();
          if (t.includes('unlock pff')) return false;
          const signIn = Array.from(document.querySelectorAll('a,button'))
            .some(el => (el.textContent || '').trim().toLowerCase() === 'sign in');
          return !signIn;
        }""",
        timeout=timeout_ms,
    )

    context.storage_state(path=str(STORAGE_STATE_PATH))
    print(f"Updated storage state saved to: {STORAGE_STATE_PATH}")



def maybe_accept_cookies(page: Page) -> bool:
    """Best-effort cookie consent dismissal.

    PFF uses a cookie banner (e.g. "Accept All") that can block clicks.
    This helper tries to dismiss it without failing the run if it isn't present.
    """
    try:
        # Common consent CTA text.
        page.get_by_role("button", name="Accept All").click(timeout=1500)
        page.wait_for_timeout(250)
        return True
    except PlaywrightTimeoutError:
        return False



def retry_download(page: Page, link_info: LinkInfo, max_retries: int = 5) -> Download:
    """Click the CSV button and return the Playwright Download, retrying on timeout."""
    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            csv_btn = page.get_by_role("button", name="CSV")
            csv_btn.wait_for(state="visible", timeout=30000)
            csv_btn.scroll_into_view_if_needed()

            # CSV triggers a download; waiting for it makes this reliable.
            with page.expect_download(timeout=30000) as dl_info:
                csv_btn.click()

            return dl_info.value
        except PlaywrightTimeoutError as e:
            # Common failure: "Timeout ... waiting for event 'download'".
            last_err = e
            if attempt >= max_retries:
                raise
            print(
                f"Download timed out for {link_info.league} {link_info.year} "
                f"week {link_info.week} {link_info.stat_type} "
                f"(attempt {attempt}/{max_retries}). Reloading and retrying..."
            )
            page.reload(wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            maybe_accept_cookies(page)

    raise last_err if last_err is not None else RuntimeError("Unknown download error")



def download_csv(page: Page, link_info: LinkInfo, *, max_retries: int = 5) -> None:
    """Download the CSV from the link."""
    download = retry_download(page=page, link_info=link_info, max_retries=max_retries)

    # Save into repo `csv/` folder (csv/nfl or csv/ncaa).
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "csv" / link_info.league.lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = "temp.csv"
    out_path = out_dir / filename
    try:
        download.save_as(str(out_path))
    except PlaywrightError as e:
        # Intermittently Playwright reports: "Download.save_as: canceled"
        # This usually means the underlying download was aborted (navigation,
        # server-side cancellation, or transient browser issue). Retry the
        # click/download flow a few times before failing.
        if "canceled" not in str(e).lower():
            raise
        print(
            f"Download.save_as canceled for {link_info.league} {link_info.year} "
            f"week {link_info.week} {link_info.stat_type}. Retrying..."
        )
        download = retry_download(page=page, link_info=link_info, max_retries=max_retries)
        download.save_as(str(out_path))
    add_to_csv(link_info)



def add_to_csv(link_info: LinkInfo) -> None:
    """Adding data to the CSV file is not already created.
    If the file is not created, create it and add the header row.
    If the file is created, add the data to the file.
    """
    file_name = f"{link_info.league}-{link_info.year}-{link_info.stat_type}.csv"
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "csv" / link_info.league.lower()

    temp_data = out_dir / "temp.csv"

    out_path = out_dir / file_name
    file_exists = os.path.exists(out_path)
    tag = "w" if not file_exists else "a"

    with open(out_path, tag, encoding="utf-8") as data_file:
        writer = csv.writer(data_file)
        with open(temp_data, "r", encoding="utf-8") as temp_file:
            temp_reader = csv.reader(temp_file)

            for row in temp_reader:
                insert_data: str = "week" if "player" in row[0] else str(link_info.week)
                row.insert(0, insert_data)
                writer.writerow(row)

    os.remove(temp_data)



def calculate_total_downloads() -> int:
    """Calculate the total number of downloads needed."""
    total = 0
    for league in LEAGUES:
        start_year = LEAGUE_YEARS[league]["start_year"]
        end_year = LEAGUE_YEARS[league]["end_year"]
        weeks = NFL_WEEKS if league == "NFL" else NCAA_WEEKS
        total += (end_year - start_year + 1) * len(weeks) * len(PFF_STAT_NAME)

    return total



def main() -> None:
    """Main function to go and take all the premium data from PFF."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if STORAGE_STATE_PATH.exists():
            context = browser.new_context(
                storage_state=str(STORAGE_STATE_PATH),
                accept_downloads=True,
            )
        else:
            context = browser.new_context(accept_downloads=True)

        accept_cookies = False
        page = context.new_page()
        ensure_logged_in(page, context)
        total = calculate_total_downloads()

        with tqdm(total=total, desc="Downloading PFF CSVs", unit="csv") as pbar:
            for league in LEAGUES:
                link_template = PFF_LINK if league == "NFL" else PFF_LINK + NCAA_ADD_ON

                end_year = LEAGUE_YEARS[league]["end_year"]
                start_year = LEAGUE_YEARS[league]["start_year"]
                weeks = NFL_WEEKS if league == "NFL" else NCAA_WEEKS
                for year in range(start_year, end_year + 1):
                    for week in weeks:
                        for stat_type in PFF_STAT_NAME:
                            link = link_template.format(
                                league=league.lower(),
                                year=year,
                                stat_type=stat_type.lower(),
                                week=week,
                            )
                            page.goto(link, wait_until="domcontentloaded")
                            page.wait_for_load_state("networkidle")

                            if not accept_cookies:
                                accept_cookies = maybe_accept_cookies(page)

                            download_csv(
                                page=page,
                                link_info=LinkInfo(
                                    league=league,
                                    year=year,
                                    week=week,
                                    stat_type=stat_type,
                                ),
                            )
                            pbar.update(1)

        context.close()
        browser.close()
        return


if __name__ == "__main__":
    main()
