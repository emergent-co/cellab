# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

B.init('mea-cell', 'GU-MEACEL', '막전극(MEA) 전해셀')

SER = [('mea-cell-ti','MEA-TI-TI·GP 바이폴라'),('mea-cell-wb','MEA-TI-WB 항온 수조'),
       ('mea-cell-special','가시화·라만·유로교체·스택'),('mea-cell-system','EC-MEA 시스템·주변기기'),
       ('mea-cell-parts','막·GDL·소모품')]
def CR(me): return cross('막전극(MEA) 전해셀 시리즈', [(s, n) for s, n in SER if s != me])

FX = ('표기 정가는 가오스유니온 2026 in-situ·MEA·가스확산 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    return ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX)) + extra
WARN = '<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>'
INQ = (WARN % ('<b>대면적 사양은 가격문의</b> — 카탈로그 35페이지 종합표에 30×30 mm 이상 일부 규격이 '
               '<b>“Inquiry”</b>로만 적혀 있습니다. 값이 없는 것이 아니라 제조사가 건별 견적하는 항목이라 '
               '<b>가격문의</b>로 안내합니다.'))
FAQ_FX = ('가격','표기 가격 기준이 어떻게 되나요?',
 '가오스유니온 2026 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
 '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_MEA = ('구성','막전극(MEA)도 같이 오나요?',
 '아니요. 전해셀 본체(바이폴라 플레이트·체결부·피팅)가 구매 구성입니다. 촉매를 담지한 막전극 어셈블리, '
 '이온교환막, 가스확산층(GDL)은 사용자가 준비하시거나 소모품 페이지에서 따로 주문하십니다.')
FAQ_NI = ('재질','니켈판으로 바꿀 수 있나요?',
 '가능합니다. 알칼리 용액에서 티타늄보다 내식성이 필요한 경우 고순도 니켈판으로 맞춤 제작합니다. '
 '카탈로그에 "price to be quoted separately"로 되어 있어 별도 견적이 필요하니 문의해 주세요.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows) + '</tbody></table></div>')

OUT = []
def make(cfg):
    n, sz = B.build(cfg); OUT.append((cfg['slug'], n, sz))
def report():
    for slug, n, sz in OUT: print('%-22s 가격행 %2d · %d bytes' % (slug, n, sz))
