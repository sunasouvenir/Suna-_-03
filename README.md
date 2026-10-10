# 대구 강사공고 레이더

대구 평생교육원·공공도서관·구청 평생학습·백화점 문화센터·클래스 플랫폼(솜씨당, 모카플러스 등) 22곳의
**강사모집 / 강좌개설** 공고를 한곳에서 D-day, 공고 링크, 첨부파일과 함께 보는 웹앱(PWA 준비)입니다.

## 구성

| 파일 | 역할 |
|---|---|
| `index.html` | 앱 화면 (공고 · 예상 일정 · 기관 목록 · 공고 직접 추가). 서버 없이 열려도 동작 |
| `data/sources.json` | 점검 대상 기관과 게시판 URL, 키워드 |
| `data/notices.json` | 자동 점검으로 찾은 공고 (앱이 읽어서 합쳐 보여줌) |
| `scraper/check.py` | 게시판을 읽어 키워드가 있는 새 글, 본문 첨부파일, 마감일을 저장 (표준 라이브러리만 사용) |
| `.github/workflows/weekly-check.yml` | 매주 월요일 09:00 KST 자동 점검 후 `data/notices.json` 커밋 |
| `manifest.webmanifest` | 홈 화면 추가용 |

## 쓰는 법

- 휴대폰: GitHub Pages(Settings → Pages → main / root)로 열고 "홈 화면에 추가".
- 직접 점검: `python scraper/check.py`
- 기관 게시판 주소가 바뀌거나 추가하려면 `data/sources.json` 의 `boards` 를 고칩니다.
  `verified: false` 는 홈페이지만 확인된 곳이라 평생교육 게시판 주소로 바꿔주세요.

## 한계

- 로그인이 필요한 페이지(강좌개설 신청서 작성 등)는 자동 점검하지 않습니다. 공고 목록은 대부분 로그인 없이 보입니다.
- 일부 관공서 사이트는 해외 IP(GitHub Actions)를 막을 수 있습니다. 그 경우 로그에 `!` 로 표시됩니다.
