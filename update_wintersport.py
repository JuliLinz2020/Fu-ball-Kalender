"""Build Julian's combined winter-sport calendar (Python standard library only).

Run manually: python3 update_wintersport.py
The Thursday ChatGPT task additionally checks FIS, IBU and organizer schedules.
Never infer unannounced qualification dates or start times.
Second runs have stable child UIDs. Unknown start times are transparent all-day
markers, never estimated clock times. During the Thursday review, update the
verified ALPINE_SCHEDULES table from FIS / official organizer schedules.
Team-combination's second stage is labelled Slalom, not a second downhill.
Jumping round 2 is not automatically called the final (format can differ).
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


# Official FIS / organizer schedules checked 25 October 2026.
# FIS information-sheet tables explicitly give CET/CEST and local times; the
# values below are the CET/CEST (Europe/Berlin = Vienna) column, not host local.
# Match UID, date and title: if the source reschedules an event, fail closed to
# an unknown-time marker until the new official schedule has been checked.
# pdf_page_index is zero-based and retained for the weekly reviewer.
ALPINE_SCHEDULES = {'390adea0f863f49942b708c094eb@julian-wintersport': {'date': '20261024',
                                                     'summary': 'Ski Alpin Sölden Riesenslalom (Frauen)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid=131577',
                                                     'pdf_page_index': 2,
                                                     'source_checked': '2026-10-25'},
 'b738faaea0d856e7a76009b4a1eb@julian-wintersport': {'date': '20261025',
                                                     'summary': 'Ski Alpin Sölden Riesenslalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid=131578',
                                                     'pdf_page_index': 2,
                                                     'source_checked': '2026-10-25'},
 'e8ea6b47287d3c9e887a43cfdeea@julian-wintersport': {'date': '20261114',
                                                     'summary': 'Ski Alpin Levi Slalom (Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 4,
                                                     'source_checked': '2026-10-25'},
 '997548530441863740a1ae743893@julian-wintersport': {'date': '20261115',
                                                     'summary': 'Ski Alpin Levi Slalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 4,
                                                     'source_checked': '2026-10-25'},
 'efd5055e902c89120b9bdb2a3f71@julian-wintersport': {'date': '20261121',
                                                     'summary': 'Ski Alpin Gurgl Slalom (Frauen)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 6,
                                                     'source_checked': '2026-10-25'},
 '4bca58a1d6e06458ab50465ad127@julian-wintersport': {'date': '20261122',
                                                     'summary': 'Ski Alpin Gurgl Slalom (Männer)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 6,
                                                     'source_checked': '2026-10-25'},
 '7ef3faef4538a32de5b129954cef@julian-wintersport': {'date': '20261128',
                                                     'summary': 'Ski Alpin Killington Riesenslalom (Frauen)',
                                                     'first_time': '1530',
                                                     'second_time': '1830',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 8,
                                                     'source_checked': '2026-10-25'},
 '2a5b16ee64d38f7decafc396254c@julian-wintersport': {'date': '20261129',
                                                     'summary': 'Ski Alpin Killington Slalom (Frauen)',
                                                     'first_time': '1630',
                                                     'second_time': '1900',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 8,
                                                     'source_checked': '2026-10-25'},
 '64b60b15e948f22f7d1ca912f011@julian-wintersport': {'date': '20261129',
                                                     'summary': 'Ski Alpin Copper Mountain Riesenslalom '
                                                                '(Männer)',
                                                     'first_time': '1800',
                                                     'second_time': '2100',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 10,
                                                     'source_checked': '2026-10-25'},
 'b27ab2be7b7b3aa131b0c35d48d7@julian-wintersport': {'date': '20261205',
                                                     'summary': 'Ski Alpin Tremblant Riesenslalom (Frauen)',
                                                     'first_time': '1700',
                                                     'second_time': '2000',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 14,
                                                     'source_checked': '2026-10-25'},
 '2b310137b96d7e0f585753fe12a4@julian-wintersport': {'date': '20261206',
                                                     'summary': 'Ski Alpin Beaver Creek Riesenslalom '
                                                                '(Männer)',
                                                     'first_time': '1800',
                                                     'second_time': '2100',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 12,
                                                     'source_checked': '2026-10-25'},
 '58fa9338bc41ad7d7964dbb9281e@julian-wintersport': {'date': '20261206',
                                                     'summary': 'Ski Alpin Tremblant Riesenslalom (Frauen)',
                                                     'first_time': '1630',
                                                     'second_time': '1930',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 14,
                                                     'source_checked': '2026-10-25'},
 '65441efa4c973fd768e5d7b36eab@julian-wintersport': {'date': '20261212',
                                                     'summary': 'Ski Alpin Val dIsere Riesenslalom (Männer)',
                                                     'first_time': '0930',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 16,
                                                     'source_checked': '2026-10-25'},
 '8a868643eef0ac5da4eb88259e4d@julian-wintersport': {'date': '20261213',
                                                     'summary': 'Ski Alpin Val dIsere Slalom (Männer)',
                                                     'first_time': '0930',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 16,
                                                     'source_checked': '2026-10-25'},
 '10e7940d641ac6de1b9124135126@julian-wintersport': {'date': '20261220',
                                                     'summary': 'Ski Alpin St. Moritz Riesenslalom (Frauen)',
                                                     'first_time': '0930',
                                                     'second_time': '1230',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 20,
                                                     'source_checked': '2026-10-25'},
 '1ddf87ddc7f18d9d84e59e9edd23@julian-wintersport': {'date': '20261220',
                                                     'summary': 'Ski Alpin Alta Badia Riesenslalom (Männer)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 22,
                                                     'source_checked': '2026-10-25'},
 'db8996129c223fee8841fb1f1b57@julian-wintersport': {'date': '20261221',
                                                     'summary': 'Ski Alpin Alta Badia Slalom (Männer)',
                                                     'first_time': '1745',
                                                     'second_time': '2100',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 22,
                                                     'source_checked': '2026-10-25'},
 'ae83cd04a72c67ef67d365599852@julian-wintersport': {'date': '20261222',
                                                     'summary': 'Ski Alpin Courchevel Slalom (Frauen)',
                                                     'first_time': '1745',
                                                     'second_time': '2045',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 24,
                                                     'source_checked': '2026-10-25'},
 'b15fc7e9be72b9e5219c695f91e2@julian-wintersport': {'date': '20261223',
                                                     'summary': 'Ski Alpin Madonna di Campiglio Slalom '
                                                                '(Männer)',
                                                     'first_time': '1745',
                                                     'second_time': '2100',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 26,
                                                     'source_checked': '2026-10-25'},
 'f3043d462979a7f1095be3a4ec71@julian-wintersport': {'date': '20261228',
                                                     'summary': 'Ski Alpin Dachstein West / Gosau '
                                                                'Riesenslalom (Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 30,
                                                     'source_checked': '2026-10-25'},
 'd96b8b444f715d52ca7003998e69@julian-wintersport': {'date': '20261229',
                                                     'summary': 'Ski Alpin Dachstein West / Gosau Slalom '
                                                                '(Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 30,
                                                     'source_checked': '2026-10-25'},
 '72d48a5cb7ca32c8a41303c973d3@julian-wintersport': {'date': '20270102',
                                                     'summary': 'Ski Alpin Kranjska Gora Riesenslalom '
                                                                '(Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 32,
                                                     'source_checked': '2026-10-25'},
 '40ab371724ab9fb81003409c8c71@julian-wintersport': {'date': '20270103',
                                                     'summary': 'Ski Alpin Kranjska Gora Slalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 32,
                                                     'source_checked': '2026-10-25'},
 '0cc58804cdcba389edd282e7354e@julian-wintersport': {'date': '20270104',
                                                     'summary': 'Ski Alpin Flachau Riesenslalom (Frauen)',
                                                     'first_time': '1745',
                                                     'second_time': '2045',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 34,
                                                     'source_checked': '2026-10-25'},
 '767ad2ccf5cb1b7b027688369fbd@julian-wintersport': {'date': '20270105',
                                                     'summary': 'Ski Alpin Flachau Slalom (Frauen)',
                                                     'first_time': '1800',
                                                     'second_time': '2100',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 34,
                                                     'source_checked': '2026-10-25'},
 'ec36cd417f0359d68c20a71a51fb@julian-wintersport': {'date': '20270109',
                                                     'summary': 'Ski Alpin Adelboden Riesenslalom (Männer)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 38,
                                                     'source_checked': '2026-10-25'},
 'bd07422a69bb999a8f8726e62cb0@julian-wintersport': {'date': '20270110',
                                                     'summary': 'Ski Alpin Adelboden Slalom (Männer)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 38,
                                                     'source_checked': '2026-10-25'},
 '492e45bea07c510ae286d04227b6@julian-wintersport': {'date': '20270117',
                                                     'summary': 'Ski Alpin Wengen Slalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 40,
                                                     'source_checked': '2026-10-25'},
 'd73471faca04fd4211ae1938ae1d@julian-wintersport': {'date': '20270119',
                                                     'summary': 'Ski Alpin Kronplatz Riesenslalom (Frauen)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 44,
                                                     'source_checked': '2026-10-25'},
 '0a272874e0e8c6aeea7dfb2da532@julian-wintersport': {'date': '20270123',
                                                     'summary': 'Ski Alpin Jasna Riesenslalom (Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 48,
                                                     'source_checked': '2026-10-25'},
 '42e57040f2856b2e04dc2e50b816@julian-wintersport': {'date': '20270124',
                                                     'summary': 'Ski Alpin Kitzbühel Slalom (Männer)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 46,
                                                     'source_checked': '2026-10-25'},
 'ce7c3ad03add8fabe8628c3aa743@julian-wintersport': {'date': '20270124',
                                                     'summary': 'Ski Alpin Jasna Slalom (Frauen)',
                                                     'first_time': '0930',
                                                     'second_time': '1215',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 48,
                                                     'source_checked': '2026-10-25'},
 'c2169995c4e8b8eb0285c30fae34@julian-wintersport': {'date': '20270126',
                                                     'summary': 'Ski Alpin Schladming Riesenslalom (Männer)',
                                                     'first_time': '1745',
                                                     'second_time': '2045',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 50,
                                                     'source_checked': '2026-10-25'},
 '329868ff531cdbc9f688b1e10180@julian-wintersport': {'date': '20270127',
                                                     'summary': 'Ski Alpin Schladming Slalom (Männer)',
                                                     'first_time': '1745',
                                                     'second_time': '2045',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 50,
                                                     'source_checked': '2026-10-25'},
 '267f73873070b980db9178337349@julian-wintersport': {'date': '20270129',
                                                     'summary': 'Ski Alpin Kranjska Gora Riesenslalom '
                                                                '(Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 32,
                                                     'source_checked': '2026-10-25'},
 '80f05d1e022212e33918c8bd548e@julian-wintersport': {'date': '20270130',
                                                     'summary': 'Ski Alpin Kranjska Gora Slalom (Frauen)',
                                                     'first_time': '1030',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 32,
                                                     'source_checked': '2026-10-25'},
 'f88ce8e66c78b255f1eb552c8866@julian-wintersport': {'date': '20270130',
                                                     'summary': 'Ski Alpin Chamonix Slalom (Männer)',
                                                     'first_time': '0930',
                                                     'second_time': '1230',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 52,
                                                     'source_checked': '2026-10-25'},
 'e4a2f1098f16b793e29c38af3859@julian-wintersport': {'date': '20270209',
                                                     'summary': 'Ski Alpin Weltmeisterschaft 2027 '
                                                                'Crans-Montana (SUI) Team-Kombination '
                                                                '(Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/',
                                                     'pdf_page_index': None,
                                                     'source_checked': '2026-10-25'},
 '8092e274eaacb77a4dc559f4edb8@julian-wintersport': {'date': '20270210',
                                                     'summary': 'Ski Alpin Weltmeisterschaft 2027 '
                                                                'Crans-Montana (SUI) Team-Kombination '
                                                                '(Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/',
                                                     'pdf_page_index': None,
                                                     'source_checked': '2026-10-25'},
 '789fb15fc5223fb5d6239f661b73@julian-wintersport': {'date': '20270211',
                                                     'summary': 'Ski Alpin Weltmeisterschaft 2027 '
                                                                'Crans-Montana (SUI) Riesenslalom (Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/',
                                                     'pdf_page_index': None,
                                                     'source_checked': '2026-10-25'},
 'd80d30fde9e10787c25aa827d198@julian-wintersport': {'date': '20270212',
                                                     'summary': 'Ski Alpin Weltmeisterschaft 2027 '
                                                                'Crans-Montana (SUI) Riesenslalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/',
                                                     'pdf_page_index': None,
                                                     'source_checked': '2026-10-25'},
 'd4997443149f0d43cb5de9d77508@julian-wintersport': {'date': '20270213',
                                                     'summary': 'Ski Alpin Weltmeisterschaft 2027 '
                                                                'Crans-Montana (SUI) Slalom (Frauen)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/',
                                                     'pdf_page_index': None,
                                                     'source_checked': '2026-10-25'},
 '9ce9f56ee793d4ced6f1e420f419@julian-wintersport': {'date': '20270214',
                                                     'summary': 'Ski Alpin Weltmeisterschaft 2027 '
                                                                'Crans-Montana (SUI) Slalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1330',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/',
                                                     'pdf_page_index': None,
                                                     'source_checked': '2026-10-25'},
 '9cffe1e90acc8b591250d402d7c1@julian-wintersport': {'date': '20270306',
                                                     'summary': 'Ski Alpin Soldeu Riesenslalom (Frauen)',
                                                     'first_time': '0930',
                                                     'second_time': '1230',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 62,
                                                     'source_checked': '2026-10-25'},
 'f440bb72aba136940255899d8ee5@julian-wintersport': {'date': '20270307',
                                                     'summary': 'Ski Alpin Soldeu Slalom (Frauen)',
                                                     'first_time': '0930',
                                                     'second_time': '1230',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 62,
                                                     'source_checked': '2026-10-25'},
 '3dfb443bf8444e48114c0ecc6d49@julian-wintersport': {'date': '20270313',
                                                     'summary': 'Ski Alpin Åre Riesenslalom (Männer)',
                                                     'first_time': '1000',
                                                     'second_time': '1300',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 64,
                                                     'source_checked': '2026-10-25'},
 'a0352280063ea13edda7f7aa14ae@julian-wintersport': {'date': '20270314',
                                                     'summary': 'Ski Alpin Åre Slalom (Männer)',
                                                     'first_time': '0930',
                                                     'second_time': '1230',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 64,
                                                     'source_checked': '2026-10-25'},
 '58bfea79dbcc0ab5d1cb998ef580@julian-wintersport': {'date': '20270323',
                                                     'summary': 'Ski Alpin Sun Valley Riesenslalom (Frauen)',
                                                     'first_time': '1630',
                                                     'second_time': '1900',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 66,
                                                     'source_checked': '2026-10-25'},
 '1c1460fcc91c11c5fed27354b9d1@julian-wintersport': {'date': '20270324',
                                                     'summary': 'Ski Alpin Sun Valley Riesenslalom (Männer)',
                                                     'first_time': '1630',
                                                     'second_time': '1900',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 66,
                                                     'source_checked': '2026-10-25'},
 '71df73c4f6e7fa3ef0d06e2c45f7@julian-wintersport': {'date': '20270325',
                                                     'summary': 'Ski Alpin Sun Valley Slalom (Frauen)',
                                                     'first_time': '1600',
                                                     'second_time': '1900',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 66,
                                                     'source_checked': '2026-10-25'},
 '747b2c6694be08b10e10ced039ff@julian-wintersport': {'date': '20270325',
                                                     'summary': 'Ski Alpin Sun Valley Slalom (Männer)',
                                                     'first_time': '1700',
                                                     'second_time': '2000',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf',
                                                     'pdf_page_index': 66,
                                                     'source_checked': '2026-10-25'}}

# Explicit official jumping second-round times, only when independently verified.
# Unknown times remain transparent date-only markers; never assume +60 minutes.
JUMPING_SCHEDULES = {'5cc72e65595f4cef178072e8f5d9@julian-wintersport': {'date': '20261219',
                                                     'summary': 'Skispringen Engelberg HS 140 Einzel '
                                                                '(Frauen)',
                                                     'second_time': '1415',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.weltcup-engelberg.ch/de/tickets-events/programm',
                                                     'source_checked': '2026-10-25',
                                                     'status': 'TENTATIVE',
                                                     'time_status': 'PUBLISHED-PROVISIONAL',
                                                     'note': 'Vorläufige veröffentlichte Planzeit aus dem '
                                                             'offiziellen Veranstalterprogramm (indexierter '
                                                             'Stand vom 23.10.2026). Die direkt abrufbare '
                                                             'Seite liefert teilweise eine ältere '
                                                             'Programmfassung; deshalb als vorläufig '
                                                             'gekennzeichnet.'},
 'c2c7f60fbd831d44720447205fe3@julian-wintersport': {'date': '20261219',
                                                     'summary': 'Skispringen Engelberg HS 140 Einzel '
                                                                '(Männer)',
                                                     'second_time': '1710',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.weltcup-engelberg.ch/de/tickets-events/programm',
                                                     'source_checked': '2026-10-25',
                                                     'status': 'TENTATIVE',
                                                     'time_status': 'PUBLISHED-PROVISIONAL',
                                                     'note': 'Vorläufige veröffentlichte Planzeit aus dem '
                                                             'offiziellen Veranstalterprogramm (indexierter '
                                                             'Stand vom 23.10.2026). Die direkt abrufbare '
                                                             'Seite liefert teilweise eine ältere '
                                                             'Programmfassung; deshalb als vorläufig '
                                                             'gekennzeichnet.'},
 '691a6970daabd9e4b316e80e8fa4@julian-wintersport': {'date': '20261220',
                                                     'summary': 'Skispringen Engelberg HS 140 Einzel '
                                                                '(Männer)',
                                                     'second_time': '1710',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.weltcup-engelberg.ch/de/tickets-events/programm',
                                                     'source_checked': '2026-10-25',
                                                     'status': 'TENTATIVE',
                                                     'time_status': 'PUBLISHED-PROVISIONAL',
                                                     'note': 'Vorläufige veröffentlichte Planzeit aus dem '
                                                             'offiziellen Veranstalterprogramm (indexierter '
                                                             'Stand vom 23.10.2026). Die direkt abrufbare '
                                                             'Seite liefert teilweise eine ältere '
                                                             'Programmfassung; deshalb als vorläufig '
                                                             'gekennzeichnet.'},
 '800c91347fc27e1c57a26084443c@julian-wintersport': {'date': '20261220',
                                                     'summary': 'Skispringen Engelberg HS 140 Einzel '
                                                                '(Frauen)',
                                                     'second_time': '1430',
                                                     'timezone': 'Europe/Berlin',
                                                     'source_url': 'https://www.weltcup-engelberg.ch/de/tickets-events/programm',
                                                     'source_checked': '2026-10-25',
                                                     'status': 'TENTATIVE',
                                                     'time_status': 'PUBLISHED-PROVISIONAL',
                                                     'note': 'Vorläufige veröffentlichte Planzeit aus dem '
                                                             'offiziellen Veranstalterprogramm (indexierter '
                                                             'Stand vom 23.10.2026). Die direkt abrufbare '
                                                             'Seite liefert teilweise eine ältere '
                                                             'Programmfassung; deshalb als vorläufig '
                                                             'gekennzeichnet.'}}

FIRST_RUN_CORRECTIONS = {
    '65441efa4c973fd768e5d7b36eab@julian-wintersport',  # 20261212 Ski Alpin Val dIsere Riesenslalom (Männer)
    '8a868643eef0ac5da4eb88259e4d@julian-wintersport',  # 20261213 Ski Alpin Val dIsere Slalom (Männer)
    '3dfb443bf8444e48114c0ecc6d49@julian-wintersport',  # 20270313 Ski Alpin Åre Riesenslalom (Männer)
}


def value(p, name, default=''):
    return p.get(name, name + ':' + default).split(':', 1)[1]


def second_run_kind(p):
    """Return only explicitly eligible competition types, never qualifiers."""
    title = value(p, 'SUMMARY')
    low = title.casefold()
    if value(p, 'X-JULIAN-PHASE') == 'SECOND-RUN':
        return None
    if any(word in low for word in ('quali', 'training', 'gesamtwertung',
                                     'probedurchgang', 'probesprung')):
        return None
    if re.search(r'\b(?:2[.]?\s*(?:durchgang|lauf|run)|second run|run 2)\b', low):
        return None
    category = value(p, 'CATEGORIES')
    if category == 'Ski alpin':
        if 'team-kombination' in low:
            return 'combination'
        # Parallel is a knockout format, not the conventional two-run event.
        if 'parallel' not in low and ('riesenslalom' in low or
                                     re.search(r'\bslalom\b', low)):
            return 'alpine'
    if category == 'Skispringen':
        return 'jumping'
    return None


def second_run_uid(parent_uid):
    return hashlib.sha256(('second-run:' + parent_uid).encode()).hexdigest()[:28] + '@julian-wintersport'


def make_second_runs(parent_events, stamp):
    """Create date-only markers unless an independently verified time exists."""
    children = {}
    for raw in parent_events:
        p = props(raw)
        kind = second_run_kind(p)
        if not kind or value(p, 'STATUS') == 'CANCELLED':
            continue
        title = value(p, 'SUMMARY')
        match = re.search(r':(\d{8})', p.get('DTSTART', ''))
        if not match:
            continue
        date = match[1]
        parent_uid = value(p, 'UID')
        uid = second_run_uid(parent_uid)
        stage = 'Slalom (2. Teil)' if kind == 'combination' else '2. Durchgang'
        clock = source = None
        schedules = JUMPING_SCHEDULES if kind == 'jumping' else ALPINE_SCHEDULES
        official = schedules.get(parent_uid)
        if official and official['date'] == date and official['summary'] == title:
            clock, source = official['second_time'], official['source_url']
        lines = ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + stamp,
                 'SEQUENCE:1', 'RELATED-TO;RELTYPE=PARENT:' + parent_uid,
                 'X-JULIAN-PHASE:SECOND-RUN',
                 p.get('CATEGORIES', 'CATEGORIES:Wintersport'),
                 'TRANSP:TRANSPARENT']
        if 'LOCATION' in p:
            lines.append(p['LOCATION'])
        if clock:
            lines += ['DTSTART;TZID=Europe/Berlin:' + date + 'T' + clock + '00',
                      'STATUS:' + official.get('status', 'CONFIRMED'),
                      'X-JULIAN-TIME-STATUS:' + official.get('time_status', 'OFFICIAL-SCHEDULE'),
                      'SUMMARY:' + title + ' – ' + stage + (' – vorläufig' if official.get('status') == 'TENTATIVE' else '')]
            description = ('Separater ' + stage + '. Start laut offiziellem Zeitplan. '
                           'Geprüft am 25.10.2026. Änderungen durch Jury/Wetter möglich. '
                           'Keine bestätigte Endzeit angegeben.')
            if official.get('note'):
                description += ' ' + official['note']
        else:
            next_day = (dt.datetime.strptime(date, '%Y%m%d').date() + dt.timedelta(days=1)).strftime('%Y%m%d')
            lines += ['DTSTART;VALUE=DATE:' + date, 'DTEND;VALUE=DATE:' + next_day,
                      'STATUS:TENTATIVE', 'X-JULIAN-TIME-STATUS:UNCONFIRMED',
                      'SUMMARY:' + title + ' – ' + stage + ' – Uhrzeit offen']
            description = ('Terminmarker, kein ganztägiger Wettkampf. Startzeit des '
                           + stage + ' noch nicht verifiziert; Start nach dem ersten '
                           'Durchgang gemäß offiziellem Ablauf und Wetter. Keine '
                           'geschätzte Uhrzeit. Der Marker erhält nach Bekanntgabe '
                           'der Zeit dieselbe UID. Datum/Ort wie beim Haupttermin; '
                           'Änderungen möglich.')
            source = value(p, 'URL')
        if kind == 'jumping':
            description += (' Zweiter Wertungsdurchgang dieses Tages; nicht automatisch '
                            'Finaldurchgang. Je nach Wettkampfformat sind weitere '
                            'Durchgänge möglich; kein zweiter Qualifikationsdurchgang.')
        if kind == 'combination':
            description += ' Slalom-Teil der Team-Kombination, keine zweite Abfahrt.'
        lines += ['DESCRIPTION:' + esc(description)]
        if source:
            lines += ['URL:' + source]
        lines.append('END:VEVENT')
        children[uid] = (date, lines)
    return children


def correct_verified_first_runs(calendar):
    """Correct three checked start-time conflicts without changing event UIDs."""
    normalized = calendar.replace('\r\n', '\n')
    for raw in re.findall(r'BEGIN:VEVENT\n.*?\nEND:VEVENT\n?', normalized, re.S):
        p = props(unfold(raw))
        uid = value(p, 'UID')
        if uid not in FIRST_RUN_CORRECTIONS:
            continue
        official = ALPINE_SCHEDULES[uid]
        match = re.search(r':(\d{8})', p.get('DTSTART', ''))
        if not match or match[1] != official['date'] or value(p, 'SUMMARY') != official['summary']:
            continue
        expected = 'DTSTART;TZID=Europe/Berlin:' + official['date'] + 'T' + official['first_time'] + '00'
        if p.get('DTSTART') == expected:
            continue
        p['DTSTART'] = expected
        p['SEQUENCE'] = 'SEQUENCE:' + str(int(value(p, 'SEQUENCE', '0')) + 1)
        p['DTSTAMP'] = 'DTSTAMP:' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        p['URL'] = 'URL:' + official['source_url']
        p['DESCRIPTION'] = 'DESCRIPTION:' + esc('Start des 1. Durchgangs laut offiziellem FIS-Zeitplan 2026/27, geprüft 25.10.2026. Der zweite Durchgang ist separat eingetragen. Änderungen vorbehalten.')
        lines = []
        for line in unfold(raw).splitlines():
            if ':' in line:
                name = line.split(':',1)[0].split(';',1)[0]
                lines.append(p.pop(name, line))
            else:
                lines.append(line)
        # Original source events already contain all changed properties.
        new = '\n'.join(fold(line).replace('\r\n','\n') for line in lines) + '\n'
        normalized = normalized.replace(raw,new,1)
    return normalized.replace('\n','\r\n')


def add_second_runs_to_calendar(calendar, stamp=None, previous_calendar=None):
    """Add or refresh only owned second runs; preserve original events verbatim.

    Also usable for a surgical calendar refresh without fetching unrelated feeds.
    Stable UIDs survive a transition from unknown date-only marker to timed start.
    """
    stamp = stamp or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    normalized = correct_verified_first_runs(calendar).replace('\r\n', '\n')
    raw_events = re.findall(r'BEGIN:VEVENT\n.*?\nEND:VEVENT\n?', normalized, re.S)
    parents = []
    old_children = {}
    if previous_calendar:
        for prior_raw in re.findall(r'BEGIN:VEVENT\n(.*?)\nEND:VEVENT', unfold(previous_calendar), re.S):
            prior = props(prior_raw)
            if value(prior, 'X-JULIAN-PHASE') == 'SECOND-RUN':
                old_children[value(prior, 'UID')] = prior
    for raw in raw_events:
        p = props(unfold(raw))
        if value(p, 'X-JULIAN-PHASE') == 'SECOND-RUN':
            old_children[value(p, 'UID')] = p
            normalized = normalized.replace(raw, '', 1)
        else:
            parents.append(unfold(raw))
    children = make_second_runs(parents, stamp)
    additions = []
    for uid, (_, lines) in sorted(children.items(), key=lambda x: (x[1][0], x[0])):
        old = old_children.get(uid)
        if old:
            # Increment iCalendar sequence only for actual content changes.
            new_p = props('\n'.join(lines))
            ignored = {'DTSTAMP', 'SEQUENCE'}
            changed = {k:v for k,v in old.items() if k not in ignored} != {k:v for k,v in new_p.items() if k not in ignored}
            seq = int(value(old, 'SEQUENCE', '0')) + int(changed)
            lines = [('SEQUENCE:' + str(seq)) if l.startswith('SEQUENCE:') else l for l in lines]
        additions.extend(lines)
    body = '\n'.join(fold(line).replace('\r\n', '\n') for line in additions) + '\n'
    normalized = normalized.replace('END:VCALENDAR', body + 'END:VCALENDAR', 1)
    return normalized.replace('\n', '\r\n'), len(children)


def build(feed_texts, previous_calendar=None):
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
            if sport == 'ski-alpin' and p['UID'].split(':',1)[1] == '68b1e2812192a@7748.calovo':
                pass  # Historical source UID is not used for the override below.
            # FIS-confirmed delayed start; retain even if the secondary feed lags.
            if sport == 'ski-alpin' and date[1] == '20261024' and 'Sölden' in title and 'Frauen' in title:
                p['DTSTART'] = 'DTSTART;TZID=Europe/Berlin:20261024T103000'
                p.pop('DTEND', None)
                p['SEQUENCE'] = 'SEQUENCE:265'
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
    result, added = add_second_runs_to_calendar(result, stamp, previous_calendar)
    counts['zweite-durchgaenge'] = added
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
    previous = (ROOT/'wintersport.ics').read_text() if (ROOT/'wintersport.ics').exists() else None
    calendar,counts = build(feeds, previous)
    (ROOT/'wintersport.ics').write_bytes(calendar.encode('utf-8'))
    print(counts, 'plus',len(WM),'WM events. Total:',calendar.count('BEGIN:VEVENT'))

