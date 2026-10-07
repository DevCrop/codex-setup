"""Render one portable, sanitized RTK report from existing private evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path

from presentation import font_css
from setup import ROOT, Deployment, atomic, deployment_lock, read_json, safe, save_json
from tools import verify


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0 else None


def model(routine, installed, runtime):
    feedback = routine.get('feedback_loop', {})
    aggregate = feedback.get('rtk_aggregate', {})
    summary = aggregate.get('summary', {})
    inp, out = number(summary.get('total_input')), number(summary.get('total_output'))
    difference = inp - out if inp is not None and out is not None else None
    saved = number(summary.get('total_saved'))
    evidence = feedback.get('rtk_validation', {})
    identity = evidence.get('identity', {})
    harness = ROOT / 'scripts/verify_rtk.py'
    matches = (runtime.get('status') == 'pass' and evidence.get('status') == 'pass'
               and identity.get('binary_sha256') == installed.get('sha256')
               and identity.get('version') == runtime.get('version')
               and harness.is_file() and identity.get('harness_sha256') == hashlib.sha256(harness.read_bytes()).hexdigest())
    daily = []
    import re
    for date, row in sorted(aggregate.get('daily_by_date', {}).items()):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date) or not isinstance(row, dict):
            continue
        daily.append({'date': date, **{k: number(row.get(k)) for k in
                      ('commands', 'input_tokens', 'output_tokens')}})
    return {'input': inp, 'output': out, 'difference': difference, 'reported_saved': saved,
            'discrepancy': saved - difference if saved is not None and difference is not None else None,
            'commands': number(summary.get('total_commands')), 'daily': daily[-90:],
            'runtime_status': runtime.get('status', 'unknown'),
            'runtime_checks': number(evidence.get('check_count')) if matches else None,
            'runtime_evidence_reused': bool(matches),
            'runtime_checked_at': evidence.get('checked_at') if matches else None,
            'collected_at': aggregate.get('collected_at'),
            'binary_sha256': installed.get('sha256'),
            'actual_openai_token_savings': None, 'browser_review': 'not-verified'}


def render(data, now):
    def esc(value):
        return html.escape(str(value if value is not None else '미확인'))
    def fmt(value):
        return format(value, ',') if value is not None else '미확인'
    difference = data['difference']
    ratio = f"{100 * difference / data['input']:.1f}%" if data['input'] and difference is not None else '미확인'
    daily = []
    for row in data['daily']:
        inp, out = row['input_tokens'], row['output_tokens']
        diff = inp - out if inp is not None and out is not None else None
        pct = 100 * diff / inp if inp and diff is not None else None
        daily.append('<tr><td>' + esc(row['date']) + '</td>' + ''.join('<td class="num">' + fmt(v) + '</td>' for v in (row['commands'], inp, out, diff))
                     + '<td>' + (f'{pct:.1f}%' if pct is not None else '미확인') + '</td></tr>')
    discrepancy = ('산술 불일치 미확인' if data['discrepancy'] is None else
                   f"RTK 보고 절약값 {fmt(data['reported_saved'])}과 입력−출력 {fmt(difference)} 사이에 {fmt(data['discrepancy'])} 차이가 있습니다. 원인 미확인; 차이를 숨기거나 실제 토큰 절약으로 해석하지 않습니다.")
    rows = [('RTK 소유권·해시', data['runtime_status'], '현재 로컬 바이너리'),
            ('런타임 호출·종료·필수 증거', str(data['runtime_checks']) + '개 통과' if data['runtime_evidence_reused'] else '미확인 / 식별자 불일치', '기존 검증 시점의 한정된 범위'),
            ('OpenAI 전체 토큰·업무 시간', '미측정', '구독 효율 개선률 미입증')]
    values = {'FONT': font_css(), 'RTK_STATUS': esc(data['runtime_status']),
              'DIFFERENCE': fmt(difference), 'RATIO': ratio, 'COMMANDS': fmt(data['commands']),
              'CHECKS': fmt(data['runtime_checks']), 'DISCREPANCY': esc(discrepancy),
              'VERIFICATION_ROWS': ''.join('<tr>' + ''.join('<td>' + esc(x) + '</td>' for x in row) + '</tr>' for row in rows),
              'DAILY_ROWS': ''.join(daily) or '<tr><td colspan="6">수집 기록 없음</td></tr>',
              'IDENTITY': '<p>수집: ' + esc(data['collected_at']) + '</p><p>런타임 검증: ' + esc(data['runtime_checked_at']) + '</p><p>바이너리 SHA-256: <code>' + esc(data['binary_sha256']) + '</code></p>',
              'BROWSER_STATUS': '미검증', 'GENERATED': esc(now)}
    result = (ROOT / 'templates/rtk-status.html').read_text(encoding='utf-8')
    for key, value in values.items():
        result = result.replace('{{' + key + '}}', value)
    return result.encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    dep = Deployment(state=args.state)
    with deployment_lock(dep.state):
        routine = read_json(safe(dep.state, 'routine-review.json'), None)
        if not isinstance(routine, dict):
            raise ValueError('Existing private routine state is required')
        try:
            runtime = verify(dep.state)
        except (OSError, ValueError):
            runtime = {'status': 'unknown'}
        installed = read_json(safe(dep.state, 'tools-installed.json'), {}).get('rtk', {})
        data = model(routine, installed, runtime)
        now = datetime.now(timezone.utc).isoformat()
        output = safe(dep.state, 'reports/rtk-status.html')
        receipt = safe(dep.state, 'reports/rtk-status.evidence.json')
        previous = read_json(receipt, {})
        if output.exists() and hashlib.sha256(output.read_bytes()).hexdigest() != previous.get('artifact_sha256'):
            raise ValueError('Existing report ownership differs; preserve user edits')
        encoded = render(data, now)
        atomic(output, encoded)
        save_json(receipt, {'schema_version': 2, 'generated_at': now, 'data': data,
                           'template_sha256': hashlib.sha256((ROOT / 'templates/rtk-status.html').read_bytes()).hexdigest(),
                           'artifact_sha256': hashlib.sha256(encoded).hexdigest(),
                           'status': 'rendered-static-checks-only', 'browser_review': 'not-verified'})
    print(json.dumps({'status': 'rendered-static-checks-only', 'path': str(output),
                      'runtime_checks_reused': data['runtime_evidence_reused'], 'browser_review': 'not-verified'}))


if __name__ == '__main__':
    main()
