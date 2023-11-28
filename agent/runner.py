#!/usr/bin/env python3

'''
    GenTraf: runner
'''


import time
import random
import logging
import threading
from typing import List, Tuple

import agent.actions
from agent.types import TestInfo, TestFailed


def _actions_():
    return [action for action in dir(agent.actions) if callable(getattr(agent.actions, action)) and not action.startswith("_") and action.startswith('test_')]


def _run_action_(action_name: str, test: TestInfo):
    action = getattr(agent.actions, action_name)(test)
    logging.debug(f"{action_name}({action.__doc__} with {test})")


class Runner(threading.Thread):
    '''Single request thread'''
    def __init__(self, test: TestInfo) -> None:
        super().__init__()
        self._actions_ = []
        self._test_ = test
        self._end_ = threading.Event()

    @property
    def samples(self) -> List[Tuple]:
        return self._actions_

    def stop(self):
        self._end_.set()

    def run(self):
        self._start_time_ = time.time()

        while not self._end_.is_set():
            if not self._test_.last_blob:
                action = 'test_upload_blob'
            else:
                action = random.choice(_actions_())

            action_start = time.time()
            try:
                _run_action_(action, self._test_)
                self._actions_.append((action, time.time() - action_start, None))
            except TestFailed as error:
                self._actions_.append((action, time.time() - action_start, str(error)))
        self._end_time_ = time.time()

    def results(self) -> List[Tuple]:
        return self._actions_

    def total_actions(self) -> int:
        return len(self._actions_)

    def failed_actions(self) -> int:
        return len([i for i in self.results() if i[1] != None])
