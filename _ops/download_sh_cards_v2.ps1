# 삼흥 상세페이지 대표사진(hero) 원본 내려받기 — 실험실닷컴(silhumsil.com) 직접 요청
#
#   기존 download_cards.ps1 은 https://rndsetup.com/api/img/ 를 쓰는데 그 프록시가 없어져
#   전부 404 가 납니다. 이 스크립트는 원본 도메인에서 바로 받습니다.
#
# 사용법 (저장소 루트에서):
#   powershell -ExecutionPolicy Bypass -File _ops\download_sh_cards_v2.ps1            # 5장
#   powershell -ExecutionPolicy Bypass -File _ops\download_sh_cards_v2.ps1 -Limit 20  # 20장
#   powershell -ExecutionPolicy Bypass -File _ops\download_sh_cards_v2.ps1 -All       # 전부
# 이미 받은 파일은 건너뛰므로 중단 후 다시 실행해도 안전합니다.

param(
  [int]$Limit = 5,
  [switch]$All
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$csv = Join-Path $root '_ops\sh_thumbs_todo.csv'
$dst = Join-Path $root 'img\product\sh-cards'
$log = Join-Path $root '_ops\download_fail.log'
if (-not (Test-Path $csv)) { throw "목록 파일이 없습니다: $csv" }
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$rows = Import-Csv -Path $csv -Encoding UTF8
$todo = @()
foreach ($r in $rows) {
  $url = $r.'원본URL(silhumsil)'
  if ([string]::IsNullOrWhiteSpace($url)) { continue }
  $out = Join-Path $dst ($r.'슬러그' + '.jpg')
  if (Test-Path $out) { continue }
  $todo += [pscustomobject]@{ Slug = $r.'슬러그'; Url = $url; Out = $out }
}

if ($todo.Count -eq 0) { Write-Host '내려받을 사진이 없습니다. (전부 완료)'; exit 0 }
$batch = if ($All) { $todo } else { $todo | Select-Object -First $Limit }
Write-Host ("남음 {0}장 → 이번 실행 {1}장`n" -f $todo.Count, $batch.Count)

$ok = 0; $fail = 0; $i = 0
foreach ($t in $batch) {
  $i++
  try {
    Invoke-WebRequest -Uri $t.Url -OutFile $t.Out -TimeoutSec 60 `
      -Headers @{ 'Referer' = 'https://silhumsil.com/'; 'User-Agent' = 'Mozilla/5.0' }
    $size = (Get-Item $t.Out).Length
    if ($size -lt 3000) {
      Remove-Item $t.Out -Force
      throw "파일이 너무 작음 ($size bytes) — 실제 이미지가 아님"
    }
    $ok++
    Write-Host ("[{0}/{1}] OK    {2}  ({3:N0} KB)" -f $i, $batch.Count, $t.Slug, ($size / 1KB))
  } catch {
    $fail++
    $msg = $_.Exception.Message -replace "`r?`n", ' '
    Write-Host ("[{0}/{1}] FAIL  {2}`n    -> {3}" -f $i, $batch.Count, $t.Slug, $msg) -ForegroundColor Yellow
    Add-Content -Path $log -Value ("{0}`t{1}`t{2}`t{3}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $t.Slug, $t.Url, $msg) -Encoding UTF8
  }
  Start-Sleep -Milliseconds 700
}

Write-Host ("`n이번 실행: 성공 {0}  실패 {1}   |   전체 남은 장수 {2}" -f $ok, $fail, ($todo.Count - $ok))
if ($fail -gt 0) { Write-Host "실패 상세: $log" }
Write-Host '다음 단계:  python clean_thumbs_nanobanana.py   (기본 5장씩)'
