import socket
import subprocess

from pyroute2 import IPRoute
from pyroute2.netlink.rtnl import rtscopes
from pyroute2.netlink.exceptions import NetlinkError

from cougarnet.sys_helper.cmd_helper import sys_cmd_pid

class ForwardingTableNative:
    def __init__(self):
        self._ip = IPRoute()

    def add_entry(self, prefix: str, intf: str, next_hop: str) -> None:
        '''Add forwarding entry mapping prefix to interface and next hop
        IP address.'''

        if '/' not in prefix:
            if ':' in prefix:
                prefix += '/128'
            else:
                prefix += '/32'
        if next_hop is None:
            next_hop = ''
        if intf is None:
            intf = ''

        sys_cmd_pid(['add_route', prefix, intf, next_hop], check=True)

    def remove_entry(self, prefix: str) -> None:
        '''Remove the forwarding entry matching prefix.'''

        if '/' not in prefix:
            if ':' in prefix:
                prefix += '/128'
            else:
                prefix += '/32'
        sys_cmd_pid(['del_route', prefix], check=True)

    def flush(self, family: int=None, global_only: bool=True) -> None:
        '''Flush the routing table.'''

        routes = self.get_all_entries(family=family, \
                resolve=False, global_only=global_only)

        for prefix in routes:
            self.remove_entry(prefix)


    def get_entry(self, address: str) -> tuple[str, str]:
        '''Return the subnet entry having the longest prefix match of
        address.  The entry is a tuple consisting of interface and
        next-hop IP address.  If there is no match, return None, None.'''

        try:
            route = self._ip.route('get', dst=address)[0]
        except (NetlinkError, IndexError):
            return None, None

        if 'attrs' not in route:
            return None, None
        attrs = dict(route['attrs'])
        if 'RTA_GATEWAY' in attrs:
            next_hop = attrs['RTA_GATEWAY']
        else:
            next_hop = None
        if 'RTA_OIF' in attrs:
            intf = socket.if_indextoname(attrs['RTA_OIF'])
        else:
            intf = None
        return intf, next_hop

    def get_all_entries(self, family: int=None,
            resolve: bool=False, global_only: bool=True):

        routes = self._ip.get_routes()
        entries = {}
        for route in routes:
            if 'attrs' not in route or \
                    'dst_len' not in route:
                continue
            if global_only and \
                    'scope' in route and \
                    route['scope'] != rtscopes['RT_SCOPE_UNIVERSE']:
                continue
            if family is not None and route['family'] != family:
                continue
            prefix_len = route['dst_len']
            attrs = dict(route['attrs'])
            if prefix_len == 0:
                if route['family'] == socket.AF_INET:
                    prefix = '0.0.0.0/0'
                else:
                    prefix = '::/0'
            elif route['family'] == socket.AF_INET and prefix_len == 32:
                prefix = attrs['RTA_DST']
            elif route['family'] == socket.AF_INET6 and prefix_len == 128:
                prefix = attrs['RTA_DST']
            else:
                prefix = f"{attrs['RTA_DST']}/{prefix_len}"
            if 'RTA_GATEWAY' in attrs:
                next_hop = attrs['RTA_GATEWAY']
            else:
                next_hop = None
            if 'RTA_OIF' in attrs:
                intf = socket.if_indextoname(attrs['RTA_OIF'])
            else:
                intf = None
            if resolve:
                if '/' not in prefix:
                    try:
                        prefix = socket.getnameinfo((prefix, 0), 0)[0]
                    except:
                        pass
                if next_hop is not None:
                    try:
                        next_hop = socket.getnameinfo((next_hop, 0), 0)[0]
                    except:
                        pass
            entries[prefix] = (intf, next_hop)
        return entries
