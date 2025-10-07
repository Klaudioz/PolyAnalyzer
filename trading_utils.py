"""
Polymarket Trading Utilities Module

This module provides functions for interacting with Polymarket smart contracts
and placing trades. These are MANUAL functions that must be explicitly called.

⚠️  WARNING: These functions interact with real smart contracts on Polygon blockchain.
    Use only with funds you can afford to lose. Requires wallet with USDC balance.

Main Functions:
    - get_clob_client(): Create authenticated Polymarket API client
    - approveContracts(): One-time setup to approve USDC and CTF tokens (required before trading)
    - market_action(marketId, action, price, size): Place buy/sell orders
    - get_position(marketId): Check current position value in a market

Usage Example:
    from trading_utils import approveContracts, market_action
    
    # First time setup (run once per wallet)
    approveContracts()
    
    # Place a buy order
    market_action(
        marketId="0x123abc...",
        action="BUY",
        price=0.55,
        size=100
    )

Required:
    - PK environment variable (private key)
    - USDC balance in wallet
    - erc20ABI.json file
"""

from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, BalanceAllowanceParams, AssetType
from py_clob_client.order_builder.constants import BUY

from web3 import Web3
from web3.middleware import geth_poa_middleware

import json

from dotenv import load_dotenv
load_dotenv()

import time

import os

MAX_INT = 2**256 - 1

def get_clob_client():
    """
    Create and authenticate a Polymarket CLOB client for trading.
    
    Returns:
        ClobClient: Authenticated Polymarket API client, or None if authentication fails
        
    Environment Variables:
        PK: Polygon wallet private key (hex string)
    """
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    chain_id = POLYGON
    
    if key is None:
        print("Environment variable 'PK' cannot be found")
        return None


    try:
        client = ClobClient(host, key=key, chain_id=chain_id)
        api_creds = client.create_or_derive_api_creds()
        client.set_api_creds(api_creds)
        return client
    except Exception as ex: 
        print("Error creating clob client. Please check your PK environment variable and network connection.")
        return None


