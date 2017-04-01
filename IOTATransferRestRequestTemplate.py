from __future__ import absolute_import, division, print_function, \
    unicode_literals

import requests
from iota import *
from iota.adapter.sandbox import SandboxAdapter
import uuid
from pprint import pprint


# this method will register the request by generating a unique id for the request, this will serve as the tag for the
# sample transaction
def register_request():
    return uuid.uuid5()


# sample dummy api request, will return dictionary of request object and UUID of the requst

def create_request(url="https://api.github.com/users/sigmoidfreud/repos", headers={}):
    return {"request": requests.get(url, headers), "request-id": uuid.uuid5()}


# Create the API object.
iota = Iota(
    # To use sandbox mode, inject a ``SandboxAdapter``.
    adapter=SandboxAdapter(
        # URI of the sandbox node.
        uri='https://sandbox.iotatoken.com/api/v1/',

        # Access token used to authenticate requests.
        # Contact the node maintainer to get an access token.
        auth_token='auth token goes here',
    ),

    # Seed used for cryptographic functions.
    # If null, a random seed will be generated.
    seed=b'SEED9GOES9HERE',
)


# Example of sending a transfer using the sandbox.
# For more information, see :py:meth:`Iota.send_transfer`.
# noinspection SpellCheckingInspection
def create_transaction_dictionary(depth=100, request_tag=None,
                                  payment_address=b'TESTVALUE9DONTUSEINPRODUCTION99999FBFFTG'):
    sample_transaction = ProposedTransaction(
        # API payment address.
        address=
        Address(
            bytes(payment_address)
        ),

        # Amount of IOTA to transfer.
        # This value may be zero.
        value=17,

        # Optional tag to attach to the transfer.
        tag=Tag(bytes(request_tag)),

        # Optional message to include with the transfer.
        message=TryteString.from_string('I am making an API Request!'),
    )
    return {"depth": depth, "transaction-object": sample_transaction, "tag": request_tag}


def requestData():
    request_id = register_request()
    transaction = create_transaction_dictionary(request_tag=request_id)
    iota.send_transfer(
        depth=transaction['depth'],

        # One or more :py:class:`ProposedTransaction` objects to add to the
        # bundle.
        transfers=[transaction],
    )
    request_dict = create_request(headers={"auth_token": transaction.branch_transaction_hash})
    if transaction['tag'] == request_id:
        return request_dict['request'].json()


def main():
    requestData()


if __name__ == "__main__": main()
