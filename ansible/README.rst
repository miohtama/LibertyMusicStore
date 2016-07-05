Ansible installation
--------------------

Create Python 2.7 venv.

Install ansible::

    pip install ansible

Install ansible requirements::

    ansible-galaxy install -r requirements.yml

Get vault file copy.

Play locally (may need to edit hosts.ini)::

    vagrant up
    ansible-playbook -i hosts.ini playbook-libertymusicstore.yml -l vagrant