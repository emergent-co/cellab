# -*- coding: utf-8 -*-
"""HTML 무결성 검증 — </html> 종료 + JSON-LD 파싱.

전에는 go.ps1 안에 here-string 으로 박아 파이프로 python 에 밀어 넣었다.
그래서 (1) 윈도우 콘솔에서 한글이 ??? 로 깨지고
      (2) 실패해도 «파일 이름»만 나와, 진짜 깨진 건지 읽다 만 건지 구분이 안 됐다.

빌드가 500개 가까운 파일을 한꺼번에 새로 쓰면, 그 직후 다른 프로세스(백신 검사·색인기 등)가
같은 파일을 붙들고 있어 «짧게 읽히는» 일이 있다. 실제로 두 번 배포가 막혔고
두 번 다 파일은 멀쩡했다. 그래서 한 번 실패하면 잠깐 쉬었다 다시 읽어 본다.
"""
import io, json, os, re, sys, time

SKIP = {'.git', '.wrangler', 'node_modules', '_build', '_to_delete', 'img', 'assets', 'out'}
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

RETRY = 3          # 같은 파일을 최대 3번까지 다시 읽는다
WAIT = 1.2         # 초


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def check(path):
    """(ok, 사유, 꼬리) — 읽기 자체가 실패하면 사유에 그대로 담는다."""
    try:
        t = read(path)
    except Exception as e:
        return False, u'읽지 못함: %s' % e, ''
    if not t.strip():
        return False, u'파일이 비어 있음 (%d바이트)' % len(t), ''
    if not t.rstrip().endswith('</html>'):
        return False, u'</html> 로 끝나지 않음 (%d자)' % len(t), t[-60:].replace('\n', '\\n')
    return True, '', ''


def main():
    files, blocks, bad, ld_bad = [], 0, [], []

    for root, dirs, names in os.walk('.'):
        # continue 로는 그 아래까지 훑는 것을 못 막는다 — dirs 를 잘라야 .git(3만 5천 개)을 건너뛴다
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
        for fn in names:
            if fn.endswith('.html'):
                files.append(os.path.join(root, fn))

    for p in files:
        ok, why, tail = check(p)
        # 한 번 실패했다고 바로 멈추지 않는다 — 쓰기 직후의 경합이면 잠깐 뒤에 통과한다
        for i in range(RETRY - 1):
            if ok:
                break
            time.sleep(WAIT)
            ok, why, tail = check(p)
            if ok:
                print(u'  [i] %s — %d번째에 정상 (쓰기 직후 경합)' % (p, i + 2))
        if not ok:
            bad.append((p, why, tail))
            continue
        try:
            t = read(p)
        except Exception:
            continue
        for m in LD.finditer(t):
            blocks += 1
            try:
                json.loads(m.group(1))
            except Exception as e:
                ld_bad.append((p, str(e)[:80]))

    print(u'  HTML %d개 / JSON-LD %d블록' % (len(files), blocks))

    if bad:
        print(u'  [X] 무결성 실패 %d건:' % len(bad))
        for p, why, tail in bad:
            print(u'      %s' % p)
            print(u'        → %s' % why)
            if tail:
                print(u'        끝: %s' % tail)
        return 1
    if ld_bad:
        print(u'  [X] JSON-LD 파싱 오류 %d건:' % len(ld_bad))
        for p, why in ld_bad:
            print(u'      %s → %s' % (p, why))
        return 1

    print(u'  무결성 OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
