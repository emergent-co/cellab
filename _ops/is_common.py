# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

B.init('insitu-cell', 'GU-INSITU', 'in-situ 분광전기화학 셀')

SER = [('insitu-cell-raman','라만'),('insitu-cell-ir','적외·ATR'),('insitu-cell-xrd','XRD'),
       ('insitu-cell-xafs','X선흡수 XAFS'),('insitu-cell-uv','자외 UV'),
       ('insitu-cell-sfg','합주파수 SFG'),('insitu-cell-ms','질량분석·다기능')]
def CR(me): return cross('in-situ 분광전기화학 셀 — 측정 모드별',
                         [(s, n) for s, n in SER if s != me])

FX = ('표기 정가는 가오스유니온 2026 in-situ·MEA·가스확산 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    return ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX)) + extra
WARN = '<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>'
FAQ_FX = ('가격','표기 가격 기준이 어떻게 되나요?',
 '가오스유니온 2026 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
 '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_PEEK = ('재질','셀 바디가 왜 PEEK인가요?',
 'PEEK는 내약품성과 기계 강도가 모두 높으면서 가공 정밀도가 나옵니다. in-situ 셀은 광창과 전극 사이 거리를 mm 단위로 잡아야 하고 분해·세척을 자주 하므로, 금속처럼 전기적으로 간섭하지 않으면서 형상이 유지되는 소재가 필요합니다.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows) + '</tbody></table></div>')

OUT = []
def make(cfg):
    n, sz = B.build(cfg); OUT.append((cfg['slug'], n, sz))
def report():
    for slug, n, sz in OUT: print('%-24s 가격행 %2d · %d bytes' % (slug, n, sz))
