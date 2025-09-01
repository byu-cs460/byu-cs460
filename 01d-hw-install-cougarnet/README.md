# Hands-On with Cougarnet

The objective of this assignment is to familiarize you with the Cougarnet
framework, which will be used for completing your lab assignments for this
class.


# Installation

## Install Dependencies

Use the following commands to install the build and run-time dependencies for
Cougarnet:

```bash
sudo apt install openvswitch-switch frr tmux python3-pyroute2 iptables lxterminal python3-pygraphviz libgraph-easy-perl tcpdump wireshark socat
```

## Install Cougarnet

Clone the Cougarnet repository, then build and install it using the following
commands.

*Important:*  These commands must be run _outside_ of any shared folders that
you have configured (see the [previous homework](../01a-hw-create-vm/)).

```bash
git clone https://github.com/cdeccio/cougarnet/
cd cougarnet
sudo pip3 install --root-user-action ignore --break-system-packages .
```


## Configure System

 1. Run the following to create the group `cougarnet` and add your user to it:

    ```bash
    sudo groupadd cougarnet
    sudo usermod -a -G cougarnet $USER
    ```

    Now log out of LXDE and log back in, so your user is a member of the
    `cougarnet` group.  The privileges associated with this group membership
    will be explained in the next instruction.

 2. Run the following to edit `/etc/sudoers.d/99-local`

    ```bash
    sudo visudo -f /etc/sudoers.d/99-local
    ```

    Note that `/etc/sudoers` is the configuration file for `sudo`.  On many
    systems, files in the directory `/etc/sudoers.d` are "included" by
    `/etc/sudoers`, and it is preferred to create local configuration (i.e.,
    overriding the default) in files in this directory, rather than modifying
    `/etc/sudoers` directly.  Finally, the proper way to to modify the `sudo`
    configuration (whether `/etc/sudoers` or an included file) is using the
    `visudo` command, as shown above.  This opens an editor (by default `nano`)
    to securely edit the file.

    Add the following contents to this file:

    ```
    %cougarnet  ALL=(ALL:ALL) NOPASSWD: /usr/local/libexec/cougarnet/syscmd_helper
    ```

    Exit `nano` by pressing `Ctrl`+`x`.

    This will allow members of the `cougarnet` group to run the command
    `/usr/local/libexec/cougarnet/syscmd_helper` as `root` using the `sudo`
    command, without prompting for a password (`NOPASSWD`).  The script
    `syscmd_helper` is a script that runs in connection with Cougarnet to
    execute privileged operations associated with virtual network creation and
    configuration.

 3. Configure the FRR routing daemon on your system:

    a. Open `/etc/frr/daemons` for editing using the following command:

       ```
       sudo -e /etc/frr/daemons
       ```
  
       
       Enable the BGP and RIP daemons by modifying the lines containing "bgpd",
       "ripd", and "ripngd" to have the value "yes" instead of "no" (e.g.,
       "bgpd=yes" instead of "no" (e.g., "bgpd=yes").

       Find the line containing the commented-out `frr_global_options` option.
       Immediately below that line, add the following line:

       ```
       frr_global_options="-w"
       ```

       This will pass the `-w` option to every routing daemon, so it will work
       properly with Cougarnet.

    b. Restart FRR by running the following:

       ```
       sudo systemctl restart frr.service
       ```


# Exercises

1. Look through the
   [Cougarnet documentation](https://github.com/cdeccio/cougarnet/blob/main/README.md).
   While much of it might not make sense just yet, you will be referring back
   to this as you work on the labs.

2. Complete the five
   [Working Examples](https://github.com/cdeccio/cougarnet/blob/main/README.md#working-examples)
