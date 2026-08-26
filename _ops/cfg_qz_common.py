# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

B.init('quartz-cell', 'GU-QZCELL', '부식 시험·석영 전기화학 셀')

SER = [('corrosion-cell-c009','C009 구형 부식'),('corrosion-cell-c010','C010 평판 부식'),
       ('corrosion-cell-c011','C011 코팅 부식'),('quartz-cell-c012','C012 직육면체 석영'),
       ('quartz-cell-c013','C013 박층 분광'),('quartz-cell-c014','C014 원통 개방'),
       ('quartz-cell-c015','C015 원통 소형'),('quartz-cell-c017','C017 원통 대구경'),
       ('quartz-cell-c018','C018 측면 조사')]
def CR(me):
    return cross('부식 시험 · 석영 전기화학 셀 시리즈',
                 [(s, n) for s, n in SER if s != me])

FX = ('표기 정가는 가오스유니온 2026 전해셀 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    h = ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX))
    return h + extra
WARN = ('<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>')
FAQ_FX = ('가격', '표기 가격 기준이 어떻게 되나요?',
  '가오스유니온 2026 전해셀 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
  '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows)
            + '</tbody></table></div>')

OUT = []
def make(cfg):
    n, sz = B.build(cfg)
    OUT.append((cfg['slug'], n, sz))

