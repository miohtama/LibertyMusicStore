Ansible playbook goes here.

Ansible example installation to Python 2.7 virtual environment::

    virtualenv-2.7 ~/code/tatianastore/avenv
    source ~/code/tatianastore/avenv/activate
    pip install ansible

    # Install roles from Ansible Galaxy repository locally (no sudo needed)
    ansible-galaxy install --roles-path=`pwd`/galaxy Ansibles.build-essential ANXS.postgresql Stouts.foundation Stouts.nginx Stouts.sentry

Create a vault file with secrets::

    cd ansible
    # You might want to remove the existing vault file
    ansible-vault create group_vars/all/secret.yml

    # Add in these variables
    # TODO

Store vault password locally::

    echo "yourvaultpass" >> ~/tatianastore-ansible-vault.txt

Spin up a new VM with Vagrant and deploy Sentry playbook on it::

    cd ansible
    vagrant up

Used roles

* `sentry <https://github.com/Stouts/Stouts.sentry>`_

* `postfix_mandrill <https://github.com/analytically/hadoop-ansible>`_

* `postgresql <https://galaxy.ansible.com/list#/roles/512>`_
