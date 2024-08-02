# Commonly Experienced Cougarnet Issues - and How to Fix Them

 - "pkg\_resources.DistributionNotFound: The 'cougarnet==0.0.0' distribution
   was not found and is required by the application"

   Make sure you are building and installing cougarnet from a folder that is
   _outside_ your shared folder (i.e., a folder that is shared between you and
   the host using VirtualBox).  To fix things, do the following:

   1. Clone Cougarnet outside the shared folder.  For example:
      ```
      $ cd ~/
      $ git clone https://github.com/cdeccio/cougarnet
      ```

   2. Enter the directory, and build/install from there:
      ```
      $ cd cougarnet
      $ python3 setup.py build
      $ sudo python3 setup.py install
      ```
      Note that `~/` is the user's home directory, and I wouldn't expect this
      to be a shared folder.
