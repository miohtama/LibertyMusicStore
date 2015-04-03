Sentry installation with Ansible

Spinning up a virtual machine with full Sentry installation
------------------------------------------------------------------------

Ansible example installation to Python 2.7 virtual environment::

    virtualenv-2.7 ~/code/tatianastore/avenv
    source ~/code/tatianastore/avenv/activate
    pip install ansible

    # Install roles from Ansible Galaxy repository locally (no sudo needed)
    ansible-galaxy install --roles-path=`pwd`/galaxy Ansibles.build-essential ANXS.postgresql Stouts.foundation Stouts.nginx Stouts.sentry

Create an Ansible vault file with secrets. This file is encrypted and can be put under version control::

    cd ansible
    # You might want to remove the existing vault file
    ansible-vault create group_vars/all/secret.yml

Add in these variables to ``secret.yml``::

    mandrill_username: "Email you used to sign up to Mandrill"
    mandrill_api_key: "grab from Mandrill console"
    sentry_secret_key: "randomstringhere"

    sentry_admin_username: "admin"
    sentry_admin_email: "mikko@example.com"
    sentry_admin_password: "x"

Store vault password locally for subsequent Ansible runs::

    echo "yourvaultpass" >> ~/tatianastore-ansible-vault.txt

Spin up a new VM with Vagrant and deploy Sentry playbook on it::

    cd ansible
    vagrant up

Grab the public IP if your Vagrant box. Then add it to ``/etc/hosts`` on your computer::

    192.168.62.77 sentry.local

Then you can access the Vagrant Sentry site::

    https://sentry.local

Installing Sentry on a production server
-----------------------------------------

You need a sever with SSH access where you have a normal user with sudo access.

Create file ``hosts.ini``::

    # Inventory of LBC servers under Hetzner hosting
    [hetzner]
    sentry ansible_ssh_host=1.2.3.4 ansible_ssh_user=root sentry_hostname=sentry.libertymusicstore.net

Run::

    ansible-playbook --inventory-file=hosts.ini -e "sentry_hostname=sentry.libertymusicstore.net" sentry.yml

Please note that SSH'ing as root is not recommended.

Used roles

* `sentry <https://github.com/Stouts/Stouts.sentry>`_

* `postfix_mandrill borrowed from <https://github.com/analytically/hadoop-ansible>`_

* `postgresql <https://galaxy.ansible.com/list#/roles/512>`_
