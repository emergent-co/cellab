# -*- coding: utf-8 -*-
"""중문 사양을 기존 파이프라인이 읽는 영문 키 + 한국어 값으로 바꿔
hench_products.csv 를 갱신하고 신규 49종 행을 덧붙인다.

원본 영문 수집본은 hench_products_en.csv 로 보존한다.
값은 중문 우선(자기정합·최신 리비전), 중문에 없는 항목만 영문 원본으로 채운다.
"""
import csv, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import newmap

# 중문 한국어 라벨 -> 기존 파이프라인의 영문 스펙 키
CN2EN = {
 '모델': 'Instrument model',
 '압력 범위': 'Pressure range', '압력 환산': 'Pressure conversion', '압강 환산': 'Pressure conversion',
 '유압실린더 직경': 'Cylinder diameter', '피스톤 직경': 'Piston diameter',
 '피스톤 행정': 'Piston stroke', '실린더 행정': 'Cylinder stroke',
 '압력계': 'Pressure gauge', '압력 정밀도': 'Precision', '정밀도 범위': 'Accuracy range',
 '압력 안정성': 'Pressure stability', '작업대 직경': 'Table diameter',
 '기둥 수': 'Number of columns', '기둥 연장': 'Column extension',
 '유효 공간': 'Valid space', '외형 치수': 'Dimensions', '본체 치수': 'Host size',
 '장비 치수': 'Dimensions', '전체 치수': 'Dimensions', '장비 중량': 'Weight',
 '본체 중량': 'Host weight', '제어함 치수': 'Controller size', '제어함 중량': 'Controller weight',
 '온도컨트롤러 치수': 'Controller size',
 '구조': 'Overall structure', '구성 안내': 'Configuration description',
 '안전 방호': 'Safety protection', '가압 방식': 'Pressure mode', '가압 과정': 'Pressure process',
 '가압 단수': 'Number of pressurized sections', '가압 상한': 'Pressure upper limit',
 '감압 방식': 'Pressure relief die', '탈형 압력': 'Demoulding pressure', '탈형 방식': 'Demoulding mode',
 '보압 시간': 'Pressure holding time', '보온 시간': 'Heat holding time', '보압 보정': 'After compaction way',
 '자동 제어': 'Automatic control', '스마트 조작': 'Intelligent operation', '원격 제어': 'Remote control',
 '설정 방식': 'Setting method', '표시 방식': 'Display mode', '디스플레이': 'Screen display',
 '제어 패널': 'Control panel', '터치 모듈': 'Touch module', '압력 곡선': 'Pressure curve',
 '데이터 관리': 'Data management', '본체 보호': 'Host protection', '리미트 보호': 'Limit protection',
 '리미트 기능': 'Limit function', '비상정지': 'Emergency stop', '수동 안전장치': 'Passive safety',
 '능동 안전장치': 'Active safety', '안전 구성': 'Safety configuration', '고온 안전': 'High temperature safety',
 '완료 알림': 'Completion alarm', '현수 설계': 'Overall structure',
 '사용 환경온도': 'Ambient temperature', '전원': 'Power supply', '소비 전력': 'Equipment power',
 '출력': 'Equipment power', '모터 출력': 'Motor power',
 '가열 범위': 'Heating range', '가열 온도': 'Heating temperature', '가열 출력': 'Heating power',
 '가열 평판': 'Heating plate', '온도 제어 방식': 'Temperature control by thermostat',
 '온도 정밀도': 'Temperature control accuracy', '온도 범위': 'Heating range',
 '온도컨트롤러 범위': 'Intelligent temperature controller temperature range',
 '압력 제어 정밀도': 'Precision', '압력·온도 제어': 'Pressure and temperature control',
 '압력·온도 정밀도': 'Pressure and temperature control accuracy',
 '냉각 방식': 'Cooling method', '단열 방식': 'Heat insulation method', '열판 형식': 'Heating plate type',
 '상판 가열': 'Upper plate heating', '하판 가열': 'Lower plate heating',
 '가열 코어 재질': 'Heating core material',
 '금형 재질': 'Material', '금형 치수': 'Die size', '금형 규격': 'Mold specifications',
 '금형 종류': 'Mold type', '챔버 치수': 'Chamber size', '챔버 재질': 'Cavity material',
 '캐비티 깊이': 'Cavity depth', '챔버 연장': 'Chamber extension', '진공도': 'Vacuum degree',
 '승온 속도': 'Heating rate', '행정': 'Stroke', '최대 압강': 'Maximum pressure',
 '압두 경도': 'Indenter hardness',
 '시료 치수': 'Sample size', '시료 두께': 'Sample thickness', '외경 치수': 'Dimensions',
 '중량': 'Weight', '글로브박스 재질': 'Glovebox material', '작업실 치수': 'Chamber room size',
 '전실 치수': 'Antechamber size', '재질': 'Material', '규격 치수': 'Mold specifications',
 '펀칭 압력': 'Punching pressure', '펀치 재질': 'Punch material', '센서': 'Pressure sensor',
 '표시계': 'Pressure gauge', '패널': 'Panel', '베이스 폭': 'Base width', '열판 치수': 'Heating plate size', '온도 제어 시스템': 'Temperature control system', '단열': 'Heat insulation method', '압력 안전': 'Safety protection', '승온 속도 설정': 'Heating rate', '금형 온도': 'Dies heating temperature', '슬라이스 규격': 'Slice size', '수집함': 'Receiving box', '기본 툴헤드': 'Standard tool head', '적용 시료': 'Suitable material', '펀치': 'Punch material', '실린더 리미트': 'Cylinder limit protection', '주입 가능 가스': 'Purge gas', '중간층 두께': 'Sample thickness', '장변': 'Sample size', '챔버 내압': 'Maximum pressure',
}

