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

  # ---------- 진공 · SEMI (MCV · SFF · MCES · MCVS) ----------
  @{ d='specs/vacuum'; u='https://documents.alicat.com/specifications/DOC-SPECS-MCV-LOW.pdf';  f='MCV_0.5-5SCCM.pdf' }
  @{ d='specs/vacuum'; u='https://documents.alicat.com/specifications/DOC-SPECS-MCV-MID.pdf';  f='MCV_10SCCM-20SLPM.pdf' }
  @{ d='specs/vacuum'; u='https://documents.alicat.com/specifications/DOC-SPECS-SFF-LOW.pdf';  f='SFF_0.5-5SCCM.pdf' }
  @{ d='specs/vacuum'; u='https://documents.alicat.com/specifications/DOC-SPECS-SFF-MID.pdf';  f='SFF_10SCCM-20SLPM.pdf' }
  @{ d='specs/vacuum'; u='https://documents.alicat.com/specifications/DOC-SPECS-MCES.pdf';     f='MCES_0.5SCCM-20SLPM.pdf' }
  @{ d='specs/vacuum'; u='https://documents.alicat.com/specifications/DOC-SPECS-MCVS.pdf';     f='MCVS_0.5SCCM-20SLPM.pdf' }
  # ---------- BASIS 2 (소형 MEMS 열식) ----------
  @{ d='specs/basis';  u='https://documents.alicat.com/specifications/DOC-SPECS-BASIS.pdf';    f='BASIS2_100SCCM-100SLPM.pdf' }
  @{ d='manuals';      u='https://documents.alicat.com/manuals/DOC-MANUAL-BASIS2.pdf';         f='BASIS2_Manual.pdf' }
  @{ d='brochures';    u='https://documents.alicat.com/cutsheets/BASIS2-Bifold.pdf';           f='BASIS2_Brochure.pdf' }
  # ---------- 압력 컨트롤러 (PC · PCD · IVC · PCX) ----------
  @{ d='specs/pressure'; u='https://documents.alicat.com/specifications/DOC-SPECS-PC.pdf';      f='PC_0.07-3000PSI.pdf' }
  @{ d='specs/pressure'; u='https://documents.alicat.com/specifications/DOC-SPECS-PCD.pdf';     f='PCD_0.07-3000PSI.pdf' }
  @{ d='specs/pressure'; u='https://documents.alicat.com/specifications/DOC-SPECS-IVC.pdf';     f='IVC_10-1000TorrA.pdf' }
  @{ d='specs/pressure'; u='https://documents.alicat.com/specifications/DOC-SPECS-PCX-SFF.pdf'; f='PCX_500Torr-100PSIA.pdf' }
  @{ d='manuals';        u='https://documents.alicat.com/manuals/DOC-MANUAL-9V-PC.pdf';         f='PC_Manual_9v_2021.pdf' }
  @{ d='manuals';        u='https://documents.alicat.com/manuals/DOC-MANUAL-9V-PCD.pdf';        f='PCD_Manual_9v_2021.pdf' }
  @{ d='manuals';        u='https://documents.alicat.com/manuals/DOC-MANUAL-EXTSEN.pdf';        f='EXTSEN_Manual.pdf' }
  @{ d='brochures';      u='https://documents.alicat.com/cutsheets/Pressure-controllers.pdf';   f='PC_PCD_Brochure.pdf' }

  # ---------- 매뉴얼 ----------
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-MPL.pdf';        f='MC_Manual_10v_Latest.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-9V-MC.pdf';      f='MC_Manual_9v_2021.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-MC.pdf';         f='MC_Manual_8v_2020.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-7V-MC.pdf';      f='MC_Manual_7v_2016_C1D2-ATEX.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/DOC-MANUAL-QUICK-MC.pdf';   f='MC_QuickStart.pdf' }
  @{ d='manuals';    u='https://documents.alicat.com/manuals/Gas_Flow_Controller_Manual.pdf'; f='GasFlowController_Manual.pdf' }

  # ---------- 브로슈어(카탈로그) ----------
  @{ d='brochures';  u='https://documents.alicat.com/cutsheets/M-cut-sheet.pdf';         f='MC_Series_Brochure.pdf' }

  # ---------- 제품 이미지 (alicat.com) → 웹 게시 경로 img/product/alicat/ ----------
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/10/MC-prod-600px.webp';                    f='mc.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/10/MCS-prod-600px.webp';                   f='mcs.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/11/MCD-prod-600px.webp';                   f='mcd.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/11/MCT-prod-600px.webp';                   f='mct.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/11/BIOC-prod-600px.webp';                  f='bioc.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/11/MCV-prod-600px.webp';                   f='mcv.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/SFF-prod-600px.webp';                   f='sff.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/MCES-prod-600px.webp';                  f='mces.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/MCVS-prod-600px.webp';                  f='mcvs.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/11/BASIS-controller-prod-600px.webp';      f='basis.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/10/BASIS-Manifold-prod-600px.webp';        f='basis-manifold.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/PC-prod-600px.webp';                    f='pc.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2025/02/PCX-prod-600px.webp';                   f='pcx.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/PC3-prod-600px.webp';                   f='pc3.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/10/PCD-prod-600px.webp';                   f='pcd.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/PCDS-prod-600px.webp';                  f='pcds.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/PCD3-prod-600px.webp';                  f='pcd3.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/IVCD-prod-600px.webp';                  f='ivcd.webp' }
  # 그룹 컷
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/11/mc-model-prod-1200px.webp';             f='group-mc.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/vaccuum-group-prod-1200px.webp';        f='group-vacuum.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2025/02/PC-group-prod-1200px-b.webp';           f='group-pc.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/PCD-series-prod-900px.webp';            f='group-pcd.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2024/12/basis-bc-series-controller-prod-900px.webp'; f='group-basis.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2025/06/gas-controller-group-prod-1200px.webp'; f='group-all.webp' }
  @{ w=1; u='https://www.alicat.com/wp-content/uploads/2025/02/logo-alicat.svg';                       f='logo-alicat.svg' }
)

$ok = 0; $fail = @()
foreach ($t in $targets) {
  if ($t.w) { $dir = Join-Path (Split-Path $PSScriptRoot -Parent) 'img\product\alicat' }
  else      { $dir = Join-Path $root $t.d }
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  $out = Join-Path $dir $t.f
  if (Test-Path $out) { Write-Host ("  skip  " + $t.f) -ForegroundColor DarkGray; $ok++; continue }
  try {
    Invoke-WebRequest -Uri $t.u -OutFile $out -UseBasicParsing -TimeoutSec 60
    $kb = [math]::Round((Get-Item $out).Length / 1KB, 1)
    Write-Host ("  ok    " + $t.f + "  (${kb} KB)") -ForegroundColor Green
    $ok++
  } catch {
    Write-Host ("  FAIL  " + $t.u) -ForegroundColor Red
    $fail += $t.u
  }
}

Write-Host ""
Write-Host ("완료: $ok / " + $targets.Count) -ForegroundColor Cyan
Write-Host ("문서 저장 위치: $root")
Write-Host ("이미지 저장 위치: " + (Join-Path (Split-Path $PSScriptRoot -Parent) 'img\product\alicat'))
if ($fail.Count) { Write-Host "실패 목록:" -ForegroundColor Yellow; $fail | ForEach-Object { Write-Host "  $_" } }
