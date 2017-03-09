from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.callback import CallbackBase
from ansible import constants as C

import os, urllib2, json, socket

class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'instana_change_callback'

    def __init__(self):
        super(CallbackModule, self).__init__()

        self.errors = 0

    def post_event(self, title, text, duration, severity):
        request = urllib2.Request("http://localhost:42699/com.instana.plugin.generic.event", json.dumps({
            'title': title,
            'text': text,
            'duration': duration,
            'severity': severity
        }))

        try:
            urllib2.urlopen(request, timeout=2)
        except Exception as e:
            self._display.warning('Could not send event to Instana agent: %s' % str(e))

    def v2_playbook_on_start(self, playbook):
        self.playbook = os.path.basename(playbook._file_name)
        self.post_event("Ansible playbook started",
          "Playbook '%s' started on '%s'" % (self.playbook, socket.gethostname()),
          0, -1)

    def v2_playbook_on_stats(self, stats):
        summarize_stat = {}
        for host in stats.processed.keys():
            summarize_stat[host] = stats.summarize(host)

        if self.errors == 0:
            status = "OK"
            severity = -1 
        else:
            status = "FAILED"
            severity = 1

        self.post_event("Ansible playbook finished",
          "Playbook '%s' finished on '%s' with status '%s':\nSummary: %s" % (self.playbook, socket.gethostname(), status, json.dumps(summarize_stat)),
          0, severity)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        severity = -1
        if ignore_errors:
            self.errors += 1
            severity = 1

        self.post_event("Ansible task failed",
          "Task '%s' from the playbook '%s' failed on '%s'" % (result._task, self.playbook, result._host.name),
          0, severity)

    def v2_runner_on_async_failed(self, result, ignore_errors=False):
        severity = -1
        if ignore_errors:
            self.errors += 1
            severity = 1

        self.post_event("Ansible task failed",
          "Asyncronous task '%s' from the playbook '%s' failed on '%s'" % (result._task, self.playbook, result._host.name),
          0, severity)

    def v2_runner_on_ok(self, result):
        self.post_event("Ansible task success",
          "Task '%s' from the playbook '%s' successfully ran on '%s'" % (result._task, self.playbook, result._host.name),
          0, -1)

    def v2_runner_on_skipped(self, result):
        self.post_event("Ansible task skipped",
          "Task '%s' from the playbook '%s' was skipped on '%s'" % (result._task, self.playbook, result._host.name),
          0, 0.5)

    def v2_runner_on_unreachable(self, result):
        self.post_event("Ansible host unreachable",
          "Task '%s' from the playbook '%s' cannot reach '%s'" % (result._task, self.playbook, result._host.name),
          0, 1)