# 표에 싣지 않을 중문 라벨(장황한 마케팅 서술)
CN_DROP = {'구성 안내', '스마트 조작', '데이터 관리', '본체 보호'}



# 중문 값이 들어온 항목의 영문 동의어 키는 함께 버린다(같은 칸이 두 번 나오는 것을 막는다)
SYN = {
 'Weight': ['Equipment weight', 'Net weight'],
 'Dimensions': ['Size', 'Machine size', 'Boundary dimension'],
 'Valid space': ['Effective space', 'Available space', 'Work space', 'Working space'],
 'Power supply': ['Device power supply', 'Voltage'],
 'Equipment power': ['Device power'],
 'Pressure gauge': ['Pressure gage', 'Pressure display'],
 'Screen display': ['Display mode', 'Display die', 'Device display'],
 'Pressure holding time': ['Holding time', 'Pressure holding'],
 'Precision': ['Accuracy'],
 'Overall structure': ['Design structure', 'Construction'],
 'Pressure mode': ['Pressure die', 'Press process'],
 'Material': ['Die material', 'Mold material', 'Mould material'],
 'Table diameter': ['Working table diameter'],
 'Piston stroke': ['Travel of piston', 'Travel ofpiston', 'Max. piston stroke'],
 'Number of columns': ['Columns'],
 'Cylinder stroke': ['Stroke'],
 'Maximum pressure': ['Pressure limit'],
}


# ── 제조사 중문 페이지의 명백한 오기 교정 ───────────────────────────────
# 근거를 함께 남긴다. 근거 없이 값을 만들지 않는다.
CORR = {
 # YP-60FS: 압력범위가 "0-35=4Mpa" 로 깨져 있다.
 # 같은 60T 기종 YP-60F 가 0-34MPa 이고, 이 페이지가 적은 환산 1MPa=1.76T 로도 60/1.76=34.1MPa 다.
 ('4229988', 'Pressure range'): ('0-60T(0-34MPa)', 'YP-60F 동일 사양 및 자체 환산계수 1MPa=1.76T'),
 # YP-30J/S: "0-30T/3.15Mpa" — 소수점 위치 오기. 자체 환산 1MPa=0.95T 로 30/0.95=31.6MPa.
 ('11973566', 'Pressure range'): ('0-30T/31.5MPa', '자체 환산계수 1MPa=0.95T'),
}

def cn_to_en(spec_ko, cid=None):
    """[(한국어라벨, 값)] -> {영문키: 한국어값}"""
    out = {}
    for k, v in spec_ko:
        if k in CN_DROP:
            continue
        ek = CN2EN.get(k)
        if not ek or ek in out:
            continue
        out[ek] = v
    # 분리형 기기: 제조사가 본체/제어함을 따로 적어 '무게·외형' 칸이 비는 것을 메운다
    if 'Weight' not in out:
        hw, cw = out.get('Host weight'), out.get('Controller weight')
        if hw:
            out['Weight'] = ('본체 %s + 제어함 %s' % (hw, cw)) if cw else hw
    for (c, k), (v, _why) in CORR.items():
        if c == cid and k in out:
            out[k] = v
    if 'Heating range' not in out and out.get('Intelligent temperature controller temperature range'):
        out['Heating range'] = out['Intelligent temperature controller temperature range']
    if 'Dimensions' not in out and out.get('Host size'):
        out['Dimensions'] = out['Host size']
    return out


