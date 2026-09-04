# go.ps1 — 한 번에 동기화·빌드·검증·배포 (왕복 줄이기용)
#
#   .\go.ps1                  작업 시작 : 잠금정리 → fetch → pull → 빌드 → 무결성 검증
#   .\go.ps1 "커밋 메시지"     작업 종료 : 빌드 → 검증 → commit → rebase → push
#
# 두 대의 컴퓨터를 오가며 작업하므로, 배포 모드는 항상 원격 최신 위로 rebase 한 뒤 push 한다.
# 충돌이 나면 자동으로 abort 하고 멈춘다(작업 유실 방지).

param([string]$Message = "")

Set-Location $PSScriptRoot
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8; [Console]::InputEncoding = [Text.Encoding]::UTF8 } catch {}
$OutputEncoding = New-Object System.Text.UTF8Encoding $false  # BOM 없이 — python stdin(`python -`)에 BOM(U+FEFF) 주입 방지
$env:LC_ALL = "C.UTF-8"
git config i18n.commitEncoding utf-8 2>$null
git config i18n.logOutputEncoding utf-8 2>$null

function Step($t) { Write-Host ""; Write-Host "== $t ==" -ForegroundColor Cyan }
function Ok($t)   { Write-Host "[OK] $t" -ForegroundColor Green }
function Warn($t) { Write-Host "[!] $t" -ForegroundColor Yellow }
function Die($t)  { Write-Host ""; Write-Host "[중단] $t" -ForegroundColor Red; exit 1 }

# ── 1. 잠금 정리 (index.lock 사고 방지)
Step "1. .git 잠금 정리"
Remove-Item .git\index.lock -Force -ErrorAction SilentlyContinue
Remove-Item .git\*.lock     -Force -ErrorAction SilentlyContinue
Ok "잠금 해제"

# ── 2. 빌드
Step "2. 빌드 (_build/build.py)"
python _build\build.py
if ($LASTEXITCODE -ne 0) { Die "빌드 실패" }

# ── 3. 무결성 검증 (</html> 종료 + JSON-LD 파싱)
# 검사기는 파일로 뺐다. here-string 을 파이프로 밀어 넣으면 윈도우 파이썬이 stdin 을 UTF-8 로
# 안 읽어 한글이 깨지고, 실패해도 «왜»가 안 나온다. verify.py 는 이유와 파일 끝을 같이 찍고,
# 쓰기 직후 경합으로 짧게 읽힌 경우엔 잠깐 뒤 다시 읽어 본다.
Step "3. HTML 무결성 검증"
python _build\verify.py
if ($LASTEXITCODE -ne 0) { Die "무결성 검증 실패 — 커밋하지 않았습니다" }

# ── 4. 원격 상태 확인
Step "4. 원격 확인 (git fetch)"
git fetch origin
$local  = (git rev-parse HEAD).Trim()
$remote = (git rev-parse origin/main).Trim()
$base   = (git merge-base HEAD origin/main).Trim()
$dirty  = git status --porcelain --untracked-files=no

# ══════ 시작 모드 ══════
if ($Message -eq "") {
    Step "5. 동기화"
    if ($local -eq $remote) {
        Ok "이미 최신 — origin/main과 동일"
    }
    elseif ($local -eq $base) {
        Write-Host "  당겨올 커밋:"; git log --oneline HEAD..origin/main
        $stashed = $false
        if ($dirty) { Warn "커밋 안 된 변경 → 임시 보관(stash) 후 당깁니다"; git stash push -u -m "go.ps1 auto"; $stashed = $true }
        git pull --ff-only
        if ($LASTEXITCODE -ne 0) { if ($stashed) { git stash pop }; Die "pull 실패" }
        if ($stashed) { git stash pop; Warn "보관했던 변경을 되돌렸습니다 — 충돌 여부 확인하세요" }
        Ok "최신 반영 완료"
    }
    elseif ($remote -eq $base) {
        Warn "push 안 한 커밋이 있습니다:"; git log --oneline origin/main..HEAD
        Write-Host "  -> 올리려면:  .\go.ps1 `"커밋 메시지`"" -ForegroundColor Yellow
    }
    else {
        Warn "로컬과 원격이 갈라졌습니다."
        Write-Host "  원격에만 있는 커밋:"; git log --oneline HEAD..origin/main
        Write-Host "  로컬에만 있는 커밋:"; git log --oneline origin/main..HEAD
        Write-Host "  -> 원격 기준으로 맞추려면:  git reset --hard origin/main" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "현재: " -NoNewline; git log -1 --oneline
    exit 0
}

# ══════ 배포 모드 ══════
Step "5. 커밋"
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Warn "변경 없음 — 커밋 생략"; exit 0 }
git diff --cached --stat | Select-Object -Last 1
git commit -m $Message
if ($LASTEXITCODE -ne 0) { Die "커밋 실패" }

Step "6. 원격 최신 위로 재정렬 (rebase)"
# 빌드가 파일을 다시 써서 «내용은 같고 시각만» 바뀐 항목이 남으면
# pull --rebase 가 "You have unstaged changes" 로 거절한다. 먼저 인덱스를 훑어 정리한다.
git update-index --refresh 2>$null | Out-Null
# 당겨올 것이 없으면 재정렬 자체를 건너뛴다.
# 다른 세션이 같은 폴더에서 작업 중이면 add -A 직후에도 워킹트리가 «실제로» 다시 더러워져
# refresh 로도 안 풀리고 "cannot pull with rebase" 로 멈춘다.
# 원격이 merge-base 그대로면 이 커밋은 fast-forward 라 재정렬이 애초에 필요 없다.
if ($remote -eq $base) {
    Ok "원격에 새 커밋 없음 — 재정렬 생략(fast-forward)"
} else {
    git pull --rebase origin main
    if ($LASTEXITCODE -ne 0) {
        git rebase --abort
        Die "원격과 충돌 — 자동 정렬 실패. `git log --oneline origin/main..HEAD` 로 확인 후 수동 처리하세요."
    }
}

Step "7. 푸시"
git push origin main
if ($LASTEXITCODE -ne 0) { Die "푸시 실패 — 다시 .\go.ps1 `"메시지`" 실행" }

Ok "배포 완료 (Cloudflare Pages 자동 배포 시작)"
Write-Host "현재: " -NoNewline; git log -1 --oneline
