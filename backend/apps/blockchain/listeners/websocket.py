import asyncio
import logging
from web3 import AsyncWeb3

from web3.providers import WebSocketProvider
from django.conf import settings
from apps.blockchain.routers import route_event

logger = logging.getLogger(__name__)


# from apps.blockchain.router import route_event

def load_contract(ws, address, file_path):
    import json
    from pathlib import Path
    blockchain_path = "blockchain/out/" + file_path
    with open(Path(__file__).parent.parent.parent.parent / blockchain_path, 'r') as f:
        abi = json.load(f)
    return ws.eth.contract(address=address, abi=abi)


async def build_subscriptions(ws):
    registrar_contract = load_contract(ws, settings.USER_REGISTRAR_CONTRACT_ADDRESS,
                                       "User-Registral.sol/UserRegistrar.json")
    return [
        registrar_contract.events.ScoreUpdated.create_subscription(
            label='score-update',
            handler=lambda event: route_event(event)
        )
    ]


async def listen_websocket():
    async with AsyncWeb3(WebSocketProvider(settings.WEB3_WEBSOCKET_URL)) as ws:
        subscriptions = await build_subscriptions(ws)

        logger.info(f"Subscribing to {len(subscriptions)} events")
        await ws.subscription_manager.subscribe(subscriptions)
        logger.info("Listening...")
        await ws.subscription_manager.handle_subscriptions()


def run_websocket_listener():
    asyncio.run(listen_websocket())
