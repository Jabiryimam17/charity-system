from abc import ABC, abstractmethod

import logging
logger = logging.getLogger(__name__)

class BaseEventHandler(ABC):
    """Every handler must implement handle()."""

    event_name: str = None

    def process(self, event):
        """Called by router. Validates then handles"""
        logger.info(f"[{self.event_name}] tx={event['transactionHash'].hex()}")
        try:
            self.handle(event)
        except Exception as e:
            logger.error(f"Error handling event {self.event_name}: {e}")
            raise


    @abstractmethod
    def handle(self, event):
        """Override this in each handler"""
        pass