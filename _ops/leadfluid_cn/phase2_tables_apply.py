# -*- coding: utf-8 -*-
"""제조사 도판에서 읽어 한글로 옮긴 표를 기존 상세페이지에 삽입한다.
FAQ h2 앞에 <h2 class="pkg-h">…</h2><div class="pkg-tblwrap"><table class="pkg-tbl">…</table></div>
멱등: 마커 <!--cn-tbl--> 가 있으면 건너뛴다.
"""
import os, re, json, html, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = json.load(open(os.path.join(ROOT, '_ops/leadfluid_cn/phase2_tables_ko.json'), encoding='utf-8'))
MARK = '<!--cn-tbl-->'
HEADS = {'pump': D['_head_pump'], 'ef': D['_head_ef'], 'syr': D['_head_syr'],
         'kl40': D['_head_kl40'], 'fill': D['_head_fill']}
NOTE = {'pump': D['_note_pump'], 'ef': D['_note_pump'], 'syr': D['_note_syr'],
        'kl40': D['_note_pump'], 'fill': D['_note_pump']}

def build(v):
    head = HEADS[v['kind']]
    th = ''.join('<th>%s</th>' % html.escape(c) for c in head)
    tr = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % html.escape(c) for c in r) for r in v['rows'])
    return ('%s<h2 class="pkg-h">%s</h2><div class="pkg-tblwrap"><table class="pkg-tbl">'
            '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p class="pkg-note">%s 제조사 원문 도판(%s)에서 옮긴 값입니다.</p>'
            % (MARK, html.escape(v['h']), th, tr, html.escape(NOTE[v['kind']]), html.escape(v['src'])))

def main():
    dry = '--apply' not in sys.argv
    tot = {}; lines = []
    for slug, v in sorted(D.items()):
        if slug.startswith('_'):
            continue
        p = os.path.join(ROOT, 'brands/leadfluid', slug, 'index.html')
        if not os.path.exists(p):
            tot['NOFILE'] = tot.get('NOFILE', 0) + 1; lines.append('  %-12s NOFILE' % slug); continue
        h = open(p, encoding='utf-8').read()
        if MARK in h:
            tot['SKIP'] = tot.get('SKIP', 0) + 1; lines.append('  %-12s SKIP(이미 반영)' % slug); continue
        m = re.search(r'<h2[^>]*>\s*자주 묻는 질문', h)
        if not m:
            tot['NO_ANCHOR'] = tot.get('NO_ANCHOR', 0) + 1; lines.append('  %-12s NO_ANCHOR' % slug); continue
        h2 = h[:m.start()] + build(v) + h[m.start():]
        if not h2.rstrip().endswith('</html>'):
            tot['BROKEN'] = tot.get('BROKEN', 0) + 1; lines.append('  %-12s BROKEN' % slug); continue
        if not dry:
            open(p, 'w', encoding='utf-8').write(h2)
        tot['OK'] = tot.get('OK', 0) + 1
        lines.append('  %-12s OK  %-34s %d행' % (slug, v['h'][:32], len(v['rows'])))
    print(('[미리보기] ' if dry else '[적용] ') + str(tot))
    print('\n'.join(lines))

main()
