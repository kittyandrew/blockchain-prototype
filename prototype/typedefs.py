from typing import TypedDict


class TransactionJson(TypedDict):
    sender: str
    recipient: str
    amount: int


class BlockHeaderJson(TypedDict):
    version: str
    index: int
    previous_hash: str
    merkle_root: str
    timestamp: float
    difficulty: str
    nonce: int
    proof: str


class BlockBodyJson(TypedDict):
    transactions_count: int
    transactions: list[TransactionJson]


class BlockJson(TypedDict):
    header: BlockHeaderJson
    body: BlockBodyJson
