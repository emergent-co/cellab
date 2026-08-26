# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

B.init('gas-diffusion-cell', 'GU-GDCELL', '가스확산 전해셀')

SER = [('gas-diffusion-cell-entry','입문·초급형'),('gas-diffusion-cell-standard','표준·관찰형'),
       ('gas-diffusion-cell-mea','다기능·MEA형'),('gas-diffusion-cell-solid','고체전해질 QG-20'),
       ('gas-diffusion-cell-mtr','MTR 플로우·광전기화학'),('gas-diffusion-cell-parts','막·GDL·소모품')]
def CR(me): return cross('가스확산 전해셀 시리즈', [(s, n) for s, n in SER if s != me])

FX = ('표기 정가는 가오스유니온 2026 in-situ·MEA·가스확산 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    return ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX)) + extra
WARN = '<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>'
FAQ_FX = ('가격','표기 가격 기준이 어떻게 되나요?',
 '가오스유니온 2026 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
 '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_GDE = ('구성','가스확산 전극(GDE)도 같이 오나요?',
 '아니요. 셀 본체만 판매합니다. 가스확산 전극(카본페이퍼·카본천), 이온교환막, 촉매는 '
 '사용자가 준비하시거나 <a href="/brands/gaossunion/gas-diffusion-cell-parts/">소모품 페이지</a>에서 따로 주문하십니다.')
FAQ_GAP = ('간격','양·음극 간격이 왜 중요한가요?',
 '간격이 좁을수록 용액 저항이 줄어 같은 전류에서 셀 전압이 낮아집니다. 발열과 부반응이 줄고 에너지 효율이 올라갑니다. '
 '다만 너무 좁으면 기포가 빠져나가지 못해 오히려 저항이 튀므로, 전류밀도와 유량에 맞춰 골라야 합니다.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows) + '</tbody></table></div>')

OUT = []
def make(cfg):
    n, sz = B.build(cfg); OUT.append((cfg['slug'], n, sz))
def report():
    for slug, n, sz in OUT: print('%-30s 가격행 %2d · %d bytes' % (slug, n, sz))
