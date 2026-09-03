# 가오스유니온 소비자가 일괄 전환: 가격 ×1.45(100원 반올림) + 배송료 별도 표기(_ops/shipping.py)
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import shipping as _ship   # 브랜드별 배송비 SSOT — overseas-pricing §3.5

# 실행: 리포 루트에서 python3 _ops/gu_consumer_price.py
import glob, os, re

MULT = 1.45
SHIP = 'SHIP_FEE_TOKEN'  # 곱셈 페이즈에서 보호할 배송료 자리표시자

def won(n: int) -> str:
    return f'{n:,}원'

def conv(num_str: str) -> str:
    n = int(num_str.replace(',', ''))
    return won(int(round(n * MULT / 100.0)) * 100)

EUR_NOTE = re.compile(r'\s*표기 정가는 가오스유니온 2026 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다\.')
FAQ_OLD = ('가오스유니온 2026 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
           '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_NEW = (f'표기 가격은 소비자가이며 부가세 별도입니다. 국제 배송료 {SHIP}이 별도이며, '
           '해외 직수입 품목으로 상시 할인 대상이 아닙니다.')
SHIP_OLD = '해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.'
SHIP_NEW = f'해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 배송료 {SHIP}이 별도입니다.'
PRICE = re.compile(r'\d{1,3}(?:,\d{3})+원')
LDPRICE = re.compile(r'("price":\s*")(\d+)(")')

report, manual = [], []
files = sorted(glob.glob('brands/gaossunion/*/index.html')) + ['brands/gaossunion/index.html']
for f in files:
    if 'special-cell-dendrite' in f:
        continue  # 이미 전환 완료
    h = open(f, encoding='utf-8').read()
    orig = h
    # 1) EUR 환산·운송비 문구를 먼저 제거/치환 (숫자 곱셈 보호)
    h = EUR_NOTE.sub('', h)
    h = h.replace(FAQ_OLD, FAQ_NEW)
    h = h.replace(SHIP_OLD, SHIP_NEW)
    if 'EUR 1 =' in h:
        manual.append(f); continue  # 변형 문구 — 건드리지 않고 보고
    # 2) 가격 일괄 ×1.45
    n_price = len(PRICE.findall(h))
    h = PRICE.sub(lambda m: conv(m.group(0)[:-1]), h)
    h = LDPRICE.sub(lambda m: m.group(1) + str(int(round(int(m.group(2)) * MULT / 100.0)) * 100) + m.group(3), h)
    # 3) 배송료 복원 + 라벨 정리
    h = h.replace(SHIP, _ship.label('gaossunion'))
    h = re.sub(r'정가 (<b>[\d,]+원</b>\s*\(부가세 별도\))', r'소비자가 \1', h)
    h = h.replace('모델 · 용량 · 정가', '모델 · 용량 · 소비자가')
    assert h.rstrip().endswith('</html>'), f
    if h != orig:
        fo = open(f, 'w', encoding='utf-8'); fo.write(h); fo.flush(); os.fsync(fo.fileno()); fo.close()
        report.append((f, n_price))

print('HTML 전환:', len(report), '파일 /', sum(n for _, n in report), '가격')
for f in manual: print('수동 확인 필요(EUR 변형):', f)

# 4) SQL(SSOT): Gaoss Union 행 retail_price ×1.45
p = 'rndsetup_products.sql'
lines = open(p, encoding='utf-8').read().split('\n')
ROW = re.compile(r"(,'ea',)(\d+),(\d+)(,'https://rndsetup\.com/img/gaossunion)")
cnt = 0
for i, ln in enumerate(lines):
    if 'Gaoss Union' not in ln:
        continue
    m = ROW.search(ln)
    if not m:
        print('SQL 매칭 실패:', ln[:90]); continue
    new_retail = int(round(int(m.group(3)) * MULT / 100.0)) * 100
    lines[i] = ROW.sub(lambda mm: mm.group(1) + mm.group(2) + ',' + str(new_retail) + mm.group(4), ln, count=1)
    cnt += 1
fo = open(p, 'w', encoding='utf-8'); fo.write('\n'.join(lines)); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('SQL 전환:', cnt, '행')
