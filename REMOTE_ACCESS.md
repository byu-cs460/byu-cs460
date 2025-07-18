# Remote Access to CS Lab Machines

Throughout this class, you will be required to log on to a CS lab machine to
complete an assignment.  You are welcome to log on to a CS lab machine
directly, by sitting at a workstation in one of the labs.  However, you can
also access the lab machines remotely, which is often more convenient.  To log on
remotely, please follow these instructions.

Please note that access to the CS network and individual CS lab machines
requires that you are currently enrolled in a CS class.  If you are not
currently enrolled in a CS class, then you will not be granted access to the CS
network or individual lab machines.

 1. Access the CS network.

    To log on to a CS lab machine remotely, you must access the CS network.
    There are two ways to access the CS network:

    - *If you are in the TMCB*, simply connect to the "eduroam" WiFi.  If you
      are in the TMCB and you are currently enrolled in a CS class, then
      connecting to "eduroam" gives you access to the CS lab machines.

      Note that "eduroam" requires that you use your BYU credentials; that is,
      your BYU NetID and password.

    - *If you are outside the TMCB, including off-campus and other parts of
      campus*, [install the BYU CS VPN](https://cs-vpn.byu.edu/), if you
      haven't already.  Then connect to the BYU CS VPN by opening the software
      you installed and connecting to the VPN at "cs-vpn.byu.edu".

      Note that using the BYU CS VPN requires that you use your BYU
      credentials; that is, your BYU NetID and password.

 2. Log on to a CS Lab Machine Using SSH.

    At this point, you can access either an _arbitrary_ or a _specific_ CS lab
    machine remotely over SSH.

    - *Arbitrary lab machine.*  You can log on to an _arbitrary_ CS lab machine
      remotely over SSH by running the following from a terminal on your
      machine:

      (Replace "username" with your BYU CS username -- not your BYU NetID)

      ```bash
      ssh username@schizo.cs.byu.edu
      ```
      or simply:
      ```bash
      ssh username@schizo
      ```
      (There is some magic that automatically adds the "cs.byu.edu" suffix if
      you are on the CS network.)

      You can think of schizo as a load balancer for SSH.  That is, when you
      use schizo, you ultimately log on to _some_ CS lab machine.  Two
      consecutive connections to schizo might land you on two different lab
      machines.

      Note that your home directory is shared across all lab machines (using
      the network file server or NFS), so you can access the files in your
      home directory no matter which lab machine you log on to.

    - *Specific Lab Machine.*  A list of CS lab machines can be found
      [here](https://support.cs.byu.edu/KB/View/81187473).  You can log on to
      a _specific_ CS machine remotely over SSH by running the following:

      (Replace "username" with your BYU CS username -- not your BYU NetID.
      Also, replace "hostname" with the name of the machine to which you are
      logging on.  For example: "florida".)

      ```bash
      ssh username@hostname
      ```

    In addition to remote terminal access with the `ssh` command, you can also
    use `scp` (for copying files securely) and VS Code with the SSH Remote
    extension.

    For example:

    ```bash
    scp some/src/folder/myfile.txt shizo:some/dest/folder
    ```
