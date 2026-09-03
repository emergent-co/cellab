# -*- coding: utf-8 -*-
"""브랜드별 배송비 SSOT — 금액은 오직 여기에만 적는다.

overseas-pricing 스킬 §3.5. 다른 스크립트(build_web.py / add_buyrail.py /
mk_*_hub.py / cfg_*.py)는 숫자 리터럴을 쓰지 말고 이 모듈의 함수를 호출한다.

두 종류를 구분한다.
  s_in  : 고객이 내는 해외배송비(KRW, 주문당 1회, VAT 별도). None = 근거 없음 → "주문 시 안내"
  s_out : 제조사 출하배송비(제조사 통화). 원가 공식 ①의 (소비자가 + s_out) 자리.
          카탈로그에 개당 표기가 없으면 0 — '누락'이 아니라 '표기 없음'이라는 뜻이다.
"""

SHIPPING = {
    'gaossunion': dict(s_in=145_000, s_out=0, ccy='EUR',
                       src='사용자 확인', checked='2026-09-03'),
    'aida':       dict(s_in=145_000, s_out=0, ccy='USD',
                       src='사용자 확인 · 카탈로그에 개당 출하비 표기 없음', checked='2026-09-03'),
    'hefei':      dict(s_in=285_000, s_out=0, ccy='RMB',
                       src='사용자 확인', checked='2026-09-03'),
    'hench':      dict(s_in=None,    s_out=0, ccy='RMB',
                       src='미확정 — 견적 확보 전까지 "주문 시 안내"', checked='2026-09-03'),
}

# 국내 브랜드 — 배송비 행 자체가 없다(3% 상시할인 대상).
DOMESTIC = ('sh-scientific', 'leadfluid')

ASK = '주문 시 안내'


def is_overseas(brand):
    return brand in SHIPPING


def s_in(brand):
    """고객 해외배송비(원). 미등재·근거없음이면 None."""
    return SHIPPING.get(brand, {}).get('s_in')


def s_out(brand):
    """제조사 출하배송비(제조사 통화). 미등재면 0."""
    return SHIPPING.get(brand, {}).get('s_out', 0)


def label(brand):
    """화면에 찍을 배송비 문자열. 금액이 없으면 '주문 시 안내'."""
    v = s_in(brand)
    return ASK if v is None else '{:,}원'.format(v)


def total(brand, product_price):
    """1개 주문 합계 = 제품가격 + 배송비. 배송비 미확정이면 제품가격만."""
    v = s_in(brand)
    return product_price + (v or 0)


def small_lines(brand):
    """소액 판정선 (단품 판매 불가선, 합산 주문 권장선). 스킬 §3.5-3.
    배송비 미확정 브랜드는 종전 고정 기준(5만 / 30만)을 쓴다."""
    v = s_in(brand)
    if v is None:
        return (50_000, 300_000)
    return (v, v * 2)


def check(brand):
    """등재 여부 확인 — 등재 안 된 해외 브랜드를 조용히 0원으로 처리하지 않게 한다."""
    if brand in DOMESTIC:
        return None
    if brand not in SHIPPING:
        raise KeyError(
            "brand '%s' 가 _ops/shipping.py 에 없습니다. "
            "가격을 매기기 전에 배송비 행부터 추가하세요(스킬 §3.5-1)." % brand)
    return SHIPPING[brand]
