from __future__ import absolute_import, division, print_function, \
    unicode_literals

import uuid
from getpass import getpass as secure_input

import requests
from iota import Address, Bundle, Iota, ProposedTransaction, Tag, TryteString
from iota.adapter.sandbox import SandboxAdapter
from iota.crypto.types import Seed
from six import binary_type, moves as compat
from typing import Optional, Text


# this method will register the request by generating a unique id for the request, this will serve as the tag for the
# sample transaction
def register_request():
    # type: () -> uuid.UUID
    return uuid.uuid4()


def generate_api_key():
    r = requests.get("http://46.101.109.238/new_api_key")
    return r.content.decode("utf-8")


def generate_addresses(index=0, uri='ip address', auth_token=None):
    # type: (int, Text, Text) -> Address
    seed = get_seed()

    # Create the API instance.
    # Note: If ``seed`` is null, a random seed will be generated.
    if auth_token is None:
        api = create_iota_object(uri=uri, auth_token=auth_token, seed=seed)
    else:
        api = create_iota_object(uri=uri, auth_token=auth_token, seed=seed)

    # If we generated a random seed, then we need to display it to the
    # user, or else they won't be able to use their new addresses!
    if not seed:
        print('A new random seed has been initiated. Press enter to generate it.')
        output_seed(api.seed)

    print('Generating addresses.  Please wait until the address is generated...')
    print('')

    # generate address based on count arg
    gna_result = api.get_new_addresses(index, 1)
    print('address is now generated')
    return gna_result['addresses'][0]


def get_seed():
    # type: () -> binary_type
    """
    Prompts the user securely for their seed.
    """
    print(
        'Enter seed and press return (typing will not be shown).  '
        'If empty, a random seed will be generated and displayed on the screen.'
    )
    seed = secure_input('')  # type: Text
    return seed.encode('ascii')


def output_seed(seed):
    # type: (Seed) -> None
    """
    Outputs the user's seed to stdout, show security warnings from boiler plate code (Obligatory PSA)
    """
    print(
        'WARNING: Anyone who has your seed can spend your IOTAs! '
        'Clear the screen after recording your seed!'
    )
    compat.input('')
    print('Your seed is:')
    print('')
    print(binary_type(seed).decode('ascii'))
    print('')

    print(
        'make sure to clear the screen contents',
        'and press enter to continue.'
    )
    compat.input('')


# sample dummy api request, will return dictionary of request object and UUID of the requst

def create_request(url="http://46.101.109.238/forecast/", city='Chicago', headers=None):
    # type: (Text, Optional[dict]) -> dict
    return {"request": requests.get(url + city, headers=headers), "request-id": register_request()}


# Create the API object.
def create_iota_object(uri, auth_token, seed=None):
    # type: (Text, Text, Optional[Seed]) -> Iota
    return Iota(
        # To use sandbox mode, inject a ``SandboxAdapter``.
        adapter=SandboxAdapter(
            # URI of the sandbox node.
            uri=uri,

            # Access token used to authenticate requests.
            # Contact the node maintainer to get an access token.
            auth_token=auth_token,
        ),

        # Seed used for cryptographic functions.
        # If null, a random seed will be generated.
        seed=seed,
    )


# For more information, see :py:meth:`Iota.send_transfer`.
def create_transaction_dictionary(address, price, depth=3, request_tag=None):
    # type: (int, Optional[binary_type]) -> dict

    # encode the string so it doesnt cause conflict during encode/decode process

    r_tag = Tag(request_tag.encode('utf-8'))
    sample_transaction = ProposedTransaction(
        # on the fly API payment address.
        address=Address(str.encode(address)),
        # Amount of IOTA to transfer.
        # This value may be zero.
        value=int(price),

        # Optional tag to attach to the transfer.
        tag=r_tag,

        # Optional message to include with the transfer.
        message=TryteString.from_string('I am making an API Request!'),
    )
    return {"depth": depth, "transaction-object": sample_transaction, "tag": r_tag}


def payment_boolean(price=0):
    accept_payment = input("The server asks for a payment of " + price + " IOTAs. proceed? Y/(Any other key)\n")
    if accept_payment == 'Y':
        return True
    else:
        return False


def requestData(api_key=None, headers={}):
    if api_key is None:
        key = generate_api_key()
    # type: () -> Optional[Text]
    request_id = TryteString.from_string(str(register_request()))[0:27]

    # :todo: Populate these values and/or make API object globally-accessible.
    headers['Authorization'] = key
    request_dict = create_request(headers)
    response_headers = request_dict['request'].headers
    price = response_headers['price']
    paid = payment_boolean(price)
    if paid:
        print("Thank you for your payment the data will now be served...")
        transaction = create_transaction_dictionary(address=response_headers['address'],
                                                    price=response_headers['price'],
                                                    request_tag=response_headers['tag'])
        api = create_iota_object(uri='http://85.93.93.110:14265/', auth_token=None)
        st_response = api.send_transfer(
            depth=transaction['depth'],

            # One or more :py:class:`ProposedTransaction` objects to add to the
            # bundle.
            transfers=[transaction['transaction-object']],
        )

        # Extract the tail transaction hash from the newly-created
        # bundle.
        bundle = st_response['bundle']  # type: Bundle
        headers['transaction'] = str(bundle.tail_transaction.hash)[18:-2]
        request_dict = create_request(headers)
        return request_dict['request'].json()
    else:
        print("You have not agreed to pay for the request data, so a an empty object will be returned")

    return None


class payPerApi:
    def __init__(self, IOTA, seed, apiKey):
        self.IOTA = IOTA
        self.seed = seed
        self.apiKey = apiKey

    headers = {"Authorization": apiKey}

    def requestData(self, method='get'):
        if self.apiKey is None:
            key = generate_api_key()
        else:
            key = self.apiKey
        # type: () -> Optional[Text]
        request_id = TryteString.from_string(str(register_request()))[0:27]

        # :todo: Populate these values and/or make API object globally-accessible.
        request_dict = create_request(headers={"Authorization": key})
        response_headers = request_dict['request'].headers
        price = response_headers['price']
        accept_payment = input("The server asks for a payment of " + price + " IOTAs. proceed? Y/N\n")
        if accept_payment == 'Y':
            print("Thank you for your payment the data will now be served...")
            transaction = create_transaction_dictionary(address=response_headers['address'],
                                                        price=response_headers['price'],
                                                        request_tag=response_headers['tag'])
            st_response = self.IOTA.send_transfer(
                depth=transaction['depth'],

                # One or more :py:class:`ProposedTransaction` objects to add to the
                # bundle.
                transfers=[transaction['transaction-object']],
            )

            # Extract the tail transaction hash from the newly-created
            # bundle.
            bundle = st_response['bundle']  # type: Bundle
            request_dict = create_request(headers={'transaction': str(bundle.tail_transaction.hash)[18:-2],
                                                   "Authorization": key})
            return request_dict['request']
        else:
            print("You have not agreed to pay for the request data, so a an empty object will be returned")

        return None


def main():
    # if no api key is entered as arg then a new one will be generated, if you have an existing key, use it
    api = create_iota_object(uri='http://85.93.93.110:14265/', auth_token=None)
    client = payPerApi(api, None, None)
    req = client.requestData()
    # the above request return JSON
    print(req)


if __name__ == "__main__": main()
