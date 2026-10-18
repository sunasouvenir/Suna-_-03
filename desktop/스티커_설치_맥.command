#!/bin/bash
# 대구 강사공고 레이더 - 바탕화면 스티커 설치 (macOS)
# 사용법: 이 파일을 더블클릭 (처음엔 마우스 오른쪽 > 열기)
# 하는 일: 로그인할 때마다 화면 오른쪽 위에 작은 공고 창을 띄웁니다.
# 지우기: launchctl unload ~/Library/LaunchAgents/kr.daegu.radar.sticker.plist && rm 그 파일
URL="https://claude.ai/artifact/7NX6b849x4pkF1HH1JBwD6#sticker"
W=380; H=700
if [ -d "/Applications/Google Chrome.app" ]; then APP="Google Chrome";
elif [ -d "/Applications/Microsoft Edge.app" ]; then APP="Microsoft Edge";
else echo "Chrome 또는 Edge가 필요합니다."; read -r; exit 1; fi
PLIST="$HOME/Library/LaunchAgents/kr.daegu.radar.sticker.plist"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>kr.daegu.radar.sticker</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/open</string><string>-na</string><string>$APP</string><string>--args</string>
    <string>--app=$URL</string><string>--window-size=$W,$H</string><string></string>
  </array>
  <key>RunAtLoad</key><true/>
</dict></plist>
PL
launchctl unload "$PLIST" 2>/dev/null; launchctl load "$PLIST"
echo "설치 완료: 로그인할 때마다 자동으로 뜹니다. (처음 한 번은 창 안에서 claude.ai 로그인)"
