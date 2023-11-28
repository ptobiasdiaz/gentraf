#!/usr/bin/env python3

'''
    GenTraf: agent types
'''

import random
import logging
from typing import List

from agent import AUTH_TOKEN_HEADER, VALID_TOKEN, WRONG_TOKEN


class TestInfo:
    '''Wraps all info used by the SUT'''
    def __init__(self, url: str) -> None:
        self._url_ = url
        self._headers_ = {}
        self._blobs_ = []
        self._private_blobs_ = []

    @property
    def valid_headers(self):
        '''Return authenticated headers'''
        valid_headers = {AUTH_TOKEN_HEADER: VALID_TOKEN}
        valid_headers.update(self._headers_)
        return valid_headers

    @property
    def wrong_headers(self):
        '''Return wrong headers'''
        valid_headers = {AUTH_TOKEN_HEADER: WRONG_TOKEN}
        valid_headers.update(self._headers_)
        return valid_headers

    @property
    def last_blob(self) -> str:
        '''Get last POSTed blobId'''
        if self._blobs_:
            return self._blobs_[-1]
        return None

    @property
    def stored_blobs(self) -> List[str]:
        return self._blobs_

    @property
    def public_blob(self) -> str:
        blobs = list(set(self.stored_blobs) - set(self._private_blobs_))
        if not blobs:
            return None
        return random.choice(blobs)

    @property
    def private_blob(self) -> str:
        if not self._private_blobs_:
            return None
        return random.choice(self._private_blobs_)

    def new_blob(self, blobId: str) -> None:
        if blobId in self._blobs_:
            logging.warning(f'Blob {blobId} already added')
            return
        self._blobs_.append(blobId)

    def forget_blob(self, blobId: str) -> None:
        if blobId in self._blobs_:
            self._blobs_.remove(blobId)
        else:
            logging.warning(f'Remove unknown blobId: {blobId}')
        if blobId in self._private_blobs_:
            self._private_blobs_.remove(blobId)

    def make_blob_private(self, blobId: str) -> None:
        if blobId not in self._blobs_:
            logging.warning(f'Blob {blobId} unknown, cannot switch to private')
            return
        if blobId in self._private_blobs_:
            logging.warning(f'Blob {blobId} already private')
            return
        self._private_blobs_.append(blobId)

    def make_blob_public(self, blobId: str) -> None:
        if blobId not in self._blobs_:
            logging.warning(f'Blob {blobId} unknown, cannot switch to public')
            return
        if blobId not in self._private_blobs_:
            logging.warning(f'Blob {blobId} its public already')
        else:
            self._private_blobs_.remove(blobId)

    def endpoint(self, endpoint):
        '''Return full URL to a given endpoint'''
        return f'{self._url_}{endpoint}'

    def __str__(self):
        return f'last blob: {self.last_blob}'


class TestFailed(Exception):
    '''Raise if test fails'''
    def __init__(self, message: str) -> None:
        self._msg_ = message

    def __str__(self):
        return f'Test Failed: {self._msg_}'