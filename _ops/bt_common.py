# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

SER = [('battery-cell-b001','B001 Swagelok형'),('battery-cell-b002','B002 2전극 in-situ'),
       ('battery-cell-b003','B003 3전극 in-situ'),('battery-cell-b004','B004 광학 관찰'),
       ('battery-cell-b005','B005 개발 평가'),('battery-cell-pressurized','가압·전고체형'),
       ('battery-cell-special','FTIR·금속공기·바나듐')]
SPSER = [('special-cell-dendrite','리튬 덴드라이트 관찰'),('special-cell-membrane','막 전도도'),
         ('special-cell-cdi','CDI 해수담수화'),('special-cell-misc','가시 Swagelok·조립·ECL')]
def CR(me): return cross('배터리 테스트 셀 시리즈', [(s, n) for s, n in SER if s != me])
def CRS(me): return cross('특수 기능 셀 시리즈', [(s, n) for s, n in SPSER if s != me])

FX = ('표기 정가는 가오스유니온 2026 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    return ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX)) + extra
WARN = '<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>'
FAQ_FX = ('가격','표기 가격 기준이 어떻게 되나요?',
 '가오스유니온 2026 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
 '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_SEP = ('구성','분리막과 전해액도 포함되나요?',
 '아니요. 셀 본체만 판매합니다. 양극·음극 시료, 분리막, 전해액은 모두 사용자가 준비하십니다. '
 '카탈로그에도 분리막은 "supplied by the user"로 명시돼 있습니다.')
FAQ_GLOVE = ('조립','글로브박스에서 조립해야 하나요?',
 '리튬 전지 셀은 그렇습니다. 리튬 금속과 유기 전해액은 수분·산소에 민감하므로 아르곤 글로브박스 안에서 조립하셔야 합니다. '
 '조립 후 밀폐된 상태로 꺼내 충방전기에 연결합니다.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows) + '</tbody></table></div>')

OUT = []
def make(cfg):
    n, sz = B.build(cfg); OUT.append((cfg['slug'], n, sz))
def report():
    for slug, n, sz in OUT: print('%-26s 가격행 %2d · %d bytes' % (slug, n, sz))
