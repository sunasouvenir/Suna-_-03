# 대구 강사공고 레이더 - 바탕화면 스티커 설치 (Windows)
# 사용법: 이 파일을 마우스 오른쪽 버튼 > "PowerShell에서 실행"
# 하는 일: 노트북을 켤 때마다 화면 오른쪽 위에 작은 공고 창(스티커)을 띄우는 바로가기를
#          '시작프로그램' 폴더와 바탕화면에 만듭니다. 지우려면 두 바로가기만 삭제하면 됩니다.

$Url    = "https://claude.ai/artifact/7NX6b849x4pkF1HH1JBwD6#sticker"
$Name   = "강사공고 스티커"
$Width  = 380
$Height = 700

Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$X = $screen.Right - $Width - 16
$Y = $screen.Top + 16

# Edge는 윈도우에 기본으로 있고, Chrome이 있으면 Chrome을 씁니다.
$candidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LocalAppData\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
)
$Browser = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Browser) { Write-Host "Chrome 또는 Edge를 찾지 못했습니다." -ForegroundColor Red; Read-Host "엔터를 누르면 닫힙니다"; exit 1 }

$BrowserArgs = "--app=`"$Url`" --window-size=$Width,$Height --window-position=$X,$Y"
$shell = New-Object -ComObject WScript.Shell
foreach ($dir in @([Environment]::GetFolderPath("Startup"), [Environment]::GetFolderPath("Desktop"))) {
  $lnk = $shell.CreateShortcut((Join-Path $dir "$Name.lnk"))
  $lnk.TargetPath = $Browser
  $lnk.Arguments = $BrowserArgs
  $lnk.Description = "대구 강사모집·강좌개설 공고 D-day"
  $lnk.Save()
}

Write-Host "설치 완료: 다음 부팅부터 자동으로 뜹니다. 지금 한 번 띄웁니다." -ForegroundColor Green
Write-Host "처음 한 번은 창 안에서 claude.ai 로그인이 필요할 수 있습니다."
Start-Process $Browser $BrowserArgs
Start-Sleep -Seconds 2
