from web3 import Web3
import json
import time

# Minimal Uniswap V2 Swap event listener
def create_minimal_listener():
    print("=== DeFi Risk Pipeline: Uniswap V2 Swap Listener ===")
    
    # Use public endpoint (will need Infura key for production)
    w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Ethereum")
        return
    
    print(f"✅ Connected to Ethereum (Chain ID: {w3.eth.chain_id})")
    
    # Uniswap V2 Swap event signature
    swap_topic = w3.keccak(text='Swap(address,uint256,uint256,uint256,uint256,address)').hex()
    print(f"Swap event topic: {swap_topic}")
    
    # Get latest block
    latest = w3.eth.block_number
    print(f"Latest block: {latest}")
    
    # Simple test: Get recent logs with Swap events
    print("\nFetching recent Swap events...")
    try:
        logs = w3.eth.get_logs({
            'fromBlock': latest - 100,  # Last 100 blocks
            'toBlock': latest,
            'topics': [swap_topic]
        })
        
        print(f"Found {len(logs)} Swap events in last 100 blocks")
        
        if logs:
            # Save first event as sample
            with open('sample_swap_event.json', 'w') as f:
                json.dump(dict(logs[0]), f, indent=2, default=str)
            print("✅ Saved sample event to 'sample_swap_event.json'")
            
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    create_minimal_listener()
