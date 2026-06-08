import asyncio
from web3 import AsyncWeb3

# TO DO: fetch it from env
WS_URL = "wss://mainnet.infura.io/ws/v3/9aa3d95b3bc440fa88ea12eaa4456161"
async def listen_chain():
    infura_web_socket = AsyncWeb3(AsyncWeb3.WebSocketProvider(WS_URL))
    while True:
        block = await infura_web_socket.eth.get_block("latest")
        await asyncio.sleep(1)