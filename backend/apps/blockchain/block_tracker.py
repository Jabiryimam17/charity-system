import logging
from django.db import transaction
from django.conf import settings

logger = logging.getLogger(__name__)


class BlockTracker:

    def __init__(self, socket, start_block=None):

        """
        :param socket: tcp connection to recieve data from infura api
        :param start_block: last block number to start tracking from, if None, starts from the latest block
        """

        self.socket = socket
        self.last_block = self._load(start_block)

    def _load(self, start_block):

        """Load last block from database. creates a new record if none exists"""

        from apps.blockchain.models import ListenerState

        state, created = ListenerState().objects.get_or_create(name="block_tracker",
                                                               defaults={"last_block": start_block})
        if created:
            logger.info("Created new block tracker state")
        else:
            logger.info("Loaded block tracker state")
        return state.last_block

    def update(self, block_number):

        """Update last block in database"""

        from apps.blockchain.models import ListenerState

        with transaction.atomic():
            state = ListenerState.objects.select_for_update().get(name="block_tracker")
            state.last_block = block_number
            state.save()
        self.last_block = block_number
        logger.info(f"Updated block tracker state to {block_number}")

    def range(self):

        """Return a range of blocks to track"""
        if settings.BLOCK_TRACKER_RANGE < 1: raise ValueError("BLOCK_TRACKER_RANGE must be greater than 0")
        return range(self.last_block, min(self.last_block + settings.BLOCK_TRACKER_RANGE, self.socket.eth.block_number))

    def reset(self, block=None):
        """Manually reset the block tracker to a specific block number"""
        if block is None:
            block = self.socket.eth.block_number
        self.update(block)
        logger.info(f"Reset block tracker to block {block}")
