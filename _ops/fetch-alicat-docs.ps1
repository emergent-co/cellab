# fetch-alicat-docs.ps1
# Alicat 원본 카탈로그·데이터시트·제품 이미지를 한 폴더로 내려받는다 (검수용).
# 사용법:  cd C:\dev\rndsetup_homepage ;  .\_ops\fetch-alicat-docs.ps1
# 저장 위치: C:\dev\rndsetup_homepage\_ops\alicat-docs\  (.gitignore 처리됨 — 커밋 안 됨)

$ErrorActionPreference = 'Continue'
$root = Join-Path $PSScriptRoot 'alicat-docs'

$targets = @(
  # ---------- MC 시리즈 (표준 · 라미나 DP) ----------
  @{ d='specs/mc';   u='https://documents.alicat.com/specifications/DOC-SPECS-MC-LOW.pdf';    f='MC_0.5-5SCCM.pdf' }
  @{ d='specs/mc';   u='https://documents.alicat.com/specifications/DOC-SPECS-MC-MID.pdf';    f='MC_10SCCM-20SLPM.pdf' }
  @{ d='specs/mc';   u='https://documents.alicat.com/specifications/DOC-SPECS-MC-HIGH.pdf';   f='MC_50-12000SLPM.pdf' }
  # ---------- MCS (부식성 가스) ----------
  @{ d='specs/mcs';  u='https://documents.alicat.com/specifications/DOC-SPECS-MCS.pdf';       f='MCS_0.5SCCM-12000SLPM.pdf' }
  # ---------- MCQ (고압 320 PSIA) ----------
  @{ d='specs/mcq';  u='https://documents.alicat.com/specifications/DOC-SPECS-MCQ-MID.pdf';   f='MCQ_10SCCM-20SLPM.pdf' }
  @{ d='specs/mcq';  u='https://documents.alicat.com/specifications/DOC-SPECS-MCQ-HIGH.pdf';  f='MCQ_50-12000SLPM.pdf' }
  # ---------- BIOC (바이오리액터·발효조) ----------
  @{ d='specs/bioc'; u='https://documents.alicat.com/specifications/DOC-SPECS-BIOC-LOW.pdf';  f='BIOC_1-5SCCM.pdf' }
  @{ d='specs/bioc'; u='https://documents.alicat.com/specifications/DOC-SPECS-BIOC-MID.pdf';  f='BIOC_10SCCM-20SLPM.pdf' }
  @{ d='specs/bioc'; u='https://documents.alicat.com/specifications/DOC-SPECS-BIOC-HIGH.pdf'; f='BIOC_50-500SLPM.pdf' }

  # ---------- 매뉴얼 ----------
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-MPL.pdf';        f='MC_Manual_10v_Latest.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-9V-MC.pdf';      f='MC_Manual_9v_2021.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-MC.pdf';         f='MC_Manual_8v_2020.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-7V-MC.pdf';      f='MC_Manual_7v_2016_C1D2-ATEX.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-QUICK-MC.pdf';   f='MC_QuickStart.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/Gas_Flow_Controller_Manual.pdf'; f='GasFlowController_Manual.pdf' }

  # ---------- 브로슈어(카탈로그) ----------
  @{ d='brochures';  u='https://documents.alicat.com/cutsheets/M-cut-sheet.pdf';         f='MC_Series_Brochure.pdf' }

  # ---------- 제품 이미지 ----------
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2024/11/mc-model-prod-1200px.webp'; f='mc-group-1200.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2024/10/MC-prod-600px.webp';        f='mc-600.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2024/10/MCS-prod-600px.webp';       f='mcs-600.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2024/11/MCD-prod-600px.webp';       f='mcd-600.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2024/11/MCT-prod-600px.webp';       f='mct-600.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2024/11/BIOC-prod-600px.webp';      f='bioc-600.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2025/06/gas-controller-group-prod-1200px.webp'; f='gas-controller-group-1200.webp' }
  @{ d='images';     u='https://www.alicat.com/wp-content/uploads/2025/02/logo-alicat.svg';           f='logo-alicat.svg' }
)

$ok = 0; $fail = @()
foreach ($t in $targets) {
  $dir = Join-Path $root $t.d
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  $out = Join-Path $dir $t.f
  if (Test-Path $out) { Write-Host ("  skip  " + $t.d + '/' + $t.f) -ForegroundColor DarkGray; $ok++; continue }
  try {
    Invoke-WebRequest -Uri $t.u -OutFile $out -UseBasicParsing -TimeoutSec 60
    $kb = [math]::Round((Get-Item $out).Length / 1KB, 1)
    Write-Host ("  ok    " + $t.d + '/' + $t.f + "  (${kb} KB)") -ForegroundColor Green
    $ok++
  } catch {
    Write-Host ("  FAIL  " + $t.u) -ForegroundColor Red
    $fail += $t.u
  }
}

Write-Host ""
Write-Host ("완료: $ok / " + $targets.Count) -ForegroundColor Cyan
Write-Host ("저장 위치: $root")
if ($fail.Count) { Write-Host "실패 목록:" -ForegroundColor Yellow; $fail | ForEach-Object { Write-Host "  $_" } }
