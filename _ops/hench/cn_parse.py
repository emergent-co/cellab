# -*- coding: utf-8 -*-
"""중문 상세페이지 raw 텍스트 -> 라벨/값 dict. 라벨 어휘 기반(콜론 없음)."""
import re, json, io, os

MACH = """仪器型号 压力范围 压力换算 压强换算 油缸直径 活塞直径 活塞行程 油缸行程 油缸限位
压力表 压力精度 精度范围 压力稳定性 工作台直径 立柱数量 立柱加高 有效空间 外形尺寸 主机尺寸
设备尺寸 设备重量 主机重量 控制箱尺寸 控制箱重量 整体结构 配置说明 设备防护 加压方式 加压过程
加压段数 泄压方式 脱模压力 脱模方式 保压时间 保压时长 保温时间 补压设定 自动控制 智能操作
远程控制 设置方式 显示方式 设备屏显 屏幕显示 曲线谱图 数据管理 主机保护 限位保护 急停功能
被动安全 主动安全 安全配置 完成提醒 悬吊设计 环境温度 设备电源 设备功率 电机功率 加热范围
加热温度 加热功率 控温方式 控温精度 控温范围 控压精度 控压控温 降温方式 隔热方式 热板类型
上板加热 下板加热 加热芯材质 模具材质 模具尺寸 模具规格 模具种类 腔体尺寸 腔体材质 腔体深度
加高腔体 真空度 升温速率 行程""".split()
MACH += ['最 大压强', '最大压强', '腔体承受压强', '承受压强',
         '温控器控温', '加热平板', '手套箱材质', '工作室尺寸', '过渡仓尺寸',
         '真 空 度', '整机尺寸', '型 号', '型号', '电 源',
         '温控器尺寸', '控压控温精度', '控制面板', '触摸模块', '限位功能', '安全防护',
         '高温安全', '样品厚度', '冲切压力', '冲头材质', '加压上限', '控温方式', '底座宽度', '热压板尺寸', '热压板类型', '温控系统', '设备隔热', '压力安全', '速率模式', '模具温度', '切片尺寸', '接料盒', '标配刀头', '适配材料', '适配材', '冲头', '压杆硬度', '可冲气源', '夹层厚度', '长边',
         '整体成形式结构', '标配', '冷却方式', '传感器', '显示表', '面板', '钢环材质', '铝杯材质', '塑料环材质', '规格尺寸']

DIE = ['型 号','型号','模具材质','压头硬度','样品尺寸','腔体深度','外径尺寸','外形尺寸',
       '重 量','重量','加热温度','加热功率','控温精度','电源','功率','模具规格']

def _hits(t, vocab, need_space):
    pat = '|'.join(re.escape(x) for x in sorted(vocab, key=len, reverse=True))
    out = []
    for m in re.finditer('(' + pat + ')', t):
        s, e = m.start(), m.end()
        if need_space:
            if e >= len(t) or t[e] != ' ':
                continue
        if s > 0 and t[s-1] == ' ':
            continue          # 값 뒤 공백에 붙은 건 라벨 아님
        out.append((s, e, m.group(1)))
    # 겹침 제거
    res = []
    for s, e, l in out:
        if res and s < res[-1][1]:
            continue
        res.append((s, e, l))
    return res

def parse(raw):
    t = re.sub(r'\s+', ' ', raw or '').strip()
    if not t:
        return {}
    for vocab, sp in ((MACH, True), (DIE, False), (MACH, False)):
        hs = _hits(t, vocab, sp)
        if len(hs) >= (4 if sp else 3):
            o = {}
            for i, (s, e, l) in enumerate(hs):
                end = hs[i+1][0] if i+1 < len(hs) else len(t)
                v = t[e:end].strip(' :：')
                k = l.replace(' ', '')
                if k not in o and v:
                    o[k] = v
            return o
    return {}

_SPLIT = ['重量', '压杆硬度', '可冲气源', '夹层厚度', '切片尺寸', '接料盒', '标配刀头', '适配材料', '冲头', '热压板尺寸', '热压板类型', '温控系统', '设备隔热', '压力安全', '速率模式', '样品厚度', '控温方式', '控压控温精度', '温控器尺寸', '限位功能', '安全防护',
          '高温安全', '冲切压力', '控制面板', '触摸模块', '模具', '加']

def parse2(raw):
    o = parse(raw)
    out = {}
    for k, v in o.items():
        for lb in _SPLIT[:25]:
            i = v.find(lb)
            if i > 0:
                out.setdefault(lb, v[i + len(lb):].strip(' :：'))
                v = v[:i].strip()
        out[k] = v
    return out

if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    rows = json.load(io.open(os.path.join(d, 'hench_cn_raw.json'), encoding='utf-8'))
    out, bad = [], 0
    for r in rows:
        kv = parse2(r['raw'])
        if len(kv) < 3:
            bad += 1
        out.append({'id': r['id'], 'title': r.get('title',''), 'kv': kv, 'desc': re.sub(r'\s+', ' ', r.get('desc') or '').strip(),
                    'imgs': r.get('imgs') or []})
    io.open(os.path.join(d, 'hench_cn.json'), 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print('parsed', len(out), 'weak', bad)
    import collections
    c = collections.Counter()
    for o in out:
        c[len(o['kv'])] += 1
    print(sorted(c.items()))
