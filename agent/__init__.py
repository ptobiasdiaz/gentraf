#!/usr/bin/env python3

'''
    GenTraf agent implementation
'''

MULTIPART_FILE_KEY = 'file'
BLOBID_KEY = 'blobId'
PUBLIC_KEY = 'public'

AUTH_TOKEN_HEADER = 'AuthToken'

VALID_USER = 'USER'
VALID_TOKEN = 'USER_TOKEN'
WRONG_USER = ':():'
WRONG_TOKEN = ':():'

SIZE1K = 1024
SIZE1M = 1024 * SIZE1K
SIZE10M = 10 * SIZE1M
BLOB_SIZES = [SIZE1K, SIZE1M, SIZE10M]
