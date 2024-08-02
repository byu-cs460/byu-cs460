# Hands-On with the Transport Layer

The objectives of this assignment are to gain hands-on experience with TCP and
TCP Fast Open (TFO).


# Getting Started

## Install Dependencies

Make sure that `curl` is installed.

```
$ sudo apt install curl
```

## Update Cougarnet

Make sure you have the most up-to-date version of Cougarnet installed by
running the following in your `cougarnet` directory:

```
$ git pull
$ python3 setup.py build
$ sudo python3 setup.py install
```

Remember that you can always get the most up-to-date documentation for
Cougarnet [here](https://github.com/cdeccio/cougarnet/blob/main/README.md).


## Start the Network

File `h2-s1.cfg` contains a configuration file that describes a network with
two hosts, `a` and `b`, connected to switch `s1`.

Run the following command to create and start the network:

```bash
cougarnet --display --wireshark=a-s1 h2-s1.cfg
```


## Begin Packet Capture
Now go to the open Wireshark window, click the "Capture Options" button (the
gear icon).  Select the `s1-a` interface for packet capture.


# Part 1 - TCP Analysis of Large HTTP Response

Make sure the file `byu-y-mtn.jpg` is in the current directory.  Then run the
following command on host `b` to start an HTTP server listening:

```bash
b$ python3 -m http.server
```

On host `a` run the following:

```bash
a$ curl -o /dev/null http://10.0.0.2:8000/byu-y-mtn.jpg
```

This will request the file `byu-y-mtn.jpg` from 10.0.0.2 (host `b`) port 8000
and store it to `/dev/null` (nowhere).

Now go to the wireshark output.  You should see the control packets associated
with a TCP three-way handshake, followed by a TCP segment from 10.0.0.1
containing an HTTP GET request, followed by a bunch of ACK packets from
10.0.0.2.  Right-click on one of the packets, then hover over "Protocol
Preferences" in the menu that appears, then "Transmission Control Protocol".
Now _uncheck_ the box that says "Allow subdissector to reassemble TCP streams.
When "reassembling" is enabled, Wireshark combines all TCP segments associated
with a single HTTP response, which behavior is confusing when analyzing TCP.
Once unchecked, you should see the individual segments associated with separate
packets.

Now select "Statistics" from the Wireshark menu.  Then hover over "TCP Stream
Graphs" in the menu that appears.  Finally, click on "Time Sequence (Stevens").

In the graph, the each dot represents a TCP segment being sent by `b` (the HTTP
server responding to the HTTP request), the sequence number of which is the
y-value of the dot.  The almost-vertical stacks of dots represent TCP segments
that are sent back-to-back.  The "width" of a stack represents the time
required to transmit those segments--that is, the x-value of the last segment
in the stack minus the x-value of the first segment in the stack.  The
horizontal lines in between stacks represent the time in which the host is
waiting, idle, for in-flight bytes to be acknowledged before sending more.
Thus, initially, the length of these lines is very close to the round-trip time
(RTT), i.e., the time it takes for the segments to propagate to their
destination and the acknowledgments to propagate back to the sender.  

Answer the questions below:

 1. Beginning at time 0, when the first stack of segments (i.e., round 1) is
    issued, through the time the eighth stack of segments (i.e., round 8) is
    issued, how does the send window grow?  That is, how does the number of
    bytes (and segments) sent in round `i` compare to the number sent in round
    `i - 1`?

 2. Based on your response to the previous problem, what congestion control
    state would you say that the sender is in during the sending of these first
    8 rounds?

 3. How does the idle time change as the rounds increase?  Briefly explain why.

 4. Explain what the graph will look like if the current pattern holds.


# Part 2 - TCP Fast Open

This problem is an exercise to help you understand TCP Fast Open (TFO).  The
script `tfo_echo.py` can be run both as an echo client and an echo server,
depending on the presence of the `-l` option.  When the script is run with the
`-f` option, TFO is used.

Re-start your Wireshark capture.  Then run the following on host `b` to start
the echo server:

```bash
b$ python3 tfo_echo.py -l 5599
```

On host `a`, running the following to run the client:

```bash
a$ python3 tfo_echo.py 10.0.0.2 5599 foobar
```

Now answer the following questions about the packet capture:

 1. What were the relative sequence number and the segment length (i.e., the
    TCP payload) associated with the SYN packet?

 2. What was the relative acknowledgement number associated with the SYNACK packet?

 3. How many RTTs did it take for the string "echoed" by the server to be
    received by the client, including connection establishment?  (Note: don't
    actually add up the time; just think about and perhaps draw out the back
    and forth interactions between client and server.)

 4. Was there a TFO option in the TCP header?  If so, was there a cookie, and
    what was its value?

Now use `Ctrl`-`c` on host `b` to interrupt the running echo server.  Then run
the following on both host `a` and host `b`:

```bash
sudo sysctl net.ipv4.tcp_fastopen=3
```

Depending on the value passed to the `net.ipv4.tcp_fastopen` value, TFO might
be enabled for only when the host is acting as a TCP client, only when the host
is acting as a TCP server, or both.  The value 3 enables TFO from both a client
perspective _and_ a server perspective.

Restart the server on host `b` with the following command (note the presence of
the `-f` option):

```bash
b$ python3 tfo_echo.py -f -l 5599
```

Now run the client again on host `a` with the following command (note the
presence of the `-f` option):

```bash
a$ python3 tfo_echo.py -f 10.0.0.2 5599 foobar
```

For questions 5 - 8, answer the same questions as 1 - 4, but for the most
recent test.

Finally, run the following again:

```bash
a$ python3 tfo_echo.py -f 10.0.0.2 5599 foobar
```

For questions 9 - 12, answer the same questions as 1 - 4, but for the most
recent test.

Now, look in the `tfo_echo.py`, and answer the following question:

 13. What key differences are involved in programming a TFO connection (vs. a
     non-TFO TCP connection) from the perspective of the _client_.
