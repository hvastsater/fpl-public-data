"""Compare explicitly supplied transfer packages. Offline; never fetches FPL data.

Input: {squad:[{id,position,team,sell_price}], bank, free_transfers,
rules:{hit_cost,max_per_club}, packages:[{id,transfers:[{out,in:{id,position,
team,buy_price,sell_price}}],gross_xp_gain:null, model:null,horizon_gws:[]}]}
All money is integer tenths of a million. No implied forecast or selling price.
"""
import json
import sys


def compare(data):
    squad = {p['id']: p for p in data['squad']}
    if len(squad) != 15 or len(data['squad']) != 15:
        raise ValueError('Need 15 unique players')
    if type(data['bank']) is not int or data['bank'] < 0:
        raise ValueError('Bank must be nonnegative integer tenths')
    if type(data['free_transfers']) is not int or data['free_transfers'] < 0:
        raise ValueError('Free transfers must be a verified nonnegative integer')
    rules = data['rules']
    if type(rules['hit_cost']) is not int or rules['hit_cost'] < 0:
        raise ValueError('Explicit current-season hit cost required')
    results = []
    packages = [{'id':'ROLL','transfers':[], 'gross_xp_gain':0, 'model':'baseline'}] + data['packages']
    for package in packages:
        current = dict(squad)
        bank = data['bank']
        errors = []
        sold, bought = set(), set()
        for transfer in package['transfers']:
            out, incoming = transfer['out'], transfer['in']
            if out not in squad or out in sold:
                errors.append('outgoing_missing_or_duplicate')
                continue
            if incoming['id'] in squad or incoming['id'] in bought:
                errors.append('incoming_already_owned_or_duplicate')
                continue
            sold.add(out)
            bought.add(incoming['id'])
            sell, buy = squad[out].get('sell_price'), incoming.get('buy_price')
            if type(sell) is not int or type(buy) is not int or sell < 0 or buy < 0:
                errors.append('missing_verified_prices_in_integer_tenths')
                continue
            bank += sell - buy
            del current[out]
            current[incoming['id']] = incoming
        positions = {position:sum(p['position']==position for p in current.values()) for position in ['GK','DEF','MID','FWD']}
        if positions != {'GK':2,'DEF':5,'MID':5,'FWD':3}:
            errors.append('invalid_squad_positions')
        if any(sum(p['team']==team for p in current.values()) > rules['max_per_club'] for team in {p['team'] for p in current.values()}):
            errors.append('club_limit_exceeded')
        if bank < 0:
            errors.append('unaffordable')
        hit = max(0,len(package['transfers'])-data['free_transfers'])*rules['hit_cost']
        gain = package.get('gross_xp_gain')
        if gain is not None and not package.get('model'):
            errors.append('forecast_source_missing')
        results.append({'id':package['id'],'feasible':not errors,'errors':errors,
                        'bank_after':bank if not errors else None,'hit_cost':hit,
                        'net_xp_gain_vs_roll':gain-hit if gain is not None and not errors else None,
                        'unused_current_free_transfers':max(0,data['free_transfers']-len(package['transfers'])),
                        'note':'No future FT accrual, chip rules or flexibility value assumed. Forecast inputs must cover the same horizon and lineup/minutes assumptions.'})
    return results


if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as stream:
        print(json.dumps(compare(json.load(stream)),indent=2))
