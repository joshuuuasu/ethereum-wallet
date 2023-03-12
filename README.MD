# Ethereum Wallet Client

The ethereum wallet client provides the following functionality:

1. Create a new wallet address (public address and private key for signing transactions)
2. See user’s total eth balance
3. Send eth to another wallet address

## Installation

```bash
pip install -r requirements. txt 
```

## Usage
Note: Enter your password when prompt.

Create an account:

```shell
python3 main.py create-account
```

Check account balance:
```shell
python3 main.py check-balance
```

Send ethers:
```shell
python3 main.py send-ether ETHER_AMOUNT TO_ADDRESS
```

For help information:
```shell
python3 main.py --help
```