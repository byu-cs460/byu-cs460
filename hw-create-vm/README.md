# Install Linux on a VM

The point of this exercise is to install a Linux-based OS on a Virtual Machine
(VM) dedicated to the assignments for this class.  Using a VM is necessary for
the following reasons.  First, the virtual network framework we will be using
makes configuration changes to your network interfaces, which you don't want to
affect other applications on a working system.  Second, running the framework
requires root (administrator) privileges, which you typically don't want to use
to run applications on a more general system.

VirtualBox is the only VM platform that has been tested.  Another VM platform
(e.g., Parallels, VMware, UTM/Qemu) might work, but should be considered
experimental.  Also, you would need to adapt any of the instructions (below)
that are specific to VirtualBox to your chosen VM platform.  Note that
VirtualBox will not run on Apple M1/M2 hardware.  We have included a set of
_experimental_ instructions for running UTM/Qemu on M1/M2 laptops below.

In summary, you have the following choices for VM platform:

 - Install VirtualBox on your personal system, if supported by your
   architecture.
 - Use the VirtualBox software installed on the CS lab machines.
 - (Experimental) Use an alternate VM platform on your personal system.

Generally you might select almost any distribution of Linux.  However, for this
class I am asking that you use Debian because the framework has been tested in
this environment.


## VirtualBox (amd64 only)

