"""
credits:

    * https://gist.github.com/shirriff/c9fb5d98e6da79d9a772#file-merkle-py
    * https://github.com/richardkiss/pycoin

"""
import binascii
import hashlib
import json

import requests


BLOCKEXPLORER_API_URL = 'https://blockexplorer.com/api'

BLOCKHASH = '0000000000000000e067a478024addfecdc93628978aa52d91fabd4292982a50q'


def get_block(blockhash=BLOCKHASH, with_response=False):
    url = '{}/block/{}'.format(BLOCKEXPLORER_API_URL, blockhash)
    response = requests.get(url)
    try:
        block = json.loads(response.content)
    # TODO specify which exception to catch
    except:
        block = None
    if with_response:
        return block, response
    return block


def merkleroot(hashes):
    """
    Args:
        hashes: reversed binary form of transactions hashes, e.g.:
            ``binascii.unhexlify(h)[::-1] for h in block['tx']]``
    Returns:
        merkle root in hexadecimal form
    """
    if len(hashes) == 1:
        return binascii.hexlify(bytearray(reversed(hashes[0])))
    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])
    parent_hashes = []
    for i in range(0, len(hashes)-1, 2):
        first_round_hash = hashlib.sha256(hashes[i] + hashes[i+1]).digest()
        second_round_hash = hashlib.sha256(first_round_hash).digest()
        parent_hashes.append(second_round_hash)
    return merkleroot(parent_hashes)
