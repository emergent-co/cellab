# -*- coding: utf-8 -*-
"""rndsetup_products.sql — 가오스유니온 전극 계열 product_url 재지정.

옛 6장(reference-electrode / counter-electrode / working-electrode /
rde-rrde / rhe / electrode-holder)을 가리키던 192행을
홈페이지 기준 새 52장으로 나눠 지정한다.
product_url 필드만 바꾸며 다른 필드는 건드리지 않는다.
"""
import io, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL  = os.path.join(ROOT, 'rndsetup_products.sql')
BASE = 'https://rndsetup.com/brands/gaossunion/%s/'

OLD = ('reference-electrode', 'counter-electrode', 'working-electrode',
       'rde-rrde', 'rhe', 'electrode-holder')

def target(sobun, name, model):
    n = name
    # ── 기준전극
    if sobun == '기준전극':
        if '염화은' in n:
            return 'agcl-double-salt-bridge' if 'R8060' in n else 'agcl-reference-electrode'
        if '포화칼로멜' in n:      return 'sce-reference-electrode'
        if '황산제일수은' in n:     return 'mercury-sulfate-reference-electrode'
        if '산화수은' in n:        return 'mercury-oxide-reference-electrode'
        if '은이온' in n:          return 'ag-ion-reference-electrode'
        if '루긴' in n:            return 'luggin-capillary'
        if '염다리' in n:          return 'frit-salt-bridge'
    # ── 가역수소전극
    if sobun == '가역수소전극':     return 'rhe-reference-electrode'
    # ── 상대전극
    if sobun == '상대전극':
        if '백금판' in n:          return 'pt-plate-counter-electrode'
        if '백금망' in n:          return 'pt-mesh-counter-electrode'
        if '염다리형 백금선' in n:   return 'pt-wire-with-salt-bridge'
        if '백금선' in n:
            return 'spiral-pt-wire-counter-electrode' if 'PT0523' in n else 'pt-wire-counter-electrode'
        if '백금봉' in n:          return 'pt-rod-counter-electrode'
        if '금선' in n:            return 'spiral-au-wire-counter-electrode'
        if '흑연' in n:            return 'graphite-rod-counter-electrode'
    # ── 작업전극
    if sobun == '작업전극':
        if '카본코팅' in n:        return 'gc-disc-working-electrode'   # 玻碳=유리탄소 오역
        if '백금판 작업전극' in n:   return 'pt-disc-working-electrode'
        if '금판 작업전극' in n:     return 'au-disc-working-electrode'
        if '카본페이스트' in n:      return 'carbon-paste-electrode'
        return 'custom-material-working-electrode'                     # 재질별 19행
    # ── 회전전극
    if sobun == '회전전극':
        if '회전전극 홀더' in n:     return 'rde-coating-jig'
        if '회전링원판전극' in n:
            return 'rrde-external-thread' if '미국식' in n else 'rrde-3a'
        if '회전원판전극' in n:
            return 'rde-external-thread' if '미국식' in n else 'rde-internal-thread'
    # ── 전극 클램프·홀더
    if sobun == '전극 클램프·홀더':
        m = (model or '').strip()
        if m == 'PT-X':                              return 'pt-clamp-ptfe'
        if m in ('PT-1', 'PT-3'):                    return 'pt-clamp-peek'
        if m == 'PT-XS':                             return 'thick-sample-clamp'
        if m == 'GC-2':                              return 'gc-sheet-clamp'
        if m == 'GC 전용':                            return 'gc-electrode-clamp'
        if m == 'AU-X':                              return 'au-electrode-clamp'
        if m.startswith('SUS-1') or m == 'SUS-X':    return 'sus-clamp-sus1'   # SUS-X는 웹 미게시 → 계열 대표로
        if m.startswith('SUS-2'):                    return 'sus-clamp-sus2'
        if m.startswith('TI-'):                      return 'ti-electrode-clamp'
        if m.startswith('E10'):                      return 'simple-electrode-holder'
        if '건조 거치대' in n:                          return 'electrode-drying-rack'
    return None

COLS = ("sku,group_no,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,detail,unit,"
        "supply_price,retail_price,image_url,product_url,lead_time,cert,stock,attr1_n,attr1_v,attr2_n,attr2_v,"
        "attr3_n,attr3_v,attr4_n,attr4_v,status").split(',')
I_SOBUN, I_MODEL, I_NAME, I_URL = COLS.index('sobun'), COLS.index('model'), COLS.index('name'), COLS.index('product_url')

def split_values(b):
    """SQL VALUES(...) 안을 필드로 쪼갠다. 각 필드의 (시작,끝) 오프셋도 돌려준다."""
    out = []; i = 0; start = 0; q = False
    while i < len(b):
        c = b[i]
        if q:
            if c == "'" and i + 1 < len(b) and b[i+1] == "'": i += 2; continue
            if c == "'": q = False; i += 1; continue
            i += 1; continue
        if c == "'": q = True; i += 1; continue
        if c == ',': out.append((start, i)); start = i + 1; i += 1; continue
        i += 1
    out.append((start, len(b)))
    return out

def unq(s):
    s = s.strip()
    return s[1:-1].replace("''", "'") if s.startswith("'") else s

def main(apply=False):
    src = io.open(SQL, encoding='utf-8').read()
    lines = src.split('\n')
    cnt = collections.Counter(); miss = []
    for li, line in enumerate(lines):
        k = line.find('VALUES (')
        if k < 0: continue
        head = line[:k+8]
        body = line[k+8:]
        tail = ''
        for suf in (');', ')'):
            if body.rstrip().endswith(suf):
                cut = len(body.rstrip()) - len(suf)
                tail = body.rstrip()[cut:] + body[len(body.rstrip()):]
                body = body.rstrip()[:cut]
                break
        sp = split_values(body)
        if len(sp) != len(COLS): continue
        get = lambda idx: unq(body[sp[idx][0]:sp[idx][1]])
        if not get(0).startswith('GU-'): continue
        url = get(I_URL)
        slug = url.rstrip('/').rsplit('/', 1)[-1]
        if slug not in OLD: continue
        t = target(get(I_SOBUN), get(I_NAME), get(I_MODEL))
        if not t:
            miss.append((get(I_SOBUN), get(I_NAME), get(I_MODEL))); continue
        s, e = sp[I_URL]
        newbody = body[:s] + "'" + (BASE % t) + "'" + body[e:]
        lines[li] = head + newbody + tail
        cnt[t] += 1
    print('재지정 %d행 / %d슬러그' % (sum(cnt.values()), len(cnt)))
    for k, v in sorted(cnt.items()): print('   %-36s %d' % (k, v))
    if miss:
        print('[!] 매칭 실패 %d행' % len(miss))
        for x in miss[:20]: print('    ', x)
    if apply and not miss:
        io.open(SQL, 'w', encoding='utf-8').write('\n'.join(lines))
        print('SQL 저장 완료')
    elif miss:
        print('매칭 실패가 있어 저장하지 않았습니다')
    else:
        print('(드라이런 — 저장 안 함)')

main(apply='--apply' in sys.argv)
