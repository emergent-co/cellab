# -*- coding: utf-8 -*-
"""AIDA cfg_* 가 build_web.build() 에 넘기는 설정을 그대로 걷어 JSON 으로 뽑는다.
   페이지는 쓰지 않는다 — _build/products/aida.json SSOT 이관의 1단계."""
import os, sys, json, io, glob, importlib, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_web as B

CAPTURED = []
_real = B.build
def _spy(cfg):
    CAPTURED.append(dict(cfg))          # 페이지는 만들지 않는다
B.build = _spy

mods = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(HERE, 'cfg_aida_*.py')))
skip = {'cfg_aida_common', 'cfg_aida_floor'}
buf = io.StringIO()
for m in mods:
    if m in skip: continue
    try:
        with contextlib.redirect_stdout(buf):
            importlib.import_module(m)
    except Exception as e:
        print('[fail] %s — %s' % (m, e))

B.build = _real
out = os.path.join(HERE, '_aida_captured.json')
json.dump(CAPTURED, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('걷은 페이지: %d' % len(CAPTURED))
import collections
keys = collections.Counter()
for c in CAPTURED: keys.update(c.keys())
print('키 사용 빈도:', dict(keys))
print('모델 합계:', sum(len(c.get('price') or c.get('models') or []) for c in CAPTURED))
