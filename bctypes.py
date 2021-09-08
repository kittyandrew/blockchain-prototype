from typing import TypedDict


class Transaction(TypedDict):
    sender: str
    recipient: str
    amount: float


class BlockJson(TypedDict):
    index: int
    timestamp: float
    transactions: list[Transaction]
    proof: str
    previous_hash: str