1. Download and install
   [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

   Alternatively, you may use the VirtualBox that is already installed on the
   CS open lab machines.

2. Download the "netinst" (net install) image with amd64 architecture from
   [Debian](https://www.debian.org/releases/stable/debian-installer/).

3. Start VirtualBox, and click "New" to create a new VM.  Give the machine 2GB
   (2048 MB) of RAM and a dynamically-allocated hard drive with at least 20GB
   of disk space.  Using the default for the other options should be fine.
   Start the VM, and select the install image (`.iso` file) you downloaded when
   prompted for a startup disk.

4. Go through the installation using all the default options (you will have to
   explicitly select "yes" to write changes to disk), until you come to the
   "Software Selection" menu.  At that menu, un-check the "GNOME" box, and
   check the "LXDE" box. LXDE provides a lightweight desktop environment that
   demands less of your host system.  You will need to explicitly tell the
   installer to install GRUB to the hard drive.

5. Reboot the VM when prompted, then log in.

6. Open a terminal (`LXTerminal`) and run the following from the command line
   to temporarily become `root` (system administrator):

   ```
   $ su -
   ```

   From the `root` (`#`) prompt, add your user to the `sudo` group:

   ```
   # usermod -a -G sudo $USER
   ```

   Now log out of LXDE and log back in.  As a member of the `sudo` group, you
   will be able to run commands that require administrator privileges on a
   command-by-command basis using `sudo`, rather than working as the `root`
   user, which is discouraged.

7. On the host machine, select "Devices" from the VirtualBox menu, then select
   "Insert Guest Additions CD Image..."

8. Within the guest OS, open a terminal, and run the following from the command
   line to mount the CD volume:

   ```
   $ mount /media/cdrom
   ```

   Then run the following commands to build and install the VirtualBox Guest
   Additions for your VM:

   ```
   $ sudo apt install linux-headers-amd64 build-essential
   $ sudo sh /media/cdrom/VBoxLinuxAdditions.run
   ```

   This will allow you to do things like set up a shared drive between host and
   guest OS and use a shared clipboard.

9. Reboot your VM to have the changes take effect.

10. On the host machine, select "Devices" from the VirtualBox menu, then select
    "Shared Folders", then "Shared Folders Settings...".  Click the button to
    add a shared folder, then choose which host folder to share (e.g.,
    `/Users/$USER/VMshared`, where your actual username replaces
    `$USER`) and where it will mount on the guest filesystem (e.g.,
    `/home/$USER/host`).  Selecting both "Auto-mount" and "Make permanent" is
    recommended.  For more information see the
    [official documentation](https://docs.oracle.com/en/virtualization/virtualbox/6.0/user/sharedfolders.html).
 
11. From the prompt, add your user to the `vboxsf` (VirtualBox shared folders)
    group:

    ```
    $ sudo usermod -a -G vboxsf $USER
    ```

    Now log out of LXDE and log back in.  As a member of the `vboxsf` group,
    you will be able to access the folder `/Users/$USER/VMshared` (or
    whichever folder you selected) on the host from `/home/$USER/host` (or
    whichever mount point you selected) in the VM.

12. On the host machine, select "Devices" from the VirtualBox menu, then select
    "Shared Clipboard", then "Bidirectional". This will allow you to "copy" items
    from the host machine and "paste" them into the VM or vice-versa.

13. Run the following to remove some unnecessary
    packages from your VM:

    ```
    $ sudo apt purge libreoffice-{impress,math,writer,draw,base-core,core,help-common,core-nogui} xscreensaver
    $ sudo apt purge connman
    $ sudo apt autoremove
    ```

14. Disable the screen locker by doing the following:
    - Select "Preferences" then "Desktop Session Settings" from the menu.
    - Uncheck the box titled "Screen Locker," and click "OK".
    - Log out of LXDE and log back in.

15. Run the following to install a few packages that will be useful for you in
    this class:

    ```
    $ sudo apt install wireshark tcpdump
    $ sudo apt install python3-scapy python3-pip python3-pygraphviz virtualenv
    $ sudo apt install git tmux vim
    ```

    At the prompt "Should non-superusers be able to capture packets?" (for
    `wireshark`), select "No".

16. Run the following to give `tcpdump`, `wireshark`, and `dumpcap` targeted
    capabilities, so an unprivileged user can run them to sniff network packets
    without elevating to `root`:
    ```
    $ sudo setcap cap_net_raw=eip /usr/bin/tcpdump
    $ sudo setcap cap_net_raw=eip /usr/bin/wireshark
    $ sudo setcap cap_net_raw=eip /usr/bin/dumpcap
    ```

17. Install whatever other tools and utilities that you think will improve your
    development environment.  Please note that if you have configured shared folders
    as described above, you can use whatever development environment you have already
    installed on your host to manipulate files in `/home/$USER/host` or some
    subfolder thereof.  Thus, you do not have to develop within the VM itself if you
    do not want to.


## UTM/Qemu on MacOS (Experimental)

1. Install [Homebrew](https://brew.sh/).

2. Install qemu and utm:
   ```bash
   $ brew install utm qemu
   ```

3. Download the "netinst" (net install) image from
   [Debian](https://www.debian.org/releases/stable/debian-installer/).
   For M1/M2 hardware, use the arm64 architecture.  For anything else, use
   amd64.

4. Start UTM, then do the following:

   a. Click "Create a New Virtual Machine", then "Virtualize", then "Linux".

   b. Under "Boot ISO Image", click "Browse", then select the install image
      (`.iso` file) you downloaded.  Then click "Continue".

   c. Select 2048 MB RAM, then click "Continue".

   d. Specify at least 20GB, then click "Continue".

   e. Select a directory that will be shared between the guest OS and your VM.
      Then click "Continue".

   f. Click "Play".

5. Follow steps 4 through 6 from the [VirtualBox instructions](#virtualbox-amd64-only).
   Before rebooting (step 5), do the following to "remove" the install CD.
   Click the "Drive Image Options" button, select "CD/DVD (ISO) Image", then click
   "Eject".

6. Within the guest OS, open a terminal, and run the following from the command
   to install utilities for allowing the host to interact with the guest:

   ```bash
   $ sudo apt install spice-vdagent spice-webdavd
   $ sudo apt install nautilus
   ```

7. Reboot your VM to have the changes take effect.

8. From the menu, click "Accessories" then "Files" to open Nautilus.  Click
   "Other Locations", then "Spice client folder".  Then run the following from
    a terminal:

    ```bash
    $ ln -s /run/user/`id -u`/gvfs/dav+sd:host=Spice%2520client%2520folder._webdav._tcp.local ~/host
    ```

    By clicking "Spice client folder" in Nautilus, you mounted (i.e., made
    accessible) a special "drive" from which you can access your host's files
    over a protocol called WebDAV.  Because its default location is long and
    messy (`/run/user/...`), we used `ln -s` to create a symbolic link (i.e.,
    an alias) to that folder in your home folder, named simply "host".  That
    is, if you run the following:

    ```bash
    $ ls ~/host
    ```

    You should be able to see the directory contents in the corresponding
    directory on the host.

9. Follow steps 13 through 17 from the
   [VirtualBox instructions](#virtualbox-amd64-only).

10. If you prefer to develop on your host OS, and the WebDAV option seems slow,
    here is an alternate way to configure your setup:

    a. Run the following on your guest to install an SSH server:

       ```bash
       $ sudo apt install ssh
       ```

    b. Capture your IP address by running the following

       ```bash
       $ ip addr | awk '/^[[:space:]]+inet[[:space:]]/ { print $2 }' | sed -n '/^127/b;s:/[[:digit:]]\+::;
       ```

       This just basically picks the only non-loopback IP address and prints it
       out, minus its prefix (which we will learn about).

    c. Follow the instructions
       [here](https://github.com/kentseamons/byu-cs324-f2022/tree/master/contrib/vscode-setup),
       using the username you created for your VM and the IP address of your VM
       in place of "schizo.cs.byu.edu", in every instance.
