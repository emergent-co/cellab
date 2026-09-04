# -*- coding: utf-8 -*-
"""중문 전용 신규 49종: 계열 / 슬러그 / 한국어 제품명 확정표.
슬러그는 기존 119종과 충돌하지 않게 손으로 정한다(자동 생성 금지)."""

# cn_id: (fam, slug, 한국어 제품명, 모델표기)
NEW = {
 '4232636':  ('P5-isostatic', 'isostatic-press-yp-24j',        '24톤 수동 등정압 압편기', 'YP-24J/S'),
 '11973566': ('P5-isostatic', 'isostatic-press-yp-30j',        '30톤 수동 등정압 압편기', 'YP-30J/S'),
 '11973601': ('P5-isostatic', 'isostatic-press-hdp-12j',       '12톤 전동 등정압 압편기', 'HDP-12J'),
 '4232870':  ('P5-isostatic', 'isostatic-press-hdp-24j',       '24톤 전동 등정압 압편기', 'HDP-24J'),
 '11973602': ('P5-isostatic', 'isostatic-press-hdp-30j',       '30톤 전동 등정압 압편기', 'HDP-30J'),
 '10361236': ('P5-isostatic', 'isostatic-press-hap-30j',       '30톤 자동 등정압 압편기', 'HAP-30J'),
 '6585427':  ('P5-isostatic', 'isostatic-press-hap-100j',      '100톤 전자동 등정압 압편기', 'HAP-100J'),
 '6585232':  ('P5-isostatic', 'isostatic-press-hap-65fj',      '65톤 분리형 자동 등정압 압편기', 'HAP-65FJ'),
 '6585264':  ('P5-isostatic', 'isostatic-press-hap-200fj',     '200톤 분리형 자동 등정압 압편기', 'HAP-200FJ'),
 '11973635': ('P5-isostatic', 'isostatic-press-hap-300fj',     '300톤 분리형 자동 등정압 압편기', 'HAP-300FJ'),

 '6552649':  ('P1-manual',    'pellet-press-yp-2',             '2톤 수동 분말 압편기', 'YP-2'),
 '6555350':  ('P2-digital',   'digital-pellet-press-yp-2s',    '2톤 디지털 수동 압편기', 'YP-2S'),
 '7168883':  ('P2-digital',   'digital-pellet-press-yp-15bs',  '15톤 디지털 2주 연장형 수동 압편기', 'YP-15BS'),

 '11931291': ('P3-electric',  'electric-pellet-press-hdp-24s', '24톤 전동 분말 압편기(정밀제어형)', 'HDP-24S'),

 '9482418':  ('P4-auto', 'automatic-pellet-press-hap-2s',   '2톤 자동 압편기(정밀제어형)', 'HAP-2S'),
 '9482436':  ('P4-auto', 'automatic-pellet-press-hap-10s',  '10톤 자동 압편기(정밀제어형)', 'HAP-10S'),
 '9482445':  ('P4-auto', 'automatic-pellet-press-hap-20s',  '20톤 자동 압편기(정밀제어형)', 'HAP-20S'),
 '9482454':  ('P4-auto', 'automatic-pellet-press-hap-30s',  '30톤 자동 압편기(정밀제어형)', 'HAP-30S'),
 '11932005': ('P4-auto', 'automatic-pellet-press-hap-100s', '100톤 자동 압편기(정밀제어형)', 'HAP-100S'),
 '9988356':  ('P4-auto', 'automatic-pellet-press-hap-65fs', '65톤 분리형 자동 압편기(정밀제어형)', 'HAP-65FS'),
 '10134317': ('P4-auto', 'automatic-pellet-press-hap-200fs', '200톤 분리형 자동 압편기(정밀제어형)', 'HAP-200FS'),
 '11933938': ('P4-auto', 'automatic-pellet-press-hap-10fs-glovebox', '10톤 글로브박스 분리형 압편기', 'HAP-10FS'),
 '11933912': ('P4-auto', 'automatic-pellet-press-hap-20fs-glovebox', '20톤 글로브박스 분리형 압편기', 'HAP-20FS'),
 '11933867': ('P4-auto', 'automatic-pellet-press-hap-30s-glovebox',  '30톤 글로브박스 분리형 압편기', 'HAP-30S'),
 '11933863': ('P4-auto', 'automatic-pellet-press-hap-40s-glovebox',  '40톤 글로브박스 분리형 압편기', 'HAP-40S'),
 '11375400': ('P4-auto', 'automatic-pellet-press-hap-60fs-glovebox', '60톤 글로브박스 분리형 압편기', 'HAP-60FS'),

 '11973506': ('P7-fluoro', 'fluorometer-press-ftp-80x', '80톤 전자동 형광(XRF) 압편기(정밀제어형)', 'FTP-80X'),

 '4234385':  ('P6-hot', 'hot-pellet-press-hpc-800d-300',  '300℃ 수동 일체형 가열 압편기', 'HPC-800D/D1/D2'),
 '10925877': ('P6-hot', 'hot-pellet-press-hpc-800eg',     '500℃ 수동 일체형 가열 압편기', 'HPC-800EG/FG'),
 '4234414':  ('P6-hot', 'hot-pellet-press-yph-800eg',     '500℃ 수동 분리형 가열 압편기', 'YPH-800EG/FG'),
 '11973636': ('P6-hot', 'hot-pellet-press-yph-800a',      '원형 수동 가열 압편기 300/500℃', 'YPH-800A/AG'),
 '4234664':  ('P6-hot', 'hot-pellet-press-hzt-800eg',     '500℃ 전자동 가열 압편기 폭 300mm', 'HZT-800EG'),
 '10377174': ('P6-hot', 'hot-pellet-press-hzt-800fg',     '500℃ 전자동 가열 압편기 폭 400mm', 'HZT-800FG'),
 '6596208':  ('P6-hot', 'hot-pellet-press-vh-25t',        '글로브박스 전용 가열 압편기', 'VH-25T'),

 '9361017':  ('P9-vacuum', 'vacuum-hot-press-vhp-200d', '진공 자동 열압기 VHP-200D', 'VHP-200D'),
 '10367006': ('P9-vacuum', 'vacuum-hot-press-vhp-300e', '진공 자동 열압기 VHP-300E', 'VHP-300E'),

 '11799064': ('Z-slicer', 'electrode-slicer-cms-20', '수동 전지 절편기', 'CMS-20'),

 '4235178':  ('D3-square', 'square-die-hmf-31-40',   '31–40mm 사각 압편 금형', 'HMF-D'),
 '6603324':  ('D3-square', 'square-die-hmf-151-200', '151–200mm 조립식 사각 금형', 'HMF-H'),
 '6635775':  ('D2-opening', 'opening-die-square-bidirectional-hmf', '사각 양방향 가압 분할형 금형', 'HMF'),

 '11195867': ('D1-cylindrical', 'cylindrical-die-hmy-j', '로봇암용 원형 압편 금형', 'HMY-J'),
 '6645850':  ('D4-special', 'special-die-flat-ptm',  '원형 평판 금형', 'PTM'),
 '6646007':  ('D8-fluorodie', 'fluorometer-die-plastic-ring-pt', 'XRF 형광 전용 플라스틱 링 금형', 'PT'),

 '6649119':  ('D6-hotdie', 'hot-die-hch-dj', '가열식 전지 가압 시험 금형', 'HCH-DJ'),
 '6649120':  ('D6-hotdie', 'hot-die-hch-x',  '원형 가열 금형 코어', 'HCH-X'),
 '6649121':  ('D6-hotdie', 'hot-die-hch-f',  '평판 가열 성형 금형', 'HCH-F'),

 '6647606':  ('D7-cellmold', 'button-cell-die-pmn-p',    '코인셀 평판 금형', 'PMN-P'),
 '6647724':  ('D7-cellmold', 'button-cell-die-hmn-solid', '전고체 전지 시험 금형(압력센서 내장)', 'HMN'),
 '6647766':  ('D7-cellmold', 'button-cell-die-pmt-q',    '전지 절편 금형', 'PMT-Q'),
}

# 중복 레코드(같은 제품이 두 카테고리에 중복 등재) — 페이지로 만들지 않는다
SKIP = {'11931171'}   # YP-15BS 중복(7168883과 동일)

PREFIX_EXTRA = {'P9-vacuum': 'vacuum-hot-press'}
CAT_EXTRA = {'P9-vacuum': 'prep'}
