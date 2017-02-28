Role Name
=========

Template a goss file to a system, run it, and remove it.

Requirements
------------

None

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------


    - hosts: servers
      roles:
         - { role: run_remove_goss, goss_file: tests/goss.yaml }

License
-------

GPL2

Author Information
------------------

Sean's havin' fun.
