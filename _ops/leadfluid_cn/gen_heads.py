# -*- coding: utf-8 -*-
"""리드플루이드 펌프헤드 15종 -> _build/products/leadfluid.json 에 추가.
사양표는 parsed_170.json 원문 표를 사전으로 자동 변환한다(손으로 적지 않는다).
한글 카피는 _ops/leadfluid_cn/head_copy.json.
"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from leadfluid_zh_ko import zh_ko as _zh

_FW = {'（': ' (', '）': ')', '，': ', ', '、': ' · ', '：': ': ', '；': '; ', '　': ' ', '＜': '<', '＞': '>'}
def zh(s):
    s = _zh(s or '')
    for a, b in _FW.items():
        s = s.replace(a, b)
    s = s.replace('\\', ' / ')
    s = ' '.join(s.split()).replace(' )', ')').replace('( ', '(')
    s = re.sub(r'\)\(', ') (', s)
    return s

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PARSED = os.path.join(ROOT, '_ops/leadfluid_cn/parsed_170.json')
COPY   = os.path.join(ROOT, '_ops/leadfluid_cn/head_copy.json')
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


def imgs_for(slug):
    fs = glob.glob(os.path.join(IMGDIR, slug + '-*.jpg'))
    fs.sort(key=lambda p: int(re.search(r'-(\d+)\.jpg$', p).group(1)))
    return [os.path.basename(p) for p in fs]

def tables(item):
    out = []
    for sec in item['sections']:
        if sec['h'] in ('同类热销', '产品推荐', '相关产品'):
            continue
        out += sec['tables']
    return out

def spec_rows(item):
    rows = []
    for t in tables(item):
        for r in t:
            cells = [c for c in r if c and c.strip()]
            if len(cells) == 2:
                k, v = zh(cells[0]), zh(cells[1])
                if k and v and k != v and not k.startswith('기술 사양'):
                    if k not in [x[0] for x in rows]:
                        rows.append([k, v])
    return rows

def wide_table(item):
    for t in tables(item):
        if len(t) >= 3 and max(len(r) for r in t) >= 3:
            head = [zh(c) for c in t[0]]
            w = len(head)
            rows = [[zh(c) for c in (r + [''] * w)[:w]] for r in t[1:]]
            return {'heading': '규격 비교표', 'head': head, 'rows': rows}
    return None

def faq_for(c, specs):
    def find(*keys):
        for k, v in specs:
            if any(x in k for x in keys):
                return v
        return ''
    q = []
    flow = find('유량 범위', '최대 유량')
    if flow:
        q.append({'tag': '유량', 'q': '%s의 유량 범위는 어떻게 되나요?' % c['name'],
                  'a': '제조사 사양 기준 %s 입니다. 실제 유량은 쓰는 튜브 규격과 회전수에 따라 달라집니다.' % flow})
    tube = find('적용 튜브', '튜브 규격')
    if tube:
        q.append({'tag': '튜브', 'q': '%s에는 어떤 튜브를 쓰나요?' % c['name'],
                  'a': '제조사 사양 기준 %s 입니다. 재질(실리콘·PHARMED·Norprene 등)은 이송할 유체에 맞춰 고르시면 됩니다.' % tube})
    q.append({'tag': '호환', 'q': '%s를 지금 쓰는 펌프 본체에 달 수 있나요?' % c['name'],
              'a': '본체의 구동축 규격과 설치 치수가 맞아야 합니다. 쓰시는 펌프 모델을 알려주시면 장착 가능 여부를 확인해 드립니다.'})
    q.append({'tag': '가격', 'q': '%s 가격은 얼마인가요?' % c['name'],
              'a': '구성과 수량에 따라 달라집니다. 오른쪽 주문정보의 견적문의 버튼으로 남겨 주시면 실험셋업연구소에서 회신드립니다.'})
    q.append({'tag': 'A/S', 'q': '펌프헤드도 국내에서 수리되나요?',
              'a': '실험셋업연구소는 실험기기 수리 전문업체 emergent co.의 온라인 유통사로, 리드플루이드 제품을 국내에서 직접 수리·기술지원합니다. 해외 반송이 필요 없습니다.'})
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
        specs = spec_rows(it)
        if not specs:
            specs = c.get('specs_manual') or []
        p = {
            'slug': c['slug'], 'name': c['name'], 'name_en': c['name_en'], 'sub': c['sub'],
            'category': '연동펌프 헤드',
            'images': hero_imgs(c['slug']), 'image_alt': '리드플루이드 ' + c['name'],
            'answer': c['answer'], 'summary': c['desc_ko'],
            'features': c['features'],
            'specs': specs or c.get('specs_manual') or [['제조사 사양', '제조사가 사양표를 이미지로만 제공합니다. 필요한 값은 문의 주시면 확인해 드립니다.']],
            'specs_note': '제조사 원문 사양을 그대로 옮긴 값입니다.'
                          + (' 출처: ' + c['specs_src'] if not specs and c.get('specs_src') else ''),
            'buybox': [],
            'related': '<a href="/brands/leadfluid/">리드플루이드 전체 제품</a> · <a href="/product/">전 제품 통합 카탈로그</a> · <a href="/contact/">문의·FAQ</a>',
            'keywords': [['펌프헤드', '/product/'], ['연동펌프 헤드', '/product/'],
                         ['리드플루이드', '/brands/leadfluid/'], [c['name_en'], '']],
            'sections': [x for x in [body_section(c['slug'])] if x],
            'faq': faq_for(c, specs),
            'source': it['url'],
            'ld': {'name': c['name'], 'category': '연동펌프 헤드', 'description': c['answer']},
        }
        wt = wide_table(it)
        if wt:
            p['variants'] = wt
        products.append(p)
    data = json.load(open(OUT, encoding='utf-8'))
    keep = [x for x in data['products'] if x['slug'] not in {y['slug'] for y in products}]
    data['products'] = keep + products
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('leadfluid.json 총 %d건 (헤드 %d건 추가)' % (len(data['products']), len(products)))
    for p in products:
        left = re.findall(r'[一-鿿]', json.dumps(p, ensure_ascii=False))
        print('  %-16s 사양 %2d행 · 이미지 %2d장 · FAQ %d · 잔여한자 %d'
              % (p['slug'], len(p['specs']), len(p['images']), len(p['faq']), len(left)))

main()
