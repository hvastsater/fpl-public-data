#!/usr/bin/env python3
import datetime as dt, json, os, pathlib, random, time, urllib.request
BASE="https://fantasy.premierleague.com/api/"
ENTRY=6273717
LEAGUE=1286090
OUT=pathlib.Path("docs")
OUT.mkdir(exist_ok=True)
def get(path, optional=False):
    err=None
    for i in range(4):
        try:
            req=urllib.request.Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 FPL-public-data/1.0","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=25) as res:
                return json.load(res)
        except Exception as exc:
            err=exc
            if i<3: time.sleep(2**i+random.random())
    if not optional: raise RuntimeError(f"FPL API {path} unavailable: {err}")
    return None
def write(path,value):
    p=pathlib.Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n",encoding="utf-8")
now=dt.datetime.now(dt.timezone.utc)
base=get("bootstrap-static/")
fixtures=get("fixtures/")
profile=get(f"entry/{ENTRY}/")
history=get(f"entry/{ENTRY}/history/")
league=get(f"leagues-classic/{LEAGUE}/standings/")
events=base["events"]
assert events and base.get("elements") and isinstance(fixtures,list) and league.get("standings"), "Incomplete API data"
future=[e for e in events if e.get("deadline_time") and dt.datetime.fromisoformat(e["deadline_time"].replace("Z","+00:00"))>now]
next_gw=min(future,key=lambda e:e["deadline_time"]) if future else None
finished=max((e["id"] for e in events if e.get("finished")),default=None)
# After the deadline, FPL makes picks public even while the GW is still live.
# Never infer the current event only from the "finished" flag.
current=next((e["id"] for e in events if e.get("is_current")),None)
passed=[e["id"] for e in events if e.get("deadline_time") and dt.datetime.fromisoformat(e["deadline_time"].replace("Z","+00:00"))<=now]
latest_locked=max(passed,default=None)
recent_picks={}
for gw in sorted({g for g in [finished,current,latest_locked] if isinstance(g,int)}):
    pick=get(f"entry/{ENTRY}/event/{gw}/picks/",True)
    if pick: recent_picks[str(gw)]=pick
rows=league["standings"].get("results",[])
rivals=[]
for row in rows[:40]:
    rid=row.get("entry")
    if not isinstance(rid,int): continue
    item={"entry_id":rid,"entry_name":row.get("entry_name"),"rank":row.get("rank"),"total":row.get("total"),"event_total":row.get("event_total")}
    if latest_locked:
        picks=recent_picks.get(str(latest_locked)) if rid==ENTRY else get(f"entry/{rid}/event/{latest_locked}/picks/",True)
        if picks:
            item["picks"]=picks.get("picks")
            item["active_chip"]=picks.get("active_chip")
            item["picks_gw"]=latest_locked
    rivals.append(item)
    time.sleep(.1)
live=get(f"event/{latest_locked}/live/",True) if latest_locked else None
live_elements=live.get("elements",[]) if isinstance(live,dict) else []
live_points={str(p["id"]):p.get("stats",{}).get("total_points") for p in live_elements if isinstance(p,dict) and "id" in p}
pkeys=["id","web_name","team","element_type","now_cost","status","news","chance_of_playing_next_round","minutes","starts","total_points","form","selected_by_percent","expected_goals","expected_assists","expected_goals_per_90","expected_assists_per_90","penalties_order","corners_and_indirect_freekicks_order","direct_freekicks_order","transfers_in_event","transfers_out_event"]
players=[{k:p.get(k) for k in pkeys} for p in base["elements"]]
previous={}
try:
    previous={p["id"]:p for p in json.loads((OUT/"latest.json").read_text())["players"]}
except (FileNotFoundError,KeyError,ValueError): pass
changes=[{"id":p["id"],"name":p["web_name"],"from":previous[p["id"]]["now_cost"],"to":p["now_cost"]} for p in players if p["id"] in previous and previous[p["id"]].get("now_cost")!=p.get("now_cost")]
common={"generated_at_utc":now.isoformat(),"status":"ok","source":"Official public FPL JSON API","entry_id":ENTRY,"league_id":LEAGUE,"upcoming_event":{"id":next_gw["id"],"deadline_time_utc":next_gw["deadline_time"]} if next_gw else None,"last_finished_event":finished,"latest_locked_event":latest_locked,"current_event":current,"live_points_gw":latest_locked,"live_points":live_points,"is_latest_locked_event_finished":next((bool(e.get("finished")) for e in events if e.get("id")==latest_locked),None),"entry":profile,"entry_history":history.get("current",[]),"chips":history.get("chips",[]),"entry_picks":recent_picks,"league":{"name":league.get("league",{}).get("name"),"standings":rows,"has_next":league["standings"].get("has_next")},"rivals":rivals,"price_changes_since_previous_capture":changes,"limitations":["Pre-deadline unpublished transfers and exact current bank/FT are not public","Rivals' latest picks may not be available until after deadline","Not a source of press conference reports or independent projections"]}
latest={**common,"events":events,"fixtures":fixtures,"teams":base.get("teams",[]),"players":players}
write(OUT/"latest.json",latest)
wanted={p.get("element") for r in rivals for p in r.get("picks",[]) or []}
brief={**common,"relevant_players":[p for p in players if p["id"] in wanted]}
write(OUT/"brief.json",brief)
if latest_locked: write(OUT/"history"/f"gw{latest_locked}.json",brief)
print(f"OK {now.isoformat()} next={next_gw['id'] if next_gw else None} rivals={len(rivals)}")
