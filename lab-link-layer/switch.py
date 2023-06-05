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
    Switch().run()

if __name__ == '__main__':
    main()
