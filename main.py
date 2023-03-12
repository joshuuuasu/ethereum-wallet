import os
import json
import click

from web3 import Web3
from eth_account import Account
from secrets import token_hex

ETHEREUM_WALLET_DIR = os.path.expanduser("~") + "/.ethereum-wallet"
ETHEREUM_WALLET_CONFIG_PATH = ETHEREUM_WALLET_DIR + "/config.json"
ETHEREUM_WALLET_KEYFILE_PATH = ETHEREUM_WALLET_DIR + "/keyfile.json"

alchemy_url = "https://eth-goerli.g.alchemy.com/v2/hGXnyh_slr2vUwU7_yKQirUN2PyJCQk7"
w3 = Web3(Web3.HTTPProvider(alchemy_url))


@click.group()
def cli():
    pass


@click.command()
@click.password_option(prompt="Please set a password for your account")
def create_account(password: str) -> str:
    """
    Create a new account.

    :param password: str, password for the account to be created
    :return: the public address of the created account
    """
    token = token_hex(nbytes=32)
    private_key = '0x' + token
    account = Account.from_key(private_key=private_key)
    encrypted = Account.encrypt(private_key=private_key, password=password)
    address = account.address

    if not os.path.isdir(ETHEREUM_WALLET_DIR):
        os.mkdir(ETHEREUM_WALLET_DIR)
    with open(file=ETHEREUM_WALLET_CONFIG_PATH, mode='w+') as f:
        f.write(json.dumps({"address": address}))
    with open(file=ETHEREUM_WALLET_KEYFILE_PATH, mode='w+') as f:
        f.write(json.dumps(encrypted))

    print(f"Your new account has been created! Its address is: '{address}'.")
    return address


@click.command()
@click.password_option(confirmation_prompt=False)
def check_balance(password: str) -> float:
    """
    Check the balance of the created account. The account must be created before the function gets called.

    :param password: the password for the account.
    :return: the balance of the account in unit of ether.
    """
    address, _ = _get_credentials(password=password)
    balance = w3.eth.get_balance(address)
    ether = w3.fromWei(balance, 'ether')
    print(f"Your account balance is: {ether} ETH.")
    return ether


@click.command()
@click.password_option(confirmation_prompt=False)
@click.argument('ether')
@click.argument('to')
def send_ether(password: str, ether: float, to: str):
    """
    Send ethers to another account. The accounts must be created before the function gets called.

    :param password: password for the account.
    :param ether: amount of ethers to be sent.
    :param to: the address of the receiving account.
    """
    address, private_key = _get_credentials(password=password)
    nonce = w3.eth.get_transaction_count(address)
    tx = {
        'nonce': nonce,
        'from': address,
        'to': w3.toChecksumAddress(to),
        'value': w3.toWei(ether, 'ether'),
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    }

    signed_tx = Account.sign_transaction(tx, private_key)
    w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("Transaction succeeded.")


def _get_credentials(password: str):
    try:
        with open(file=ETHEREUM_WALLET_CONFIG_PATH, mode='r') as f:
            config = json.load(f)
            address = config.get("address")
        with open(file=ETHEREUM_WALLET_KEYFILE_PATH, mode='r') as f:
            encrypted = json.load(f)
            private_key = Account.decrypt(keyfile_json=encrypted, password=password)
        return address, private_key
    except FileNotFoundError:
        raise AssertionError(
            "You have not created an account yet! "
            "See command 'create-account' for more information."
        )
    except ValueError:
        raise ValueError("Incorrect password!")


cli.add_command(create_account)
cli.add_command(check_balance)
cli.add_command(send_ether)


if __name__ == '__main__':
    cli()

