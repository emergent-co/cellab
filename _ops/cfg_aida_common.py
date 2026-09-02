# -*- coding: utf-8 -*-
"""AIDA(天津艾达恒晟 · TianJin AIDA) 공통 — 카탈로그 USD → 원 정가 환산.

카탈로그: products catalogue20260318.pdf — Ex-factory price (USD/pc)
환산: 정가(원) = USD × USD_KRW, 1,000원 단위 반올림
      (리드플루이드 페이지가 쓰는 환산율과 같은 1,450을 따른다)
그 뒤 build_web 의 해외 발주 산식이 적용된다:
      제품가격 1개 = 정가 × 1.45  /  해외배송비 145,000원 / VAT 별도
"""
USD_KRW = 1450

def w(usd):
    """USD 정가 → 원 정가 (1,000원 단위 반올림)"""
    return int(round(usd * USD_KRW / 1000.0)) * 1000

def rows(items):
    """[(모델, 규격, USD)] → [(모델, 규격, 원정가)]"""
    return [(m, s, w(u)) for m, s, u in items]
