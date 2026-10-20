"""Offline FPL quality gates and decision evaluation. No network or account access."""
import argparse
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def parse_time(value):
    result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timezone required')
    return result


def audit(data, now):
    errors = []
    age = (now - parse_time(data['generated_at_utc'])).total_seconds() / 3600
    if age < 0 or age > 3:
        errors.append('snapshot_age_outside_0_to_3_hours')
    events = data.get('events', [])
    locked = max((e['id'] for e in events if parse_time(e['deadline_time']) <= now), default=None)
    if data.get('latest_locked_event') != locked:
        errors.append('latest_locked_event_missing_or_inconsistent')
    picks = data.get('entry_picks', {}).get(str(locked))
    if not picks or picks.get('entry_history', {}).get('event') != locked:
        errors.append('latest_locked_picks_missing_or_inconsistent')
    elif len(picks.get('picks', [])) != 15:
        errors.append('incomplete_squad')
    for rival in data.get('rivals', []):
        if rival.get('picks_gw') != locked or len(rival.get('picks') or []) != 15:
            errors.append('rival_picks_missing_or_mixed_gameweek')
            break
    if data.get('league', {}).get('has_next'):
        errors.append('league_pagination_incomplete')
    upcoming = min((e for e in events if parse_time(e['deadline_time']) > now), key=lambda e:e['deadline_time'], default=None)
    if upcoming and data.get('upcoming_event', {}).get('id') != upcoming['id']:
        errors.append('upcoming_event_inconsistent')
    return {'status': 'blocked' if errors else 'ok', 'errors': errors, 'age_hours': round(age, 2),
            'latest_locked_event': locked,
            'deadline_stockholm': parse_time(upcoming['deadline_time']).astimezone(ZoneInfo('Europe/Stockholm')).isoformat() if upcoming else None,
            'note': 'Technical consistency only; not source permission or private bank/FT verification.'}


def evaluate(snapshot, decision):
    gw = decision['gameweek']
    event = next((e for e in snapshot.get('events', []) if e['id'] == gw), {})
    if not (event.get('finished') and event.get('data_checked')):
        return {'status': 'waiting_for_official_finalization', 'gameweek': gw}
    picks = snapshot.get('entry_picks', {}).get(str(gw))
    if not picks or picks.get('entry_history', {}).get('event') != gw:
        return {'status': 'missing_actual_picks', 'gameweek': gw}
    history = picks['entry_history']
    result = {'status': 'actuals_available', 'gameweek': gw,
              'actual': {'gross_points': history['points'], 'transfer_cost': history['event_transfers_cost'],
                         'net_points': history['points'] - history['event_transfers_cost'],
                         'overall_rank': history.get('overall_rank'), 'picks': picks['picks'],
                         'chip': picks.get('active_chip')},
              'recommendation_was_executed': None, 'alternatives': [],
              'limitations': ['Observed picks do not prove which recommendation the user followed.',
                             'Realized points do not measure ex-ante decision quality.']}
    # Missing scores must never silently become zero. Only score pre-registered,
    # explicit effective multipliers; do not guess automatic substitutions.
    if snapshot.get('live_points_gw') == gw:
        points = snapshot.get('live_points', {})
        for alternative in decision.get('alternatives', []):
            effective = alternative.get('resolved_effective_picks')
            score = None
            if effective and len(effective) == 15 and all(isinstance(points.get(str(p['element'])), (int, float)) for p in effective):
                score = sum(points[str(p['element'])] * p['multiplier'] for p in effective) - alternative['transfer_cost']
            result['alternatives'].append({'id': alternative['id'], 'realized_net_points': score,
                                          'reason_if_null': None if score is not None else 'Missing scores or unresolved autosubs/captain fallback'})
    return result


def save_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--decision', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    data = json.loads(args.snapshot.read_text())
    result = evaluate(data, json.loads(args.decision.read_text())) if args.decision else audit(data, dt.datetime.now(dt.timezone.utc))
    if args.output:
        save_new(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