def approveContracts():
    """
    Approve USDC and CTF token contracts for trading on Polymarket.
    
    ⚠️  ONE-TIME SETUP: Run this function once per wallet before trading.
    ⚠️  REQUIRES: Wallet must have MATIC for gas fees (~$0.50 worth).
    
    This function approves three Polymarket contract addresses to spend your:
    - USDC tokens (for placing orders)
    - CTF tokens (Conditional Token Framework - for outcome tokens)
    
    Approved contracts:
        - 0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E (Exchange)
        - 0xC5d563A36AE78145C45a50134d48A1215220f80a (Neg Risk Adapter)
        - 0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296 (CTF Exchange)
    
    Runtime: ~30-60 seconds (6 transactions total)
    
    Returns:
        None (prints transaction hashes for verification)
        
    Raises:
        Web3 exceptions if transactions fail
    """
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    wallet = web3.eth.account.privateKeyToAccount(os.getenv("PK"))
    
    
    with open('erc20ABI.json', 'r') as file:
        erc20_abi = json.load(file)

    ctf_address = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
    erc1155_set_approval = """[{"inputs": [{ "internalType": "address", "name": "operator", "type": "address" },{ "internalType": "bool", "name": "approved", "type": "bool" }],"name": "setApprovalForAll","outputs": [],"stateMutability": "nonpayable","type": "function"}]"""

    usdc_contract = web3.eth.contract(address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", abi=erc20_abi)   # usdc.e
    ctf_contract = web3.eth.contract(address=ctf_address, abi=erc1155_set_approval)
    

    for address in ['0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E', '0xC5d563A36AE78145C45a50134d48A1215220f80a', '0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296']:
        usdc_nonce = web3.eth.getTransactionCount( wallet.address )
        raw_usdc_txn = usdc_contract.functions.approve(address, int(MAX_INT, 0)).build_transaction({
            "chainId": 137, 
            "from": wallet.address, 
            "nonce": usdc_nonce
        })
        signed_usdc_txn = web3.eth.account.sign_transaction(raw_usdc_txn, private_key=os.getenv("PK"))
        usdc_tx_receipt = web3.eth.wait_for_transaction_receipt(signed_usdc_txn, 600)

        tx_hash = usdc_tx_receipt.get('transactionHash', b'').hex() if hasattr(usdc_tx_receipt.get('transactionHash', b''), 'hex') else 'N/A'
        print(f'USDC Transaction for {address} completed. Hash: {tx_hash}')
        time.sleep(1)

        ctf_nonce = web3.eth.getTransactionCount( wallet.address )
        
        raw_ctf_approval_txn = ctf_contract.functions.setApprovalForAll(address, True).buildTransaction({
            "chainId": 137, 
            "from": wallet.address, 
            "nonce": ctf_nonce
        })

        signed_ctf_approval_tx = web3.eth.account.sign_transaction(raw_ctf_approval_txn, private_key=os.getenv("PK"))
        send_ctf_approval_tx = web3.eth.send_raw_transaction(signed_ctf_approval_tx.rawTransaction)
        ctf_approval_tx_receipt = web3.eth.wait_for_transaction_receipt(send_ctf_approval_tx, 600)

        tx_hash = ctf_approval_tx_receipt.get('transactionHash', b'').hex() if hasattr(ctf_approval_tx_receipt.get('transactionHash', b''), 'hex') else 'N/A'
        print(f'CTF Transaction for {address} completed. Hash: {tx_hash}')
        time.sleep(1)


    
    nonce = web3.eth.getTransactionCount( wallet.address )
    raw_txn_2 = usdc_contract.functions.approve("0xC5d563A36AE78145C45a50134d48A1215220f80a", int(MAX_INT, 0)).build_transaction({
        "chainId": 137, 
        "from": wallet.address, 
        "nonce": nonce
    })
    signed_txn_2 = web3.eth.account.sign_transaction(raw_txn_2, private_key=os.getenv("PK"))
    send_txn_2 = web3.eth.send_raw_transaction(signed_txn_2.rawTransaction)


    nonce = web3.eth.getTransactionCount( wallet.address )
    raw_txn_3 = usdc_contract.functions.approve("0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296", int(MAX_INT, 0)).build_transaction({
        "chainId": 137, 
        "from": wallet.address, 
        "nonce": nonce
    })
    signed_txn_3 = web3.eth.account.sign_transaction(raw_txn_3, private_key=os.getenv("PK"))
    send_txn_3 = web3.eth.send_raw_transaction(signed_txn_3.rawTransaction)
    
    
def market_action( marketId, action, price, size ):
    """
    Place a buy or sell order on a Polymarket market.
    
    ⚠️  REQUIRES: approveContracts() must be run first (one-time setup)
    ⚠️  REQUIRES: Wallet must have sufficient USDC balance
    
    Args:
        marketId (str): Token ID for the market outcome (e.g., "0x123abc...")
        action (str): Order side - "BUY" or "SELL"
        price (float): Limit price between 0.01 and 0.99 (e.g., 0.55 = 55% probability)
        size (float): Order size in USDC (e.g., 100 = $100 USD)
        
    Example:
        # Buy $100 worth at 55% probability
        market_action("0x123abc...", "BUY", 0.55, 100)
        
        # Sell $50 worth at 45% probability
        market_action("0x123abc...", "SELL", 0.45, 50)
    
    Returns:
        None (prints order ID if successful)
    """
    order_args = OrderArgs(
        price=price,
        size=size,
        side=action,
        token_id=marketId,
    )
    signed_order = get_clob_client().create_order(order_args)
    
    try:
        resp = get_clob_client().post_order(signed_order)
        print(f"Order posted successfully: {resp.get('orderID', 'N/A') if isinstance(resp, dict) else 'Success'}")
    except Exception as ex:
        print("Error posting order. Please check your balance and order parameters.")
        pass
    
    
def get_position(marketId):
    """
    Get the current USD value of your position in a specific market.
    
    Calculates position value by multiplying your share balance by the
    current best bid price from the order book.
    
    Args:
        marketId (str): Token ID for the market outcome
        
    Returns:
        float: Current position value in USD
        
    Example:
        value = get_position("0x123abc...")
        print(f"Position worth: ${value:.2f}")
    """
    client = get_clob_client()
    position_res = client.get_balance_allowance(
        BalanceAllowanceParams(
            asset_type=AssetType.CONDITIONAL,
            token_id=marketId
        )
    )
    orderBook = client.get_order_book(marketId)
    price = float(orderBook.bids[-1].price)
    shares = int(position_res['balance']) / 1e6
    return shares * price