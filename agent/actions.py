#!/usr/bin/env python3

'''
    GenTraf: actions
'''

import json
import random
import tempfile
from pathlib import Path

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from agent import BLOBID_KEY, MULTIPART_FILE_KEY, BLOB_SIZES, PUBLIC_KEY
from agent.tools import generate_file
from agent.types import TestInfo, TestFailed


def test_upload_blob(test: TestInfo) -> None:
    '''POST to /api/v1/blob with valid AuthToken'''
    with tempfile.TemporaryDirectory() as workspace:
        file_to_post = Path(generate_file(workspace, random.choice(BLOB_SIZES)))
        fd = open(file_to_post, 'rb')
        encoder = MultipartEncoder(fields={
            MULTIPART_FILE_KEY: (file_to_post.name, fd, 'text/plain')
        })
        headers = test.valid_headers
        headers.update({'Content-Type': encoder.content_type})
        response = requests.post(test.endpoint('/api/v1/blob'), params=None, headers=headers, data=encoder)
        if response.status_code != 201:
            raise TestFailed(f'Expected status code 201, but got {response.status_code}')
        try:
            response = json.loads(response.text)
        except Exception as error:
            raise TestFailed(f'Cannot decode JSON data ({error})') from error
        try:
            blob_id = response[BLOBID_KEY]
        except KeyError:
            raise TestFailed(f'Response JSON does not have "{BLOBID_KEY}" key')
        test.new_blob(blob_id)
        fd.close()


def test_replace_blob(test: TestInfo) -> None:
    '''PUT to /api/v1/blob/<blobId> with valid AuthToken'''
    with tempfile.TemporaryDirectory() as workspace:
        blobId = random.choice(test.stored_blobs)
        file_to_post = Path(generate_file(workspace, random.choice(BLOB_SIZES)))
        fd = open(file_to_post, 'rb')
        encoder = MultipartEncoder(fields={
            MULTIPART_FILE_KEY: (file_to_post.name, fd, 'text/plain')
        })
        headers = test.valid_headers
        headers.update({'Content-Type': encoder.content_type})
        response = requests.put(test.endpoint(f'/api/v1/blob/{blobId}'), params=None, headers=headers, data=encoder)
        if response.status_code != 204:
            raise TestFailed(f'Expected status code 204, but got {response.status_code}')
        fd.close()


def test_delete_blob(test: TestInfo) -> None:
    '''DELETE to /api/v1/blob/<blobId> with valid AuthToken'''
    response = requests.delete(test.endpoint(f'/api/v1/blob/{test.last_blob}'), headers=test.valid_headers)
    if response.status_code != 204:
        raise TestFailed(f'Expected status code 204, but got {response.status_code}')
    test.forget_blob(test.last_blob)


def test_get_blobs(test: TestInfo) -> None:
    '''GET to /api/v1/blobs with valid AuthToken'''
    response = requests.get(test.endpoint(f'/api/v1/blobs'), headers=test.valid_headers)
    if response.status_code != 201:
        raise TestFailed(f'Expected status code 201, but got {response.status_code}')
    try:
        response = json.loads(response.text)
    except Exception as error:
        raise TestFailed(f'Cannot decode JSON data ({error})') from error

    if 'blobs' not in response:
        raise TestFailed(f'Response JSON does not have "blobs" key')
    remote_blobs = response['blobs']
    if set(remote_blobs) != set(test.stored_blobs):
        raise TestFailed(f'Blobs in remote and local are different')


def test_get_blob(test: TestInfo) -> None:
    '''GET to /api/v1/blob/<blobId> with valid AuthToken'''
    response = requests.get(test.endpoint(f'/api/v1/blob/{test.last_blob}'), headers=test.valid_headers)
    if response.status_code != 200:
        raise TestFailed(f'Expected status code 200, but got {response.status_code}')


def test_get_blob_anonymous(test: TestInfo) -> None:
    '''GET to /api/v1/blob/<blobId> with anonymous access'''
    blobId = test.public_blob
    if not blobId:
        test_upload_blob(test)
        blobId = test.last_blob
    response = requests.get(test.endpoint(f'/api/v1/blob/{blobId}'), headers={})
    if response.status_code != 200:
        raise TestFailed(f'Expected status code 200, but got {response.status_code}')


def test_switch_blob_private(test: TestInfo) -> None:
    '''PUT to /api/v1/blob/<blobId>/visibility'''
    method = random.choice([requests.put, requests.patch])
    data = json.dumps({PUBLIC_KEY: False}).encode('UTF-8')
    blobId = test.public_blob
    if not blobId:
        test_upload_blob(test)
        blobId = test.last_blob
    response = method(test.endpoint(f'/api/v1/blob/{blobId}/visibility'), headers=test.valid_headers, data=data)
    if response.status_code != 204:
        raise TestFailed(f'Expected status code 204, but got {response.status_code}')
    test.make_blob_private(blobId)


def test_switch_blob_public(test: TestInfo) -> None:
    '''PUT to /api/v1/blob/<blobId>/visibility'''
    method = random.choice([requests.put, requests.patch])
    data = json.dumps({PUBLIC_KEY: True}).encode('UTF-8')
    blobId = test.private_blob
    if not blobId:
        test_upload_blob(test)
        blobId = test.last_blob
    response = method(test.endpoint(f'/api/v1/blob/{blobId}/visibility'), headers=test.valid_headers, data=data)
    if response.status_code != 204:
        raise TestFailed(f'Expected status code 204, but got {response.status_code}')
    test.make_blob_public(blobId)


def test_get_blob_hash(test: TestInfo) -> None:
    '''GET to /api/v1/blob/<blobId> with valid AuthToken'''
    response = requests.get(test.endpoint(f'/api/v1/blob/{test.last_blob}/hash'), headers=test.valid_headers, params={'type': random.choice(['md5', 'sha256'])})
    if response.status_code != 200:
        raise TestFailed(f'Expected status code 200, but got {response.status_code}')

