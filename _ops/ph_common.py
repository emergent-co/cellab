# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_page as B
from build_page import price_table, opt_table, model_block, faq_html, cross, IN, DL, OPT, EX, OP

B.init('photo-cell', 'GU-PHCELL', '광전기화학·광촉매 셀')

SER = [('photo-cell-c019','C019 단실'),('photo-cell-c023','C023 H형 단일광창'),
       ('photo-cell-c023-10','C023-10 소용량'),('photo-cell-c024','C024 H형 이중광창'),
       ('photo-cell-c024-10','C024-10 소용량'),('photo-cell-c025','C025 3H형'),
       ('photo-cell-c025-10','C025-10 소용량'),('photo-cell-c026','C026 전PTFE 단실'),
       ('photo-cell-c027','C027 전PTFE H형'),('photo-cell-c028','C028 밀폐 단실'),
       ('photo-cell-c030','C030 판상 시편'),('photo-cell-c032','C032 소형 H형'),
       ('photo-cell-c033','C033 순광촉매'),('photo-cell-k1300','K1300 측면조사'),
       ('photo-cell-acc','부속·소모품')]
def CR(me): return cross('광전기화학 · 광촉매 셀 시리즈', [(s,n) for s,n in SER if s != me])

FX = ('표기 정가는 가오스유니온 2026 전해셀 카탈로그가를 <b>EUR 1 = 1,750원</b> 기준으로 환산한 값입니다.<br>'
      '<b>해외 직수입 품목으로 상시 할인 대상이 아니며, 국제 운송비가 별도로 발생할 수 있습니다.</b>')
def note(fr, extra=''):
    return ('<p class="pkg-note" style="margin-top:16px">정가 <b>%s</b> (부가세 별도). %s</p>' % (fr, FX)) + extra
WARN = '<p class="pkg-note" style="border-left:3px solid #854F0B;padding-left:12px;color:#5a4a2a">%s</p>'
FAQ_FX = ('가격','표기 가격 기준이 어떻게 되나요?',
 '가오스유니온 2026 전해셀 카탈로그가를 EUR 1 = 1,750원으로 환산한 정가이며 부가세 별도입니다. '
 '해외 직수입 품목으로 상시 할인 대상이 아니고 국제 운송비가 별도 발생할 수 있습니다.')
FAQ_WIN = ('광창','석영 광창이 깨지면 교체할 수 있나요?',
 '광창은 락링으로 셀 바디에 물려 있어 링을 풀고 석영판만 갈아 끼우면 됩니다. 교체용 석영 광창판(007-32)은 175,000원에 별도 판매합니다.')
FAQ_EXT = ('전극','기존 전극을 그대로 쓸 수 있나요?',
 '이 계열은 모두 연장형(extended) 전극이 필요합니다. 일반 길이 전극은 셀 깊이에 닿지 않습니다. 완전 밀폐형은 뚜껑의 오디오잭 포트로 내부에서 끼우는 구조라 셀에 맞춘 전용 제작이 필요합니다.')
def tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows) + '</tbody></table></div>')

GLASS = [('셀 바디','고붕규산 유리(High borosilicate glass)'),
         ('광창','석영 · <b>투과율 95% 이상</b> · <b>락링</b> 체결로 석영판 빠른 교체'),
         ('전극','주문 맞춤 · 모두 <b>연장형(extended)</b> 전극')]
PTFE = [('셀 바디','PTFE(폴리테트라플루오로에틸렌)'),
        ('광창','석영 유리 · <b>투과율 95% 이상</b>'),
        ('전극','주문 맞춤 · 모두 <b>연장형(extended)</b> 전극')]
ROT = ('내심','<b>360° 회전 PTFE</b> — 전극을 광창과 평행하게 정렬 후 외캡 조임')
AER = ('폭기','침지형 폭기 장치(aeration device) 장착 — 형상 선택 가능')
SEAL2 = ('밀폐·압력','완전 밀폐 — 밸브로 진공 <b>−100 kPa 미만</b> · 가압 <b>0.5 MPa 이하</b>')
PORT = ('시료채취 포트','추가 시 <b>59,000원</b> 별도')

OUT = []
def make(cfg):
    n, sz = B.build(cfg); OUT.append((cfg['slug'], n, sz))
def report():
    for slug, n, sz in OUT: print('%-24s 가격행 %2d · %d bytes' % (slug, n, sz))
