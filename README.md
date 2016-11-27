# Instana integration with Ansible

There are different integrations possibilities between Instana and Ansible. The first one that we have implemented is the ability to send events to Instana whenever a playbook starts, finishes, tasks fail, succeed or get skipped. Events automatically appear in the timeline the UI, stored in the history, and will be used for incidents, alerting and machine learning in the future.

In order to allow this integration, callback `callbacks/instana_change_callback.py` simply needs to be added to callbacks of your Ansible infrastructure. Also, Instana agent needs to be running on the hosts where playbooks get executed.

**Instana integrations with Ansible are Ansible 2.0 compatible only, versions prior to that are not supported.**
