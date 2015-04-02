Ansible playbook goes here.

Ansible example installation to Python 2.7 virtual environment::

    virtualenv-2.7 ~/code/tatianastore/avenv
    source ~/code/tatianastore/avenv/activate
    pip install ansible

    ansible-galaxy install ANXS.postgresq

Testing out Sentry deploy to Virtualbox VM with Vagrant::

    cd ansible
    vagrant up

Roles

* `postfix_mandrill <https://github.com/analytically/hadoop-ansible>`_

* `postgresql <https://galaxy.ansible.com/list#/roles/512>`_
