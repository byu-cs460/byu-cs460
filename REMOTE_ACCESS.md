# CS Lab Machine Remote Access

This document contains important information for accessing the CS lab machines
remotely.


## Remote Access

 - *If you are in the TMCB*, simply connect to the "eduroam" WiFi.

 - *If you are outside the TMCB, including off-campus and other parts of campus*:

   1. If you haven't already,
      [install the BYU CS VPN](https://docs.cs.byu.edu/doku.php?id=vpn-configuration-and-use).

   2. [Connect to the BYU CS VPN](https://docs.cs.byu.edu/doku.php?id=vpn-configuration-and-use).

   3. Once connected, follow the homework instructions as written. This
      includes `ssh`, `scp`, and VS Code with the SSH Remote extension.

   4. When you are done using the VPN, please disconnect.


 Once you are connected to the "eduroam" WiFi *or* you are connected to the BYU
 CS VPN, you may do any of the following to access resources on the BYU CS
 network:

 - Use `ssh` to gain remote terminal access to a specific
   [CS lab machine](https://docs.cs.byu.edu/doku.php?id=open-lab-layout)
   by its hostname.  For example:

   ```
   $ ssh nebraska 
   ```

 - Use `ssh` to gain remote terminal access to any of the
   [CS lab machines](https://docs.cs.byu.edu/doku.php?id=open-lab-layout)
   using `schizo`.  For example:

   ```
   $ ssh shizo 
   ```

 - Use `scp` to transfer files to and from your folder on the
   [CS lab machines](https://docs.cs.byu.edu/doku.php?id=open-lab-layout)
   using either a specific CS lab machine or `schizo.cs.byu.edu`.  For example:

   ```
   $ scp some/src/folder/myfile.txt shizo:some/dest/folder
   ```

  - Use VS Code with the SSH Remote extension to carry out remote command
    execution over SSH as part of your development environment.

## Other Options

If, for some reason, the remote access options listed above do not work for
you, here are two alternatives, each with their own limitations:

 - *Log on directly to one of the CS workstations.* Of course, this means that
   you need to be in the TMCB and develop on a CS workstation as opposed to
   developing on your laptop. But with this solution, you avoid all the troubles
   associated with remote login and authentication.

 - *Log on to one of the CS workstations for SSH-only access.*  To do this open
   a terminal on your system, and run

   ```
   ssh schizo.cs.byu.edu
   ```

   Then [follow the instructions](https://docs.cs.byu.edu/doku.php?id=remote-access-home#ssh-into-moat).
   It's fine to use the name "schizo" instead of "moat", so it stays consistent
   with all the homework instructions.  Please NOTE this solution is really for
   terminal access only and may not work with scp or VS Code.  Only use this
   option if the other options don't work and you're comfortable working in
   only a terminal with an editor like `vim`.
