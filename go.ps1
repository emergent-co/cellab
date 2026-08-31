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
Step "3. HTML 무결성 검증"
$py = @'
import os, re, json, sys
bad = []; ld = []; n = 0; l = 0
SKIP = {'.git', '.wrangler', 'node_modules', '_build', '_to_delete', 'img', 'assets', 'out'}
for root, dirs, fs in os.walk('.'):
    # continue 로는 그 아래까지 훑는 것을 못 막는다 — dirs 를 잘라야 .git(3만 5천 개)을 건너뛴다
    dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
    r = root.replace('\\', '/')
    for fn in fs:
        if not fn.endswith('.html'): continue
        p = os.path.join(root, fn); n += 1
        t = open(p, encoding='utf-8').read()
        if not t.rstrip().endswith('</html>'): bad.append(p)
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            l += 1
            try: json.loads(m.group(1))
            except Exception: ld.append(p)
print('  HTML %d개 / JSON-LD %d블록' % (n, l))
if bad:
    print('  [X] </html> 미종료:'); [print('     ', x) for x in bad]; sys.exit(1)
if ld:
    print('  [X] JSON-LD 파싱 오류:'); [print('     ', x) for x in ld]; sys.exit(1)
print('  무결성 OK')
'@
$py | python -
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
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    git rebase --abort
    Die "원격과 충돌 — 자동 정렬 실패. `git log --oneline origin/main..HEAD` 로 확인 후 수동 처리하세요."
}

Step "7. 푸시"
git push origin main
if ($LASTEXITCODE -ne 0) { Die "푸시 실패 — 다시 .\go.ps1 `"메시지`" 실행" }

Ok "배포 완료 (Cloudflare Pages 자동 배포 시작)"
Write-Host "현재: " -NoNewline; git log -1 --oneline
