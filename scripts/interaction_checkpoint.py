"""Record a sanitized QA checkpoint in existing private state; no UI actions."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from setup import Deployment, deployment_lock, read_json, safe, save_json

STAGES = {'user_control', 'shell', 'native_initialization', 'native_targets', 'native_accessibility',
          'native_screenshot', 'native_input', 'browser_connection', 'browser_targets',
          'browser_observation', 'browser_input'}
STATUSES = {'pass', 'failed', 'unknown', 'not-required', 'stopped'}
STEP_STATUSES = {'pending', 'completed', 'failed', 'unknown-outcome'}


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', value):
        raise ValueError('Use an opaque lowercase ID; no paths, URLs or free text')
    return value


def validate(value):
    if not isinstance(value, dict) or set(value) != {'task_id', 'target_id', 'stages', 'steps'}:
        raise ValueError('Checkpoint requires task_id, target_id, stages and steps only')
    identifier(value['task_id'])
    identifier(value['target_id'])
    stages, steps = value['stages'], value['steps']
    if not isinstance(stages, dict) or not set(stages) <= STAGES:
        raise ValueError('Unsupported capability stage')
    for row in stages.values():
        if not isinstance(row, dict) or not {'status'} <= set(row) <= {'status', 'error_code'}:
            raise ValueError('Stage stores status and optional sanitized error_code only')
        if not isinstance(row['status'], str) or row['status'] not in STATUSES:
            raise ValueError('Invalid stage status')
        if 'error_code' in row:
            identifier(row['error_code'])
    if not isinstance(steps, list) or len(steps) > 100:
        raise ValueError('Use at most 100 step summaries')
    ids = set()
    for step in steps:
        if not isinstance(step, dict) or set(step) != {'id', 'status'}:
            raise ValueError('Steps store opaque id and status only')
        key = identifier(step['id'])
        if key in ids or not isinstance(step['status'], str) or step['status'] not in STEP_STATUSES:
            raise ValueError('Duplicate step ID or invalid status')
        ids.add(key)
    return value


def resume(value):
    validate(value)
    # Every resume needs a fresh observation; persisted pass never grants input.
    stopped = value['stages'].get('user_control', {}).get('status') == 'stopped'
    return {'status': 'user-resume-required' if stopped else 'observation-required',
            'target_id': value['target_id'],
            'reconcile_first': [s['id'] for s in value['steps'] if s['status'] == 'unknown-outcome'],
            'diagnose_first': [s['id'] for s in value['steps'] if s['status'] == 'failed'],
            'remaining': [s['id'] for s in value['steps'] if s['status'] == 'pending'],
            'limit': 'No automatic retry, permission grant or live-target validation. A recorded user stop requires fresh human authorization; never remove a tool interruption marker.'}


def record(state, value):
    validate(value)
    with deployment_lock(state):
        path = safe(state, 'routine-review.json')
        routine = read_json(path, None)
        if not isinstance(routine, dict):
            raise ValueError('Existing routine state is required; no second memory store')
        routine.setdefault('feedback_loop', {})['interaction_checkpoint'] = {
            **value, 'recorded_at': datetime.now(timezone.utc).isoformat()}
        save_json(path, routine)
    return resume(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['record', 'resume'])
    parser.add_argument('--input', type=Path, help='Reviewed sanitized checkpoint JSON')
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    state = args.state or Deployment().state
    if args.command == 'record':
        if not args.input:
            parser.error('record requires --input')
        result = record(state, read_json(args.input))
    else:
        routine = read_json(safe(state, 'routine-review.json'), {})
        value = routine.get('feedback_loop', {}).get('interaction_checkpoint')
        if not value:
            raise ValueError('No checkpoint; current interaction status is unknown')
        result = resume({k: v for k, v in value.items() if k != 'recorded_at'})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
