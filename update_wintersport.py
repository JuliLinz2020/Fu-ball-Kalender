"""Build Julian's combined winter-sport calendar (Python standard library only).

Run manually: python3 update_wintersport.py
The Thursday ChatGPT task additionally checks FIS, IBU and organizer schedules.
Never infer unannounced qualification dates or start times.
"""
import datetime as dt
import hashlib
import pathlib
import re
import urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = {'biathlon': 7747, 'ski-alpin': 7748, 'skispringen': 7749}
WM_URL = 'https://falun2027.com/en/here-is-the-competition-schedule-for-falun-2027-2/'
# Organizer schedule, checked 24 October 2026. Times Europe/Stockholm = Vienna.
WM = [
 ('20270225','1705','1845','Team Normalschanze (Damen)'),
 ('20270226','1530','1630','Qualifikation Normalschanze (Damen)'),
 ('20270226','1700','1830','Einzel Normalschanze (Damen)'),
 ('20270227','1630','1820','Mixed-Team Normalschanze'),
 ('20270228','1515','1620','Qualifikation Normalschanze (Herren)'),
 ('20270228','1645','1830','Einzel Normalschanze (Herren)'),
 ('20270304','1700','1845','Team Großschanze (Herren)'),
 ('20270305','1545','1645','Qualifikation Großschanze (Damen)'),
 ('20270305','1715','1845','Einzel Großschanze (Damen)'),
 ('20270306','1530','1630','Qualifikation Großschanze (Herren)'),
 ('20270306','1700','1845','Einzel Großschanze (Herren)'),
]

def esc(s):
    return s.replace('\\', '\\\\').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')

def unfold(s):
    return re.sub(r'\n[ \t]', '', s.replace('\r\n', '\n'))

def props(event):
    return {line.split(':',1)[0].split(';',1)[0]: line for line in event.splitlines() if ':' in line}

def fold(line):
    out = []
    current = ''
    for c in line:
        if len((current+c).encode('utf-8')) > 75:
            out.append(current)
            current = ' '
        current += c
    return '\r\n'.join(out+[current])

