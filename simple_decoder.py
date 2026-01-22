from web3 import Web3
import json

def simple_decoder():
    print("=== Simple Uniswap V2 Swap Decoder ===")
    
    w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    
    if not w3.is_connected():
        print("❌ Not connected to Ethereum")
        return
    
    print(f"✅ Connected (Chain ID: {w3.eth.chain_id})")
    
    # Get latest block
    latest = w3.eth.block_number
    print(f"Latest block: {latest}")
    
    # Get a few recent blocks
    from_block = latest - 10
    
    # Uniswap V2 Swap event signature
    swap_topic = w3.keccak(text='Swap(address,uint256,uint256,uint256,uint256,address)').hex()
    
    print(f"Looking for Swap events from block {from_block} to {latest}...")
    
    logs = w3.eth.get_logs({
        'fromBlock': from_block,
        'toBlock': latest,
        'topics': [swap_topic]
    })
    
    print(f"Found {len(logs)} Swap events")
    
    if logs:
        # Take first event
        raw_event = logs[0]
        print(f"\nRaw event address: {raw_event['address']}")
        
        # Try to decode
        decode_single_event(raw_event, w3)

def decode_single_event(event, w3):
    # Uniswap V2 Pair ABI for Swap event (minimal)
    swap_abi = {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "sender", "type": "address"},
            {"indexed": False, "name": "amount0In", "type": "uint256"},
            {"indexed": False, "name": "amount1In", "type": "uint256"},
            {"indexed": False, "name": "amount0Out", "type": "uint256"},
            {"indexed": False, "name": "amount1Out", "type": "uint256"},
            {"indexed": True, "name": "to", "type": "address"}
        ],
        "name": "Swap",
        "type": "event"
    }
    
    # Create minimal contract
    contract = w3.eth.contract(address=event['address'], abi=[swap_abi])
    
    try:
        decoded = contract.events.Swap().process_log(event)
        print("\n✅ DECODED SWAP EVENT:")
        print(f"  Pair Address: {event['address']}")
        print(f"  Sender: {decoded['args']['sender']}")
        print(f"  To: {decoded['args']['to']}")
        print(f"  amount0In: {decoded['args']['amount0In']}")
        print(f"  amount1In: {decoded['args']['amount1In']}")
        print(f"  amount0Out: {decoded['args']['amount0Out']}")
        print(f"  amount1Out: {decoded['args']['amount1Out']}")
        
        # Save the decoded result
        result = {
            'pair_address': event['address'],
            'block_number': event['blockNumber'],
            'tx_hash': event['transactionHash'].hex(),
            'sender': decoded['args']['sender'],
            'to': decoded['args']['to'],
            'amount0In': str(decoded['args']['amount0In']),
            'amount1In': str(decoded['args']['amount1In']),
            'amount0Out': str(decoded['args']['amount0Out']),
            'amount1Out': str(decoded['args']['amount1Out'])
        }
        
        with open('decoded_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n✅ Saved to 'decoded_result.json'")
        
    except Exception as e:
        print(f"❌ Decoding failed: {e}")
        # Show raw data for debugging
        print(f"Raw data: {event['data'].hex()}")
        print(f"Topics: {[t.hex() for t in event['topics']]}")

if __name__ == "__main__":
    simple_decoder()
