"""매주 월요일 대구 평생교육 기관 게시판을 돌며 강사모집·강좌개설 공고를 찾는다.

data/sources.json 의 boards 페이지를 받아 링크 제목에 키워드가 있는 글을 뽑고,
처음 보는 글만 data/notices.json 에 추가한다. 표준 라이브러리만 쓴다.

    python scraper/check.py
"""

import json
import re
import ssl
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources.json"
NOTICES = ROOT / "data" / "notices.json"
KST = timezone(timedelta(hours=9))
ATTACH_EXT = (".hwp", ".hwpx", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip")
UA = "Mozilla/5.0 (compatible; daegu-lifelong-watch/1.0)"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            text = " ".join("".join(self._text).split())
            self.links.append((self._href, text))
            self._href = None


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as res:
        raw = res.read()
        charset = res.headers.get_content_charset()
    for enc in filter(None, [charset, "utf-8", "euc-kr", "cp949"]):
        try:
            return raw.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", "replace")


def find_deadline(text, today):
    """제목에서 '~10.31', '2026.11.2', '11월 2일까지' 같은 마감일을 찾는다."""
    patterns = [
        r"(20\d{2})[.\-/년 ]\s*(\d{1,2})[.\-/월 ]\s*(\d{1,2})",
        r"~\s*(\d{1,2})[.\-/]\s*(\d{1,2})",
        r"(\d{1,2})월\s*(\d{1,2})일\s*까지",
    ]
    found = []
    for i, pat in enumerate(patterns):
        for m in re.finditer(pat, text):
            try:
                if i == 0:
                    d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                else:
                    mo, dy = int(m.group(1)), int(m.group(2))
                    d = date(today.year, mo, dy)
                    if d < today - timedelta(days=60):
                        d = date(today.year + 1, mo, dy)
                found.append(d)
            except ValueError:
                continue
    return max(found).isoformat() if found else None


def classify(title):
    if re.search(r"강사|인력풀|위촉|강의\s*제안|시민제안", title):
        return "강사모집"
    if re.search(r"강좌\s*개설|개설\s*신청|프로그램\s*제안|공모", title):
        return "강좌개설"
    return "수강생모집"


def scan_source(src, keywords, today):
    hits = []
    for board in src.get("boards", []):
        try:
            html = fetch(board)
        except Exception as exc:  # 사이트 하나가 죽어도 나머지는 계속 본다
            print(f"  ! {src['name']} {board}: {exc}", file=sys.stderr)
            continue
        parser = LinkParser()
        parser.feed(html)
        for href, text in parser.links:
            if not href or len(text) < 6 or not any(k in text for k in keywords):
                continue
            url = urljoin(board, href)
            hits.append({
                "id": f"{src['id']}:{url}",
                "source": src["id"],
                "title": text,
                "type": classify(text),
                "url": url,
                "deadline": find_deadline(text, today),
                "attachments": [],
                "found": today.isoformat(),
                "status": "auto",
            })
    return hits


def is_attachment(href, text):
    h = href.lower()
    return h.split("?")[0].endswith(ATTACH_EXT) or "download" in h or "filedown" in h or text.lower().endswith(ATTACH_EXT)


def enrich(hit, today):
    """새 글은 본문을 열어 첨부파일과 접수 마감일을 채운다."""
    try:
        html = fetch(hit["url"])
    except Exception as exc:
        print(f"  ! 본문 {hit['url']}: {exc}", file=sys.stderr)
        return
    parser = LinkParser()
    parser.feed(html)
    files = []
    for href, text in parser.links:
        if href and is_attachment(href, text):
            files.append({"name": text or href.rsplit("/", 1)[-1], "url": urljoin(hit["url"], href)})
    hit["attachments"] = files[:8]
    if not hit["deadline"]:
        body = re.sub(r"<[^>]+>", " ", html)
        near = " ".join(m.group(0) for m in re.finditer(r"(접수|마감|신청)[^\n]{0,80}", body))
        hit["deadline"] = find_deadline(near, today)


def main():
    today = datetime.now(KST).date()
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    store = json.loads(NOTICES.read_text(encoding="utf-8")) if NOTICES.exists() else {"notices": []}
    seen = {n["id"] for n in store["notices"]}

    new = []
    for src in config["sources"]:
        for hit in scan_source(src, config["keywords"], today):
            if hit["id"] not in seen:
                seen.add(hit["id"])
                enrich(hit, today)
                new.append(hit)

    store["notices"] = new + store["notices"]
    store["checked"] = today.isoformat()
    NOTICES.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{today}: 새 공고 {len(new)}건")
    for n in new:
        print(f"  - [{n['type']}] {n['title']} (마감 {n['deadline'] or '미상'}) {n['url']}")
        for f in n["attachments"]:
            print(f"      첨부: {f['name']} {f['url']}")


if __name__ == "__main__":
    main()
