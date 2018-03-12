#!/usr/bin/env python3

import collections
import datetime
import io
import time
import requests

BUSES = {
    1913: [(7, 'C')],
    1166: [(7, 'D'), 91], #, 8, 29, 92],
    #3621: [12],
    3619: [200],
    3682: [9],
    2785: [8, 12],
}

STOPS = collections.defaultdict(lambda: 'undefined')

def getstops():
    routes = {i[0] if isinstance(i, tuple) else i for s in BUSES.values() for i in s}

    for route in routes:
        routeinfo = requests.get(f'http://realtimemap.grt.ca/Stop/GetByRouteId?routeId={route}').json()
        for i in routeinfo:
            stopid = int(i['StopId'])
            if stopid not in STOPS:
                STOPS[stopid] = i['Name']

def query():
    out = io.StringIO()

    for stop in BUSES:
        print(f'{stop} \x1b[2m{STOPS[stop]}\x1b[0m', file=out)
        for route in BUSES[stop]:
            prefix = ''
            if isinstance(route, tuple):
                prefix = route[1]
                route = route[0]

            stopinfo = requests.get(f'http://realtimemap.grt.ca/Stop/GetStopInfo?stopId={stop}&routeId={route}').json()
            times = []
            headsign = ''
            for i in stopinfo['stopTimes']:
                #if not i['VehicleId']:
                #    continue
                if not i['HeadSign'].startswith(prefix):
                    continue
                headsign = i['HeadSign'] or i['Name']
                if headsign.startswith(str(route)):
                    headsign = headsign[len(str(route)):]
                headsign = headsign.strip()

                if i['Minutes'] == 0:
                    times.append('\x1b[1;33mdue\x1b[0m')
                elif i['Minutes'] <= 5:
                    times.append(f"\x1b[1;33m{i['Minutes']}\x1b[0m min")
                else:
                    times.append(f"\x1b[1m{i['Minutes']}\x1b[0m min")

            if not times:
                continue
            print(f"\t{times[0]}\t{times[1] if len(times) > 1 else ''}\t", end='', file=out)
            print(f"\x1b[1m{route}\x1b[0m", end='', file=out)
            if not prefix:
                print(' ', end='', file=out)
            print(f"{headsign}", file=out)

        print('', file=out)

    return out.getvalue()


def main():
    getstops()
    while True:
        out = query()
        print('\x1bc')
        print(out)
        print(f"@ {datetime.datetime.now().isoformat(timespec='minutes')}")
        time.sleep(20)


if __name__ == '__main__':
    main()
