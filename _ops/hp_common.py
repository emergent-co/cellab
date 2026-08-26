# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

B.init('high-pressure-cell', 'GU-HPCELL', '고압 전기화학 셀·계측 장비')

SER = [('high-pressure-cell-p001','P001 단실'),('high-pressure-cell-p002','P002 이중실(내부막)'),
       ('high-pressure-cell-p003','P003 이중실(외부막)'),('high-pressure-cell-p004','P004 광촉매'),
       ('high-pressure-cell-pfc','PFC 가스확산 플로우'),('high-pressure-cell-parts','고압 전극·부속'),
       ('echem-instrument','계측·주변 장비')]
def CR(me): return cross('고압 전기화학 셀 · 계측 장비', [(s, n) for s, n in SER if s != me])

FX = ('표기 정가는 가오스유니온 2026 in-situ·MEA·가스확산 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    return ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX)) + extra
WARN = '<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>'
SAFE = (WARN % ('<b>고압 사용 시 주의</b> — 정격 사용압력 <b>6 MPa</b>를 넘기지 마십시오. '
                '가압 전 밸브·피팅 체결과 O링 상태를 반드시 점검하고, 감압은 천천히 하십시오. '
                '고압 실험은 안전 절차를 갖춘 환경에서만 진행해 주세요.'))
FAQ_FX = ('가격','표기 가격 기준이 어떻게 되나요?',
 '가오스유니온 2026 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
 '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_TI = ('재질','왜 티타늄 셀인가요?',
 '고압에서 견디는 강도와 전해액 내식성을 동시에 만족해야 하기 때문입니다. 스테인리스는 염화물이나 산성 전해액에서 부식되고, 유리는 가압에 쓸 수 없습니다. 티타늄은 둘 다 해결합니다.')
FAQ_EL = ('전극','전극이 포함되나요?',
 '아니요. P001~P003 계열은 전극이 모두 별매입니다. 고압용 전극 홀더·백금판 상대전극·기준전극을 셀 계열에 맞춰 따로 주문하셔야 하며, P001 계열과 P002·P003 계열은 규격이 달라 가격도 다릅니다.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows) + '</tbody></table></div>')

TI = [('셀 바디 재질','<b>티타늄(Ti)</b>'),
      ('최대 내압','<b>6 MPa</b> (정격 사용압력 6 MPa)'),
      ('밸브 재질','<b>304 스테인리스</b>'),
      ('전극 구성','3전극 — 기준 Ag/AgCl · 상대 백금판 · 작업 유리탄소 홀더 (<b>모두 별매</b>)')]

OUT = []
def make(cfg):
    n, sz = B.build(cfg); OUT.append((cfg['slug'], n, sz))
def report():
    for slug, n, sz in OUT: print('%-26s 가격행 %2d · %d bytes' % (slug, n, sz))
