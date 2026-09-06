# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,META
def D(s,i): return META[s]["det"][i]
def DETS(s,cap,frm=0):
    d=META[s]["det"][frm:]
    return figs([(f,cap) for f in d])
TUBE={"heading":"적용 연동펌프 튜브 (Peristaltic tubing)","head":["재질 (Material)","특성 (Features)","수명 (Service life)"],
 "rows":[["실리콘 (Silicone)","식품 등급 · 유연성 높음 · 사용 온도 −4℃ ~ +180℃ · 비부식성 액체용","≥200 h"],
  ["PharMed BPT","Saint-Gobain · FDA 규격 · 사용 온도 −51℃ ~ +132℃ · 약산·약염기 대응","≥1000 h"],
  ["Viton","MasterFlex · FDA 규격 · 사용 온도 −20℃ ~ +260℃ · 강산·강염기 대응","≥1000 h"]],
 "note":"튜브 수명은 상온 20℃·무가압 조건에서 순수를 연속 이송해 균열이 생길 때까지를 잰 값입니다. 매질·회전수·사용 환경에 따라 달라지며 회전수가 낮고 액성이 순할수록 길어집니다. 정량 정밀도를 유지하려면 튜브를 주기적으로 교체합니다."}
PTUBE_REL=('유체 이송: <a href="/product/">전 제품 통합 카탈로그</a> · <a href="/brands/runze/">Runze Fluid 전체</a> · '
 '<a href="/brands/leadfluid/pump-heads/">리드플루이드 펌프헤드</a> · <a href="/brands/leadfluid/tube-silicone/">연동펌프 실리콘 튜브</a> · '
 '<a href="/brands/leadfluid/tube-pharmed-bpt/">PHARMED BPT 튜브</a> · <a href="/contact/">견적·기술 문의</a>')
def PREL(e=''): return PTUBE_REL+e
PKW=KW+[["#연동펌프","/product/"],["#정량이송","/product/"]]