def main():
    m = json.load(io.open(os.path.join(HERE, 'hench_master.json'), encoding='utf-8'))
    bys = {r['slug']: r for r in m['deployed']}
    src = os.path.join(HERE, 'hench_products.csv')
    bak = os.path.join(HERE, 'hench_products_en.csv')
    if not os.path.exists(bak):
        io.open(bak, 'w', encoding='utf-8-sig', newline='').write(
            io.open(src, encoding='utf-8-sig').read())
    # 재실행 대비: 항상 영문 원본에서 다시 시작한다
    io.open(src, 'w', encoding='utf-8-sig', newline='').write(
        io.open(bak, encoding='utf-8-sig').read())

    import fam as F   # 원본 CSV 기준 슬러그(불변)
    slug_of = {}
    for o in F.out:
        slug_of[id(o['row'])] = o['slug']

    n_over = 0
    for o in F.out:
        s = bys.get(o['slug'])
        if not s or not s['cn_id']:
            continue
        cn = cn_to_en(s['spec_ko'], s['cn_id'])
        if not cn:
            continue
        en = json.loads(o['row']['spec'])
        # 재질이 중문과 영문에서 어긋나면 같은 표의 경도 값도 영문에서 물려받지 않는다
        conflict = ('Material' in cn and 'Material' in en
                    and cn['Material'].split()[0] not in en['Material'])
        skip = {'Indenter hardness'} if conflict else set()
        for k in cn:
            skip.update(SYN.get(k, ()))
        merged = dict(cn)
        for k, v in en.items():                 # 중문에 없는 항목만 영문으로 채운다
            v = (v or '').strip()
            if len(v) < 3 or v.count('(') != v.count(')'):
                continue                        # 영문 수집본의 잘린 조각은 싣지 않는다
            if k not in merged and k not in skip:
                merged[k] = v
        o['row']['spec'] = json.dumps(merged, ensure_ascii=False)
        cm = (s.get('cn_model') or '').strip()
        if cm and '/' not in cm and cm != (o['row']['model'] or '').strip():
            o['row']['model'] = cm      # 영문판 모델 오기 교정(예: 40T기 YP-30 -> YP-40)
        n_over += 1

    # 원본 순서를 유지한 채 갱신본 기록
    fields = ['cat', 'name', 'model', 'url', 'imgs', 'nkv', 'cov', 'spec', 'ids', 'famx', 'slugx']
    out = []
    for o in F.out:
        r = dict(o['row'])
        # 이미 배포된 119장은 영문 원본으로 뽑은 슬러그를 그대로 고정한다.
        # (모델 표기를 중문으로 교정하면 자동 슬러그가 바뀌어 URL 이 깨진다)
        r['famx'] = o['fam']
        r['slugx'] = o['slug']
        out.append(r)

    bycn = {r['cn_id']: r for r in m['new']}
    n_new = 0
    for cid, (fm, slug, konm, model) in newmap.NEW.items():
        rec = bycn.get(cid)
        if not rec:
            continue
        sp = cn_to_en(rec['spec_ko'], cid)
        sp.setdefault('Instrument model', model)
        cat = '다이/몰드' if fm.startswith('D') else ('기타' if fm == 'Z-slicer' else '프레스')
        out.append({'cat': cat, 'name': konm, 'model': model,
                    'url': 'http://www.henchld.com/ProductDetail/%s.html' % cid,
                    'imgs': '', 'nkv': str(len(sp)), 'cov': '1.0',
                    'spec': json.dumps(sp, ensure_ascii=False), 'ids': '',
                    'famx': fm, 'slugx': slug})
        n_new += 1

    with io.open(src, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, '') for k in fields})
    print('중문 사양 반영 %d행 · 신규 %d행 · 총 %d행' % (n_over, n_new, len(out)))


if __name__ == '__main__':
    main()