def build(feed_texts):
    feed_texts = dict(feed_texts)
    fis = feed_texts.pop('fis-skispringen')
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    events = {}
    counts = {}
    # Stable source UIDs; calendar contents are authored independently.
    for sport, text in feed_texts.items():
        n = 0
        for raw in re.findall(r'BEGIN:VEVENT\n(.*?)\nEND:VEVENT', unfold(text), re.S):
            p = props(raw)
            date = re.search(r':(\d{8})',p.get('DTSTART',''))
            if not date or not ('20261001' <= date[1] < '20270701'):
                continue
            title = p['SUMMARY'].split(':',1)[1]
            if sport == 'skispringen' and 'Quali' in title:
                continue  # Official FIS qualification dates take priority.
            if sport == 'skispringen' and ('Falun' in title or 'Weltmeisterschaft' in title):
                continue  # The direct organizer schedule below takes priority.
            key = p['UID'].split(':',1)[1]
            uid = hashlib.sha256((sport+':'+key).encode()).hexdigest()[:28]+'@julian-wintersport'
            lines = ['BEGIN:VEVENT','UID:'+uid,'DTSTAMP:'+stamp,p['DTSTART']]
            for name in ['DTEND','STATUS','SEQUENCE','LOCATION']:
                if name in p: lines.append(p[name])
            if 'SEQUENCE' not in p: lines.append('SEQUENCE:0')
            lines += ['SUMMARY:'+title,'CATEGORIES:'+esc({'biathlon':'Biathlon','ski-alpin':'Ski alpin','skispringen':'Skispringen'}[sport]),'TRANSP:TRANSPARENT']
            unknown = 'VALUE=DATE' in p['DTSTART']
            description = 'Eigener gemeinsamer Wintersportkalender. Terminbasis: Sportschau / calovo. Änderungen vorbehalten.'
            if unknown: description += ' Startzeit noch nicht bestätigt; deshalb vorläufig ganztägig.'
            lines += ['DESCRIPTION:'+esc(description),'URL:https://calovo.de/f/sportschau/'+sport,'END:VEVENT']
            events[uid] = (date[1],lines)
            n += 1
        if n < 10:
            raise ValueError('Too few events from '+sport+'; refusing incomplete replacement')
        counts[sport] = n
    qualifiers = 0
    for raw in re.findall(r'BEGIN:VEVENT\n(.*?)\nEND:VEVENT', unfold(fis), re.S):
        p = props(raw)
        title = p.get('SUMMARY','')
        if 'Qualification' not in title: continue
        date = re.search(r':(\d{8})',p['DTSTART'])[1]
        if not ('20261001' <= date < '20270701'): continue
        desc = p.get('DESCRIPTION','')
        gender = 'Damen' if 'Gender: Women' in desc else 'Herren' if 'Gender: Men' in desc else 'Mixed'
        place = p.get('LOCATION','LOCATION:').split(':',1)[1]
        uid = 'fis-'+p['UID'].split(':',1)[1]+'@julian-wintersport'
        lines = ['BEGIN:VEVENT','UID:'+uid,'DTSTAMP:'+stamp,'SEQUENCE:0',p['DTSTART'],
          'SUMMARY:'+esc('Skispringen – Qualifikation '+place+' ('+gender+')'),
          p.get('LOCATION','LOCATION:'+place),'CATEGORIES:Skispringen','TRANSP:TRANSPARENT','STATUS:TENTATIVE',
          'DESCRIPTION:'+esc('Terminquelle: FIS Weltcupkalender 2026/27. Startzeit noch nicht bestätigt; vorläufig ganztägig. Änderungen möglich.'),
          'URL:https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid='+p['UID'].split(':',1)[1][2:],'END:VEVENT']
        if 'DTEND' in p: lines.insert(5,p['DTEND'])
        events[uid] = (date,lines)
        qualifiers += 1
    if qualifiers < 10: raise ValueError('Missing FIS qualifications')
    counts['fis-qualifikationen'] = qualifiers
    for date,start,end,name in WM:
        uid = hashlib.sha256(('falun2027:'+name).encode()).hexdigest()[:28]+'@julian-wintersport'
        lines = ['BEGIN:VEVENT','UID:'+uid,'DTSTAMP:'+stamp,'SEQUENCE:0',
          'DTSTART;TZID=Europe/Berlin:'+date+'T'+start+'00',
          'DTEND;TZID=Europe/Berlin:'+date+'T'+end+'00',
          'SUMMARY:'+esc('Skispringen WM Falun – '+name),
          'LOCATION:Falun\, Schweden','CATEGORIES:Skispringen','TRANSP:TRANSPARENT',
          'STATUS:TENTATIVE','DESCRIPTION:'+esc('Quelle: offizieller Veranstalterzeitplan Falun 2027. Stand 24.10.2026. Änderungen möglich.'),
          'URL:'+WM_URL,'END:VEVENT']
        events[uid] = (date,lines)
    timezone = re.search(r'BEGIN:VTIMEZONE.*?END:VTIMEZONE',unfold(next(iter(feed_texts.values()))),re.S)
    if timezone is None: raise ValueError('Missing timezone')
    lines = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Julian Kaufmann//Wintersportkalender//DE',
      'CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:Julian – Wintersport',
      'X-WR-CALDESC:Skispringen\, Biathlon und Ski alpin – Damen\, Herren und Mixed. Wöchentliche Prüfung am Donnerstag.',
      'X-WR-TIMEZONE:Europe/Vienna','REFRESH-INTERVAL;VALUE=DURATION:P1D','X-PUBLISHED-TTL:P1D']
    lines += timezone[0].splitlines()
    for _, e in sorted(events.values(),key=lambda x:(x[0],x[1][1])): lines += e
    lines += ['END:VCALENDAR']
    result = '\r\n'.join(fold(line) for line in lines)+'\r\n'
    assert result.count('BEGIN:VEVENT') == len(events)
    assert len(events) == len(set(events))
    return result,counts

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--feed-directory',type=pathlib.Path)
    args = parser.parse_args()
    feeds = {}
    for sport,id_ in SOURCES.items():
        if args.feed_directory:
            feeds[sport] = (args.feed_directory/(sport+'.ics')).read_text()
        else:
            url = f'https://i.cal.to/ical/{id_}/sportschau/{sport}/12345.12345-54321.ics'
            with urllib.request.urlopen(url,timeout=45) as r: feeds[sport] = r.read().decode('utf-8-sig')
    if args.feed_directory:
        feeds['fis-skispringen'] = (args.feed_directory/'fis-skispringen.ics').read_text()
    else:
        url = 'https://www.fis-ski.com/DB/services/public/icalendar-feed-fis-events.html?seasoncode=2027&sectorcode=JP&categorycode=WC'
        with urllib.request.urlopen(url,timeout=45) as r: feeds['fis-skispringen'] = r.read().decode('utf-8-sig')
    calendar,counts = build(feeds)
    (ROOT/'wintersport.ics').write_bytes(calendar.encode('utf-8'))
    print(counts, 'plus',len(WM),'WM events. Total:',calendar.count('BEGIN:VEVENT'))
