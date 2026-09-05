# -*- coding: utf-8 -*-
"""AIDA(天津艾达恒晟 · TianJin AIDA) 공통 — 판매가 산정.

스킬 `overseas-pricing` 공식 ①(해외 제품 · 제조사가 외화 가격을 준 경우) 적용.

    판매가 = (제조사가 + 제조사 출하배송비) × 환율계수 × 1.45
             → 1,000원 단위 반올림

· 제조사가   : products catalogue20260318.pdf 의 Ex-factory price (USD/pc)
· 출하배송비 : 카탈로그에 개당 표기 없음 → 0.
               고객이 내는 해외배송비(주문당 1회)는 별개 행이며 금액은 _ops/shipping.py 가 SSOT다.
· 환율계수   : 올림₁₀(스팟 × 1.02)   ※ 스킬 설명문 기준 (2026-09-02 사용자 확인)
               2026-09-02 스팟 USD/KRW 1,364 → 1,364 × 1.02 = 1,391.28 → 1,400
· 1.45       : 관세 + 수입 부가세 + 판매마진 10% + 국내 부가세 (고정 계수)

판매가를 여기서 완성해 넘기므로 각 cfg 는 landed=True 로 build_web 의 ×1.45 를
한 번 더 적용하지 않는다(이중 반올림 방지). 해외 라인이라 3% 이상 상시 할인 대상이 아니다.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import shipping as _ship   # 브랜드별 배송비 SSOT — overseas-pricing §3.5

USD_KRW = 1400     # 올림₁₀(1,364 × 1.02) — 2026-09-02 산출
K       = 1.45     # overseas-pricing 고정 계수
SHIP_IN = _ship.s_out('aida')      # 제조사 출하배송비 S_out (카탈로그 개당 표기 없음 → 0)

# 소액 판정선은 그 브랜드의 고객 해외배송비 기준 (스킬 §3.5-3)
SMALL, BUNDLE = _ship.small_lines('aida')

def w(usd):
    """USD 제조사가 → 원 판매가 (1,000원 단위 반올림, 한 번만 반올림)"""
    return int(round((usd + SHIP_IN) * USD_KRW * K / 1000.0)) * 1000

def rows(items):
    """[(모델, 규격, USD)] → [(모델, 규격, 원 판매가)]"""
    return [(m, s, w(u)) for m, s, u in items]

def lo(rs):
    """가격행 최저가 — 요약·설명 문구에 그대로 쓴다(표와 어긋나지 않게)"""
    return format(min(p for _, _, p in rs if p), ',')

def note(rs):
    """소액 주문 안내 — 스킬 §5. 해당하지 않으면 빈 문자열."""
    ps = [p for _, _, p in rs if p]
    if not ps: return ''
    if min(ps) < SMALL:
        return ('<b>%s원 미만 품목</b>은 단독 주문 시 해외배송비(%s)가 제품가격을 넘습니다. '
                '다른 품목과 <b>합산 주문</b>하시길 권합니다.' % (format(SMALL, ','), _ship.label('aida')))
    if min(ps) < BUNDLE:
        return ('<b>%s원 미만 소액 품목</b>은 다른 품목과 합산 주문하시면 배송비 부담이 줄어듭니다.'
                % format(BUNDLE, ','))
    return ''
