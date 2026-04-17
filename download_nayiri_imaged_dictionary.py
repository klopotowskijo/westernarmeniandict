#!/usr/bin/env python3

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path


BASE_URL = "http://www.nayiri.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TOTAL_PAGES_RE = re.compile(r"Բովանդակութիւն\s*/\s*(\d+)")
TOC_LINK_RE = re.compile(r"<a[^>]+href=\"([^\"]*pageNumber=(\d+)[^\"]*)\"[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
IMAGE_RE = re.compile(r'id="pageImage"[^>]+src="([^"]+)"', re.IGNORECASE)


def clean_text(value):
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def create_opener():
    cookie_jar = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))


def fetch_text(opener, url, referer=None):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(url, headers=headers)
    with opener.open(request) as response:
        return response.read().decode("utf-8", "ignore")


def fetch_binary(opener, url, referer=None):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(url, headers=headers)
    with opener.open(request) as response:
        return response.read()


def parse_title(html_text):
    match = TITLE_RE.search(html_text)
    return clean_text(match.group(1)) if match else ""


def parse_total_pages(html_text):
    match = TOTAL_PAGES_RE.search(html_text)
    return int(match.group(1)) if match else None


def parse_toc_entries(html_text):
    entries = []
    seen = set()
    for href, page_number, label_html in TOC_LINK_RE.findall(html_text):
        label = clean_text(label_html)
        if not label or label.isdigit() or label in {"Յաջորդ էջ →", "← Նախորդ էջ"}:
            continue
        page_number_int = int(page_number)
        key = (page_number_int, label)
        if key in seen:
            continue
        seen.add(key)
        entries.append({
            "label": label,
            "page_number": page_number_int,
            "href": urllib.parse.urljoin(BASE_URL + "/", href.lstrip("/")),
        })
    entries.sort(key=lambda item: (item["page_number"], item["label"]))
    return entries


def parse_page_image_url(html_text):
    match = IMAGE_RE.search(html_text)
    if not match:
        return None
    return urllib.parse.urljoin(BASE_URL + "/", match.group(1).lstrip("/"))


def build_page_url(dictionary_id, page_number):
    params = urllib.parse.urlencode({
        "dictionaryId": dictionary_id,
        "dt": "HY_HY",
        "pageNumber": page_number,
    })
    return f"{BASE_URL}/imagedDictionaryBrowser.jsp?{params}"


def download_pages(opener, dictionary_id, output_dir, start_page, end_page, save_html, save_images, delay_seconds):
    pages_dir = output_dir / "pages"
    images_dir = output_dir / "images"
    if save_html:
        pages_dir.mkdir(parents=True, exist_ok=True)
    if save_images:
        images_dir.mkdir(parents=True, exist_ok=True)

    page_records = []
    for page_number in range(start_page, end_page + 1):
        page_url = build_page_url(dictionary_id, page_number)
        html_text = fetch_text(opener, page_url)
        image_url = parse_page_image_url(html_text)
        html_relpath = None
        image_relpath = None

        if save_html:
            html_path = pages_dir / f"page_{page_number:04d}.html"
            html_path.write_text(html_text, encoding="utf-8")
            html_relpath = str(html_path.relative_to(output_dir))

        if save_images and image_url:
            image_path = images_dir / f"page_{page_number:04d}.png"
            image_path.write_bytes(fetch_binary(opener, image_url, referer=page_url))
            image_relpath = str(image_path.relative_to(output_dir))

        page_records.append({
            "page_number": page_number,
            "page_url": page_url,
            "image_url": image_url,
            "html_path": html_relpath,
            "image_path": image_relpath,
        })
        if delay_seconds:
            time.sleep(delay_seconds)
    return page_records


def parse_args():
    parser = argparse.ArgumentParser(description="Download page metadata and scans from a Nayiri imaged dictionary.")
    parser.add_argument("output_dir", help="Directory where the manifest, page HTML, and scan images will be stored")
    parser.add_argument("--dictionary-id", type=int, default=7, help="Nayiri dictionary id")
    parser.add_argument("--start-page", type=int, help="First page to download")
    parser.add_argument("--end-page", type=int, help="Last page to download")
    parser.add_argument("--skip-html", action="store_true", help="Do not save raw page HTML")
    parser.add_argument("--skip-images", action="store_true", help="Do not download page images")
    parser.add_argument("--delay", type=float, default=0.0, help="Optional delay in seconds between page downloads")
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    opener = create_opener()

    toc_url = f"{BASE_URL}/imagedDictionaryBrowser.jsp?dictionaryId={args.dictionary_id}&dt=HY_HY"
    toc_html = fetch_text(opener, toc_url)
    manifest = {
        "dictionary_id": args.dictionary_id,
        "source": "Nayiri imaged dictionary browser",
        "title": parse_title(toc_html),
        "toc_url": toc_url,
        "total_pages": parse_total_pages(toc_html),
        "toc_entries": parse_toc_entries(toc_html),
        "downloaded_pages": [],
    }

    toc_path = output_dir / "toc.html"
    toc_path.write_text(toc_html, encoding="utf-8")

    if (args.start_page is None) != (args.end_page is None):
        raise SystemExit("Both --start-page and --end-page are required when downloading pages.")
    if args.start_page is not None and args.start_page > args.end_page:
        raise SystemExit("--start-page must be less than or equal to --end-page.")

    if args.start_page is not None:
        manifest["downloaded_pages"] = download_pages(
            opener=opener,
            dictionary_id=args.dictionary_id,
            output_dir=output_dir,
            start_page=args.start_page,
            end_page=args.end_page,
            save_html=not args.skip_html,
            save_images=not args.skip_images,
            delay_seconds=args.delay,
        )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "output_dir": str(output_dir),
        "dictionary_id": args.dictionary_id,
        "title": manifest["title"],
        "total_pages": manifest["total_pages"],
        "toc_entries": len(manifest["toc_entries"]),
        "downloaded_pages": len(manifest["downloaded_pages"]),
        "manifest": str(manifest_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()