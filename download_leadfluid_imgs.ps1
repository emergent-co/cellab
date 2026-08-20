# 리드플루이드 공식 제품 이미지 전체 다운로드
# 연동(peristaltic)·시린지(syringe)·기어(gear)·방폭 등 펌프 155종 / 이미지 327장
#
# 준비: 다운로드 폴더의 leadfluid_images.txt 를 이 폴더(C:\dev\rndsetup_homepage)로 옮겨주세요.
# 실행:  .\download_leadfluid_imgs.ps1

$listFile = "leadfluid_images.txt"
if (-not (Test-Path $listFile)) {
    $dl = Join-Path $env:USERPROFILE "Downloads\leadfluid_images.txt"
    if (Test-Path $dl) {
        Copy-Item $dl $listFile
        Write-Host "다운로드 폴더에서 목록 파일을 가져왔습니다."
    } else {
        Write-Host "leadfluid_images.txt 가 없습니다. 다운로드 폴더를 확인해 주세요." -ForegroundColor Red
        exit 1
    }
}

$d = "img\leadfluid\official"
New-Item -ItemType Directory -Force -Path $d | Out-Null

$rows = Get-Content $listFile | Where-Object { $_ -match "`t" }
Write-Host "총 $($rows.Count) 장 다운로드 시작..."

$ok = 0; $fail = 0; $skip = 0; $i = 0
foreach ($row in $rows) {
    $i++
    $parts = $row -split "`t", 2
    $name = $parts[0].Trim()
    $url  = $parts[1].Trim()
    $ext  = [System.IO.Path]::GetExtension(($url -split '\?')[0])
    if ([string]::IsNullOrWhiteSpace($ext)) { $ext = ".jpg" }
    $out = Join-Path $d "$name$ext"

    if (Test-Path $out) { $skip++; continue }

    try {
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -TimeoutSec 60
        $ok++
        if ($ok % 25 -eq 0) { Write-Host "  $i / $($rows.Count) ..." }
    } catch {
        $fail++
        Write-Host "FAIL $name" -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host "완료: $ok   실패: $fail   건너뜀(이미 있음): $skip"
Write-Host "저장 위치: $d"
Write-Host "클로드에게 '리드플루이드 이미지 다운로드 끝'이라고 알려주세요."
