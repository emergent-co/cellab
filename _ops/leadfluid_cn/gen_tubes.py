# -*- coding: utf-8 -*-
"""리드플루이드 펌프튜브 8종 -> _build/products/leadfluid.json 생성.
수치·규격표는 parsed_170.json 원문에서만 가져온다(손으로 적지 않는다).
한글 카피는 _ops/leadfluid_cn/tube_copy.json.
"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from leadfluid_zh_ko import zh_ko as _zh_ko

_FW = {'（': ' (', '）': ')', '，': ', ', '、': ' · ', '：': ': ', '；': '; ', '　': ' '}

def zh_ko(s):
    s = _zh_ko(s)
    for a, b in _FW.items():
        s = s.replace(a, b)
    return ' '.join(s.split()).replace(' )', ')').replace('( ', '(')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PARSED = os.path.join(ROOT, '_ops/leadfluid_cn/parsed_170.json')
COPY   = os.path.join(ROOT, '_ops/leadfluid_cn/tube_copy.json')
OUT    = os.path.join(ROOT, '_build/products/leadfluid.json')
IMGDIR = os.path.join(ROOT, 'img/leadfluid')

ROLES = json.load(open(os.path.join(ROOT, '_ops/leadfluid_cn/img_roles.json'), encoding='utf-8'))
BODY  = json.load(open(os.path.join(ROOT, '_ops/leadfluid_cn/img_body.json'), encoding='utf-8'))
import html as _h

def hero_imgs(slug):
    idx = ROLES['hero'].get(slug, [])
    got = [f'{slug}-{i}.jpg' for i in idx]
    return [f for f in got if os.path.exists(os.path.join(IMGDIR, f))]

def body_section(slug):
    """제조사 도판 — 표 이미지는 싣지 않는다(우리 한글 표와 중복 + 중국어)."""
    d = BODY.get(slug) or {}
    figs = []
    for i in sorted(d, key=lambda x: int(x)):
        kind, cap = d[i]
        if kind == 'table' or not cap:
            continue
        f = f'{slug}-{i}.jpg'
        if not os.path.exists(os.path.join(IMGDIR, f)):
            continue
        figs.append('<figure class="pkg-fig"><img src="/img/leadfluid/%s" alt="%s" loading="lazy" '
                    'width="1200" height="900"><figcaption>%s</figcaption></figure>'
                    % (f, _h.escape(cap), _h.escape(cap)))
    if not figs:
        return None
    return {'h': '제조사 자료', 'html': '<div class="pkg-figs">' + ''.join(figs) + '</div>',
            'note': '제조사 원문 도판입니다. 캡션은 실험셋업연구소가 한글로 옮긴 것이며, 도판 안의 수치·표기는 제조사 원문 그대로입니다.'}


# 원문 오기(계산 교차검증으로 확인). 값은 고치지 않고 note 로 밝힌다.
ERRATA = {
 'tube-tygon-s3-e3603': '제조사 원문 규격표 중 1.85×0.85 · 2.79×0.85 행의 공칭 치수 칸은 앞 행 값이 잘못 들어가 있습니다(각각 1.85×3.55×0.85 · 2.79×4.49×0.85 이 계산값). 원문 표기를 그대로 실었으니 주문 전 확인 바랍니다.',
 'tube-pharmed-bpt': '제조사 원문 규격표 중 0.89×0.85 행의 공칭 치수 칸은 앞 행 값이 잘못 들어가 있습니다(0.89×2.59×0.85 가 계산값). 원문 표기를 그대로 실었습니다.',
 'tube-tygon-3350': '제조사 원문 규격표 중 1.020.85(×기호 누락) · 2.64×4.88 행은 표기 오류로 보입니다. 원문 표기를 그대로 실었으니 주문 전 확인 바랍니다.',
 'tube-norprene-a60f': '제조사 원문 규격표 중 191# 행의 공칭 치수 19.1×27×4.8 은 계산값 19.1×28.7×4.8 과 다릅니다. 원문 표기를 그대로 실었습니다.',
 'tube-norprene-a60g': '제조사 원문 규격표 중 19# 행의 표준 포장 길이 150 m 는 나머지 전 규격(15 m)과 달라 오기로 보입니다. 원문 표기를 그대로 실었습니다.',
}
COMMON_NOTE = ('13#·14#·19#·16#·25#·15#·17#·24#·18#·35#·36#·73#·82# 등 호수 규격의 외경은 '
               '업계 표준 실측치라 "내경 + 2 × 벽두께" 계산값과 소수점 단위로 다를 수 있습니다.')

def imgs_for(slug):
    got = sorted(glob.glob(os.path.join(IMGDIR, slug + '-*.jpg')))
    return [os.path.basename(p) for p in got]

def pick_spec_table(item):
    """가장 행이 많은 표 = 규격 비교표."""
    best = None
    for sec in item['sections']:
        for t in sec['tables']:
            if len(t) < 3:
                continue
            if best is None or len(t) > len(best):
                best = t
    return best

def build_variants(tbl):
    head = [zh_ko(c) for c in tbl[0]]
    rows = []
    w = len(head)
    for r in tbl[1:]:
        r = [zh_ko(c) for c in r]
        r = (r + [''] * w)[:w]
        rows.append(r)
    return {'heading': '규격 비교표', 'head': head, 'rows': rows}

def faq_for(c, tbl, slug):
    n = len(tbl) - 1
    ids = [r[1] if len(r) > 1 else '' for r in tbl[1:]]
    hoses = [x for x in ids if re.match(r'^\d+#$', x)]
    q = []
    q.append({'tag': '규격', 'q': '%s는 어떤 규격이 있나요?' % c['name'],
              'a': '제조사 규격표 기준 %d개 규격입니다.%s 자세한 내경·외경·벽두께는 위 규격 비교표에서 확인하세요.'
                   % (n, (' 호수 규격은 %s 입니다.' % ' · '.join(hoses)) if hoses else '')})
    q.append({'tag': '호환', 'q': '%s를 우리 연동펌프에 쓸 수 있나요?' % c['name'],
              'a': '펌프헤드가 받는 튜브 내경·벽두께와 규격표의 값이 맞으면 사용할 수 있습니다. '
                   '쓰시는 펌프 모델과 헤드 모델을 알려주시면 맞는 규격을 골라 드립니다.'})
    q.append({'tag': '재질', 'q': '%s의 재질과 사용 온도는 어떻게 되나요?' % c['name'],
              'a': '재질은 %s이고, %s입니다.' % (c['specs'][0][1], c['specs'][1][1])})
    q.append({'tag': '가격', 'q': '%s 가격은 얼마인가요?' % c['name'],
              'a': '규격과 수량에 따라 달라집니다. 오른쪽 주문정보의 견적문의 버튼으로 규격·수량을 남겨 주시면 '
                   '실험셋업연구소에서 회신드립니다.'})
    q.append({'tag': '수명', 'q': '연동펌프 튜브는 얼마나 자주 교체해야 하나요?',
              'a': '재질·회전수·압력·유체에 따라 다릅니다. 유량이 초기 대비 눈에 띄게 줄거나 튜브가 납작해지면 교체 시점입니다. '
                   '같은 조건이라면 압착 구간을 조금씩 옮겨 주는 것만으로도 수명이 늘어납니다.'})
    return q

def main():
    P = {x['url'].replace('https://www.leadfluid.com.cn/', ''): x
         for x in json.load(open(PARSED, encoding='utf-8'))['items']}
    C = json.load(open(COPY, encoding='utf-8'))
    products = []
    for key, c in C.items():
        if key == '_doc':
            continue
        it = P[key]
        tbl = pick_spec_table(it)
        var = build_variants(tbl)
        note = COMMON_NOTE
        if c['slug'] in ERRATA:
            note += ' ' + ERRATA[c['slug']]
        var['note'] = note
        im = hero_imgs(c['slug'])
        products.append({
            'slug': c['slug'], 'name': c['name'], 'name_en': c['name_en'], 'sub': c['sub'],
            'category': '연동펌프 튜브',
            'images': im, 'image_alt': c['name'],
            'answer': c['answer'],
            'summary': c['desc_ko'],
            'features': c['features'],
            'specs': c['specs'],
            'variants': var,
            'specs_note': '제조사 원문 사양을 그대로 옮긴 값입니다.',
            'buybox': [],
            'related': '<a href="/brands/leadfluid/">리드플루이드 전체 제품</a> · <a href="/product/">전 제품 통합 카탈로그</a> · <a href="/contact/">문의·FAQ</a>',
            'keywords': [['연동펌프 튜브', '/product/'], ['펌프 호스', '/product/'],
                         ['리드플루이드', '/brands/leadfluid/'], [c['name_en'], '']],
            'sections': [x for x in [body_section(c['slug'])] if x],
            'faq': faq_for(c, tbl, c['slug']),
            'source': it['url'],
            'ld': {'name': c['name'], 'category': '연동펌프 튜브',
                   'description': c['answer'], 'count': len(tbl) - 1},
        })
    data = {'brand': {'slug': 'leadfluid', 'name_ko': '리드플루이드', 'name_en': 'LEADFLUID',
                      'hub': '/brands/leadfluid/', 'hub_label': '← 리드플루이드 전체',
                      'img_dir': '/img/leadfluid/'},
            'products': products}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding='utf-8'))
        keep = [p for p in old.get('products', [])
                if p['slug'] not in {p2['slug'] for p2 in products}]
        data['products'] = keep + products
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('생성: %s — 제품 %d건' % (OUT, len(data['products'])))
    for p in products:
        left = re.findall(r'[一-鿿]', json.dumps(p, ensure_ascii=False))
        print('  %-24s 규격 %3d행 · 이미지 %d장 · 잔여한자 %d'
              % (p['slug'], len(p['variants']['rows']), len(p['images']), len(left)))

main()
