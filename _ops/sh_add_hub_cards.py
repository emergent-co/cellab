# -*- coding: utf-8 -*-
"""브랜드 허브(brands/sh-scientific/index.html)에 빠진 dscard 를 넣는다.

왜
  통합 카탈로그(/product/)와 헤더 검색은 브랜드 허브의 <article class="dscard"> 를 긁어
  만들어진다. 상세페이지만 만들고 허브에 카드를 안 넣으면 올려놓고도 검색에서 안 나온다.
  린터 NOT_IN_CATALOG 가 그 사고를 잡아 준다.

무엇을
  아래 CARDS 에 적은 10장. 값은 각 상세페이지의 사양표에서 그대로 옮겼다(추측 없음).
  삽입 위치는 같은 계열 카드 바로 뒤 — 허브의 계열 묶음 순서를 깨지 않는다.

쓰기
  python _ops/sh_add_hub_cards.py            검사만
  python _ops/sh_add_hub_cards.py --write    적용
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = os.path.join(ROOT, 'brands', 'sh-scientific', 'index.html')
IMG = '/api/img/web/product/big/'

# slug, 앵커(이 카드 뒤에 넣는다), tier, type, use, 제목, 모델표기, 스펙4행, 용도, 이미지
CARDS = [
    ('cvd-1200-300mm', 'gas-flow-package', '1200', 'CVD·가스플로', 'cvd battery semi vacuum',
     '1200℃ CVD 튜브로 · 300mm', 'SH-CVD-30~250TG300 · TG150',
     [('최고온도', '1200℃'), ('적용 튜브경', '30~250Φ'), ('핫존', '300mm (30TG150은 150mm)'),
      ('구성', '퍼니스+유량계+칠러+진공펌프')],
     '가스 분위기 CVD · 박막 증착', '202606/45ac09673f84a1d96f2dcb3a4680db00.jpg'),
    ('cvd-1200-600mm', 'cvd-1200-300mm', '1200', 'CVD·가스플로', 'cvd battery semi vacuum',
     '1200℃ CVD 튜브로 · 600mm', 'SH-CVD-50~250TG600',
     [('최고온도', '1200℃'), ('적용 튜브경', '50~250Φ'), ('핫존', '600mm'),
      ('구성', '퍼니스+유량계+칠러+진공펌프')],
     '균일 구간 2배 — 다수 시료·긴 기판', '202606/d06312af6a1dfc2caf85812fd5fe64b9.jpg'),
    ('cvd-1200-3zone', 'cvd-1200-600mm', '1200', 'CVD·가스플로', 'cvd battery semi vacuum',
     '1200℃ 3존 CVD 튜브로', 'SH-CVD-50~250TG200-3',
     [('최고온도', '1200℃'), ('적용 튜브경', '50~250Φ'), ('핫존', '200mm × 3존 개별 제어'),
      ('구성', '퍼니스+유량계+칠러+진공펌프')],
     '전구체 기화부·반응부 온도 분리', '202606/b6224868ba5a0bbb2e24e667564a0c85.jpg'),
    ('cvd-1500', 'cvd-1200-3zone', '1500', 'CVD·가스플로', 'cvd sintering vacuum',
     '1500℃ CVD 튜브로', 'SH-CVD-50 / 80 / 100 / 120TH300',
     [('최고온도', '1500℃'), ('적용 튜브경', '50~120Φ'), ('발열체', 'SiC'),
      ('구성', '퍼니스+유량계+칠러+진공펌프')],
     '세라믹·탄화물 계열 고온 CVD', '202606/985a3b0fa4a69d0a439ae0cc6524d807.jpg'),
    ('cvd-1700', 'cvd-1500', '1700', 'CVD·가스플로', 'cvd sintering vacuum',
     '1700℃ CVD 튜브로', 'SH-CVD-50 / 80 / 100 / 120TS300/17',
     [('최고온도', '1700℃'), ('적용 튜브경', '50~120Φ'), ('발열체', 'MoSi2'),
      ('구성', '퍼니스+유량계+칠러+진공펌프')],
     '고온 세라믹 합성 · 탄화', '202606/a2d37cc0f187d510b8445490552402d4.jpg'),
    ('cvd-1800', 'cvd-1700', '1800', 'CVD·가스플로', 'cvd sintering vacuum',
     '1800℃ CVD 튜브로', 'SH-CVD-50 / 80 / 100 / 120TS300/18',
     [('최고온도', '1800℃'), ('적용 튜브경', '50~120Φ'), ('발열체', 'MoSi2'),
      ('구성', '퍼니스+유량계+칠러+진공펌프')],
     'CVD 라인 최고온 등급', '202606/8ec74a740815f9d59d5e784f31e8632d.jpg'),
    ('elevator-1700', 'elevator-1500', '1700', '엘레베이터', 'sintering',
     '1700℃ 엘레베이터로', 'Elevator Type · SH-FU-2 / 4 / 6MSU1700',
     [('최고온도', '1700℃'), ('권장 상시 온도', '1000 ~ 1550℃'),
      ('노 내부치수', '130×130×150 ~ 170×170×190mm'), ('컨트롤러', 'SP590 프로그램')],
     '하부 자동 승강 도어 — 고온 소결', '202210/2b4a62b6bfdb36fd15d60c44189c1b7e.jpg'),
    ('muffle-1200-quartz', 'muffle-1200', '1200', '박스전기로', 'ashing sintering vacuum',
     '1200℃ 석영챔버 진공 머플로', 'SH-FU-5 / 14 / 27MGQ',
     [('최고온도', '1200℃'), ('내용적', '4.5 ~ 27 L'),
      ('석영 챔버', '150×300×100 ~ 300×300×300mm'), ('컨트롤러', 'Digital PID / SP570')],
     '석영 챔버 — 오염 없는 진공 열처리', '202602/95babc940d284ecb9bb2a3ec829db2e3.jpg'),
    ('rotary-kiln-1500-2zone', 'rotary-kiln-1200-3zone', '1500', '회전튜브로', 'cvd sintering battery',
     '1500℃ 연속식 회전킬른 · 2 Zone', 'Rotary Kiln · SH-FU-100 / 120RKH600',
     [('최고온도', '1500℃'), ('핫존', '300mm × 2 = 600mm'),
      ('적용 튜브', '고순도 Al₂O₃ 100~120Φ × 1480mm'), ('컨트롤러', 'SP590 프로그램')],
     '연속 투입·회수 고온 열처리', '202502/5b8a14086af7f3ded03b4757c637eca9.jpg'),
    ('rotary-kiln-1500-3zone', 'rotary-kiln-1500-2zone', '1500', '회전튜브로', 'cvd sintering battery',
     '1500℃ 연속식 회전킬른 · 3 Zone', 'Rotary Kiln · SH-FU-100 / 120RKH900',
     [('최고온도', '1500℃'), ('핫존', '300mm × 3 = 900mm'),
      ('적용 튜브', '고순도 Al₂O₃ 100~120Φ × 1800mm'), ('컨트롤러', 'SP590 프로그램')],
     '체류시간 확보 — 연속 열분해·소성', '202502/086a2fbc7560bbf647997ef21cae0c67.jpg'),
]


def card(c):
    slug, _anchor, tier, typ, use, title, models, specs, purpose, img = c
    text = ' '.join([title, models] + [v for _, v in specs] + [purpose, 'cvd 화학기상증착'
                    if 'CVD' in typ else '']).lower()
    text = re.sub(r'\s+', ' ', text).strip()
    sp = ''.join('<div class="r"><span class="k">%s</span><span class="v">%s</span></div>' % (k, v)
                 for k, v in specs)
    return ('<article class="dscard" data-cat="furnace" data-tier="%s" data-type="%s" '
            'data-use="%s" data-text="%s">'
            '<div class="dscard-im"><img src="%s%s" alt="삼흥에너지 %s" loading="lazy" '
            'width="760" height="570"><div class="dscard-bdg">'
            '<span class="b t">%s℃</span><span class="b y">%s</span></div></div>'
            '<div class="dscard-bd">'
            '<h3 class="dscard-mdl"><a class="dscard-link" href="/brands/sh-scientific/%s/">%s</a></h3>'
            '<div class="dscard-nm">%s</div>'
            '<div class="dscard-sp">%s</div>'
            '<p class="dscard-use">%s</p>'
            '<div class="dscard-ft"><span class="ds-detail">상세 사양 →</span>'
            '<button type="button" class="qbtn qbtn-sm" data-quote="%s (%s)">견적문의</button>'
            '</div></div></article>'
            % (tier, typ, use, text, IMG, img, title, tier, typ, slug, title, models, sp,
               purpose, title, models))


def main():
    write = '--write' in sys.argv
    s = io.open(HUB, encoding='utf-8').read()
    n0 = s.count('<article class="dscard"')
    added = 0
    for c in CARDS:
        slug, anchor = c[0], c[1]
        if 'href="/brands/sh-scientific/%s/"' % slug in s:
            print('  [있음] %s' % slug)
            continue
        m = None
        for mm in re.finditer(r'<article class="dscard".*?</article>', s, re.S):
            if 'href="/brands/sh-scientific/%s/"' % anchor in mm.group(0):
                m = mm
        if not m:
            print('  [FAIL] %-24s 앵커 카드(%s)를 못 찾음' % (slug, anchor))
            continue
        s = s[:m.end()] + '\n' + card(c) + s[m.end():]
        added += 1
        print('  [%s] %-24s %s 뒤에' % ('추가' if write else '예정', slug, anchor))
    n1 = s.count('<article class="dscard"')
    ok = (n1 == n0 + added and s.rstrip().endswith('</html>')
          and s.count('<article') == s.count('</article>'))
    if not ok:
        print('  [FAIL] 검증 실패 — 쓰지 않음 (카드 %d→%d, 추가 %d)' % (n0, n1, added))
        return 1
    print('\n카드 %d → %d (%d장 %s)' % (n0, n1, added, '추가' if write else '예정'))
    if write and added:
        io.open(HUB, 'w', encoding='utf-8', newline='').write(s)
    return 0


if __name__ == '__main__':
    sys.exit(main())
