import asyncio
import logging
from web3 import AsyncWeb3

from web3.providers import WebSocketProvider
from django.conf import settings
from apps.blockchain.routers import route_event

logger = logging.getLogger(__name__)



def load_contract(ws, address, file_path):
    import json
    from pathlib import Path
    blockchain_path = "blockchain/out/" + file_path
    with open(Path(__file__).parent.parent.parent.parent / blockchain_path, 'r') as f:
        abi = json.load(f)
    return ws.eth.contract(address=address, abi=abi)


async def build_subscriptions(ws):
    import json
    from pathlib import Path
    blockchain_path = "blockchain/out/User-Registral.sol/UserRegistrar.json"
    with open(Path(__file__).parent.parent.parent.parent / blockchain_path, 'r') as f:
        artifact = json.load(f)
    abi = artifact['abi']
    registrar_contract = ws.eth.contract(address=settings.USER_REGISTRAR_CONTRACT_ADDRESS, abi=abi)
    
    return [
        await registrar_contract.events.ScoreUpdate.subscribe(
            on_event=lambda event: route_event(event)
        )
    ]


async def listen_websocket():
    from web3 import AsyncWeb3, WebSocketProvider
    async with AsyncWeb3(WebSocketProvider(settings.WEB3_WEBSOCKET_URL)) as ws:
        subscriptions = await build_subscriptions(ws)

        logger.info(f"Subscribing to {len(subscriptions)} events")
        
        while True:
            # This is a simplified version, real web3.py subscription handling 
            # might differ depending on version and transport.
            # Usually we iterate over subscriptions or use a callback.
            await asyncio.sleep(1)


def run_websocket_listener():
    asyncio.run(listen_websocket())
