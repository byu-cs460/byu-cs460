#!/usr/bin/env python3

import re
import signal
import subprocess
import sys

LOG_PREFIX = r'^(?P<time>\d+\.\d+)\s+(?P<hostname>\S+)\s+'
LOG_START_RE = re.compile(LOG_PREFIX + r'START$')
LOG_STOP_RE = re.compile(LOG_PREFIX + r'STOP$')
LOG_FRAME_RECV_RE = re.compile(LOG_PREFIX + \
        r'Received frame on\s+(?P<intf>\S+): ' + \
        r'(?P<src>[0-9a-f]{2}(:[0-9a-f]{2}){5}) -> ' + \
        r'(?P<dst>[0-9a-f]{2}(:[0-9a-f]{2}){5})$')

NEXT_ITERATION_SLACK = 0.15 # 150 ms
MAX_INTERVAL = 0.5 # 500 ms

class Lab1Tester:
    cmd = []
    expected_observations = []

    def evaluate(self, iteration, time_seen, observations):
        if iteration >= len(self.expected_observations):
            # not evaluated
            return None

        solution = self.expected_observations[iteration]
        if solution is None:
            # not evaluated
            return None

        i = 0
        for expected_cat, expected_hostnames in solution:
            observed_hostnames = []
            num_hostnames = len(expected_hostnames)
            j = i
            for j in range(i, i + num_hostnames):
                if j >= len(observations):
                    break
                observed_cat, observed_hostname = observations[j]
                if observed_cat != expected_cat:
                    sys.stderr.write(('ERROR: Time %0.3f: ' + \
                            'Expected %d %s at %s, but observed %s at %s\n') % \
                            (time_seen, num_hostnames, expected_cat,
                                ', '.join(expected_hostnames),
                                observed_cat, observed_hostname))
                    return False
                observed_hostnames.append(observed_hostname)
            j += 1
            i = j

            expected_hostnames = sorted(expected_hostnames)
            observed_hostnames = sorted(observed_hostnames)
            if expected_hostnames != observed_hostnames:
                sys.stderr.write(('ERROR: Time %0.3f: ' + \
                        'Expected %s at %s, but observed %s at %s\n') % \
                        (time_seen, expected_cat,
                            ', '.join(expected_hostnames),
                            expected_cat, ', '.join(observed_hostnames)))
                return False

        if len(observations) > j:
            sys.stderr.write(('ERROR: Time %0.3f: ' + \
                    'Unexpected %s at %s\n') % \
                    (time_seen, observations[j][0], observations[j][1]))
            return False

        return True

    def evaluate_lines(self, lines):
        # initialize
        start_time = None
        max_time = None
        next_time = None
        iteration = None
        observations = None

        evaluated = 0
        success = 0

        for line in lines:
            m = LOG_START_RE.search(line)
            if m is not None:
                start_time = float(m.group('time')) + 1.0
                max_time = start_time + MAX_INTERVAL
                next_time = start_time + (1 - NEXT_ITERATION_SLACK)
                iteration = 0
                observations = []
                continue

            cat = ''
            m = LOG_FRAME_RECV_RE.search(line)
            if m is not None:
                hostname = m.group('hostname')
                cat = 'FRAME'
            else:
                m = LOG_STOP_RE.search(line)
                if m is not None:
                    hostname = ''
                    cat = ''

            if m is not None:
                mytime = float(m.group('time'))

                while mytime > max_time:
                    if not observations:
                        # if we have gone through the loop more than once, then
                        # don't reduce by NEXT_ITERATION_SLACK
                        start_time = start_time + NEXT_ITERATION_SLACK
                        next_time = next_time + NEXT_ITERATION_SLACK

                    # evaluate
                    result = self.evaluate(iteration, start_time, observations)
                    if result is not None:
                        evaluated += 1
                        if result:
                            success += 1

                    # reset
                    iteration += 1
                    start_time = next_time

                    max_time = start_time + MAX_INTERVAL
                    next_time = start_time + (1.0 - NEXT_ITERATION_SLACK)
                    observations = []

                if not observations:
                    # if this is the first host seen, then save the time
                    start_time = mytime
                    max_time = start_time + MAX_INTERVAL
                    next_time = start_time + (1.0 - NEXT_ITERATION_SLACK)

                observations.append((cat, hostname))

        # evaluate
        result = self.evaluate(iteration, start_time, observations)
        if result is not None:
            evaluated += 1
            if result:
                success += 1

        return success, evaluated

    def run(self):
        p = None
        try:
            p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
            p.wait()
        except KeyboardInterrupt:
            p.send_signal(signal.SIGINT)
            p.wait()
            raise

        output = p.stdout.read().decode('utf-8')
        output_lines = output.splitlines()
        return self.evaluate_lines(output_lines)

class Scenario1(Lab1Tester):
    cmd = ['cougarnet', '--stop=22', '--disable-ipv6',
            '--terminal=none', 'scenario1.cfg']
    expected_observations = [
            [('FRAME', ['b', 'c', 'd', 'e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['c'])],
            [('FRAME', ['b', 'c', 'd', 'e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['c'])],
            None,
            None,
            [('FRAME', ['a'])],
            [('FRAME', ['b', 'c', 'd', 'e'])],
            ]

class Scenario2(Lab1Tester):
    cmd = ['cougarnet', '--stop=22', '--disable-ipv6',
            '--terminal=none', 'scenario2.cfg']
    expected_observations = [
            [('FRAME', ['b', 'c', 'd', 'e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['c'])],
            [('FRAME', ['b', 'c', 'd', 'e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['c'])],
            None,
            None,
            [('FRAME', ['a'])],
            [('FRAME', ['b', 'c', 'd', 'e'])],
            ]

class Scenario3(Lab1Tester):
    cmd = ['cougarnet', '--stop=22', '--disable-ipv6',
            '--terminal=none', 'scenario3.cfg']
    expected_observations = [
            [('FRAME', ['c', 'e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['c'])],
            [('FRAME', ['c', 'e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['e'])],
            [('FRAME', ['a'])],
            [('FRAME', ['c'])],
            None,
            None,
            [('FRAME', ['a'])],
            [('FRAME', ['c', 'e'])],
            ]

def main():
    try:
        for scenario in Scenario1, Scenario2, Scenario3:
            print(f'Running {scenario.__name__}...')
            tester = scenario()
            success, total = tester.run()
            sys.stderr.write(f'  Result: {success}/{total}\n')
    except KeyboardInterrupt:
        sys.stderr.write('Interrupted\n')

if __name__ == '__main__':
    main()
