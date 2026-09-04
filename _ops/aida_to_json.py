# -*- coding: utf-8 -*-
"""AIDA cfg_* → _build/products/aida.json (데이터 주도 SSOT 이관 2단계).
   _ops/aida_capture.py 가 뽑아 둔 설정을 제품 JSON 스키마로 옮긴다."""
import os, sys, json, io, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_web as B
B._use('aida'); B._KOFF[0] = True          # 판매가는 cfg 에서 이미 완성 — ×1.45 재적용 금지

CAP = json.load(open(os.path.join(HERE, '_aida_captured.json'), encoding='utf-8'))
BR  = json.load(open(os.path.join(ROOT, '_build', 'brands.json'), encoding='utf-8'))
prof = (BR['brands'] if 'brands' in BR else BR)['aida']
SRC  = (prof.get('source') or {}).get('url', '')

def kv(pairs):
    return [[str(a), str(b)] for a, b in (pairs or [])]

out = []
for c in CAP:
    slug = c['slug']
    price = [(m, s, p) for m, s, p in (c.get('price') or [])]
    imgs  = B.autoimgs(slug)

    p = collections.OrderedDict()
    p['slug']      = slug
    p['name']      = c['h1']
    p['name_en']   = c['sub']
    p['category']  = '전기화학 · ' + c['cat']
    p['sub']       = c['sub']
    p['title']     = c['title']
    p['desc']      = c['desc']
    p['og_title']  = c['title'].split(' | ')[0]
    p['og_desc']   = c['desc']
    p['answer']    = c['answer']
    p['summary']   = c['summary']
    p['images']    = ['/img/aida/' + f for f in imgs]
    p['image_alt'] = c['h1']
    p['features']  = list(c.get('feat') or [])
    p['specs']     = kv(c.get('spec'))
    if c.get('warn'):
        p['warn'] = c['warn']
    if price:
        p['variants'] = {
            'heading': '모델 · 규격 · 소비자가 (%d종)' % len(price),
            'head': ['모델', '규격', '소비자가'],
            'rows': [[m, s, format(B.landed_extra(pr), ',') + '원'] for m, s, pr in price],
        }
        p['buybox'] = [{'m': m, 's': s, 'p': B.landed(pr), 'x': B.landed_extra(pr)}
                       for m, s, pr in price]
    else:
        p['variants'] = {}
        p['buybox'] = []
    if c.get('note'):
        p['specs_note'] = c['note']
    p['faq']       = kv(c.get('faq'))
    p['related']   = c.get('cross', '')
    p['keywords']  = ['아이다', 'AIDA', c['cat'], c['h1'].split()[0]]
    p['source']    = SRC
    p['ld']        = {'name': 'AIDA ' + c.get('ldname', c['h1']),
                      'sku': c['h1'].split()[0],
                      'category': '전기화학 · ' + c['cat'],
                      'description': c['desc'],
                      'low': min([B.landed_extra(pr) for _, _, pr in price] or [0]),
                      'high': max([B.landed_extra(pr) for _, _, pr in price] or [0]),
                      'count': len(price)}
    out.append(p)

dest = os.path.join(ROOT, '_build', 'products', '_aida.wip.json')
json.dump({'brand': 'aida', 'products': out}, open(dest, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('제품 %d종 · 모델 %d개 → %s' % (out and len(out), sum(len(x['buybox']) for x in out), dest))
miss = collections.Counter()
for x in out:
    for k in ('answer','images','features','specs','variants','buybox','faq','source'):
        if not x.get(k): miss[k] += 1
print('빈 항목:', dict(miss) or '없음')
