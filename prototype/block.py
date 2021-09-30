from typing import Optional

from .typedefs import TransactionJson, BlockBodyJson, BlockJson
from .block_header import BlockHeader


class Block:
    __slots__ = ("transactions", "transactions_count", "header", "previous")

    def __init__(self, transactions: list[TransactionJson], header: BlockHeader):
        self.transactions = transactions
        self.transactions_count = len(self.transactions)
        self.header = header

        self.previous: Optional[Block] = None

    def to_json(self) -> BlockJson:
        return BlockJson(
            header=self.header.to_json(),
            body=BlockBodyJson(
                transactions_count=len(self.transactions),
                transactions=self.transactions,
            )
        )

    def __str__(self):
        return f"Block(hash={self.header.previous_hash[:10]})"
