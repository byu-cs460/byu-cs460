#!/usr/bin/python3

import asyncio
from cougarnet.sim.host import BaseHost

class Switch(BaseHost):
    def __init__(self):
        super().__init__()

        # do any initialization here...

    def _handle_frame(self, frame: bytes, intf: str) -> None:
        print('Received frame: %s' % repr(frame))

def main():
    with Switch() as switch:

        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
        finally:
            loop.close()

if __name__ == '__main__':
    main()
