"""Decide from diagnosed current evidence; no UI calls, logging or permission grants."""
import json
import sys


REQUIRED = {
    'stage', 'failure_origin', 'technical_cause', 'cause_confirmed',
    'policy_state', 'permission_state', 'human_stop', 'runtime_stop', 'user_input_reserved',
    'target_kind', 'same_target_verified', 'browser_url_verified',
    'action_delivery', 'switch_already_attempted',
}
CAUSES = {'bootstrap_dependency_missing', 'runtime_initialization_failed',
          'tool_transport_refused', 'tool_transport_closed'}


def classify(evidence):
    def stop(reason):
        return {'decision': 'stop', 'reason': reason}
    if not isinstance(evidence, dict) or set(evidence) != REQUIRED:
        return stop('incomplete_or_unrecognized_evidence')
    booleans = ('cause_confirmed', 'human_stop', 'runtime_stop', 'user_input_reserved',
                'same_target_verified', 'browser_url_verified', 'switch_already_attempted')
    if any(type(evidence[key]) is not bool for key in booleans):
        return stop('invalid_evidence_types')
    if any(type(evidence[key]) is not str for key in REQUIRED.difference(booleans)):
        return stop('invalid_evidence_types')
    # Stops and uncertain authority always win over a simultaneous technical error.
    if evidence['human_stop'] or evidence['runtime_stop']:
        return stop('human_or_runtime_stop')
    if evidence['user_input_reserved']:
        return stop('desktop_reserved_for_user')
    if evidence['policy_state'] != 'allowed' or evidence['permission_state'] != 'granted':
        return stop('policy_or_permission_not_established')
    if evidence['stage'] not in ('initialization', 'connection'):
        return stop('not_an_initialization_or_connection_failure')
    if (evidence['failure_origin'] != 'tool_runtime'
            or evidence['technical_cause'] not in CAUSES or not evidence['cause_confirmed']):
        return stop('technical_runtime_cause_not_confirmed')
    if evidence['action_delivery'] != 'not_delivered':
        return stop('action_outcome_not_safe_to_repeat')
    if evidence['target_kind'] not in ('native', 'browser') or not evidence['same_target_verified']:
        return stop('same_target_not_established')
    if evidence['target_kind'] == 'browser' and not evidence['browser_url_verified']:
        return stop('browser_url_not_established')
    if evidence['switch_already_attempted']:
        return stop('no_driver_switch_loop')
    return {'decision': 'switch', 'reason': 'confirmed_technical_failure_with_existing_access',
            'next': 'verify_owned_runner_then_fresh_observation', 'max_switches': 1}


def main():
    raw = sys.stdin.read(8193)
    if len(raw) > 8192:
        result = {'decision': 'stop', 'reason': 'oversized_evidence'}
    else:
        try:
            result = classify(json.loads(raw))
        except (ValueError, TypeError):
            result = {'decision': 'stop', 'reason': 'invalid_json'}
    print(json.dumps(result))
    return 0 if result['decision'] == 'switch' else 2


if __name__ == '__main__':
    sys.exit(main())
