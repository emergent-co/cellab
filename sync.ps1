# sync.ps1 — 두 컴퓨터 작업 동기화 (작업 시작 시 실행)
# 사용법: 저장소 폴더에서  ->  .\sync.ps1
# 하는 일: 잠금정리 -> fetch -> 안전 pull -> 빌드 -> HTML 무결성 검증 -> 리포트
# 원칙: origin/main(새 구조)이 무조건 기준. 커밋 안 된 로컬 변경은 자동으로 버리지 않고 알려줌.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 한글 출력 깨짐 방지 (콘솔 UTF-8)
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::InputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:LC_ALL = "C.UTF-8"

function Line($t){ Write-Host ""; Write-Host "== $t ==" -ForegroundColor Cyan }

Line "1. .git 잠금 정리"
Remove-Item .git\index.lock -Force -ErrorAction SilentlyContinue
Remove-Item .git\*.lock     -Force -ErrorAction SilentlyContinue

Line "2. 원격 최신 가져오기 (git fetch)"
git fetch origin

$local  = (git rev-parse HEAD).Trim()
$remote = (git rev-parse origin/main).Trim()
$base   = (git merge-base HEAD origin/main).Trim()
$dirty  = git status --porcelain --untracked-files=no

if ($local -eq $remote) {
    Write-Host "[OK] 이미 최신 — origin/main과 동일합니다." -ForegroundColor Green
}
elseif ($local -eq $base) {
    # 로컬이 뒤처짐 -> fast-forward pull
    if ($dirty) {
        Write-Host "[중단] 커밋 안 된 로컬 변경이 있어 당길 수 없습니다." -ForegroundColor Yellow
        git status --short
        Write-Host "-> 먼저 commit/push 하거나, 새 구조 무조건 기준이면:  git reset --hard origin/main" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "새로 당겨올 커밋:" -ForegroundColor Yellow
    git log --oneline HEAD..origin/main
    git pull --ff-only
    Write-Host "[OK] 최신 작업을 당겨왔습니다." -ForegroundColor Green
}
elseif ($remote -eq $base) {
    Write-Host "[주의] 로컬이 origin보다 앞섬 — push 안 한 커밋이 있습니다:" -ForegroundColor Yellow
    git log --oneline origin/main..HEAD
    Write-Host "-> 이 컴퓨터 작업을 올리려면:  git push" -ForegroundColor Yellow
    exit 1
}
else {
    Write-Host "[주의] 로컬과 origin이 갈라졌습니다(divergence). 수동 확인 필요." -ForegroundColor Red
    Write-Host "  - 새 구조 무조건 기준(로컬 변경 버림):  git reset --hard origin/main" -ForegroundColor Red
    Write-Host "  - 로컬 것 살리려면:  git log / git stash 등으로 확인 후 병합" -ForegroundColor Red
    exit 1
}

Line "3. 빌드 (sitemap 등 재생성)"
python _build\build.py

Line "4. HTML 무결성 검증 (모든 .html 이 </html> 로 끝나는지 — CRITICAL_RULES)"
$bad = @()
Get-ChildItem -Recurse -Filter *.html |
    Where-Object { $_.FullName -notmatch '\\_build\\' -and $_.FullName -notmatch '\\node_modules\\' } |
    ForEach-Object {
        $tail = (Get-Content $_.FullName -Tail 3) -join ''
        if ($tail -notmatch '</html>') { $bad += $_.FullName }
    }
if ($bad.Count -gt 0) {
    Write-Host "[경고] 잘림 의심 파일 — commit 전 확인:" -ForegroundColor Red
    $bad | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
} else {
    Write-Host "[OK] 모든 HTML 정상(</html> 종료)." -ForegroundColor Green
}

Line "완료"
Write-Host ("현재: " + (git rev-parse --short HEAD) + "  " + (git log -1 --pretty=%s)) -ForegroundColor Green
