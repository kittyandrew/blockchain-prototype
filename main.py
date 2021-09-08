from bctypes import Transaction, BlockJson
from random import getrandbits
from typing import Optional
from hashlib import sha256
from time import time


class Block:
    __slots__ = ("previous", "index", "hash", "timestamp", "transactions", "proof", "previous_hash")

    def __init__(self, index: int, transactions: list[Transaction], proof: str, previous_hash: Optional[str] = None):
        self.index = index
        self.timestamp = time()
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

        self.previous: Optional[Block] = None

    def to_dict(self) -> BlockJson:
        return BlockJson(
            index=self.index,
            timestamp=self.timestamp,
            transactions=self.transactions,
            proof=self.proof,
            previous_hash=self.previous_hash
        )

    def __str__(self):
        return f"Block(index={self.index})"


class Blockchain:
    def __init__(self):
        self.index = 1
        self.current: Optional[Block] = None
        self.mempool: list[Transaction] = []

    def add_transaction(self, sender: str, recipient: str, amount: float):
        self.mempool.append(
            Transaction(sender=sender, recipient=recipient, amount=amount)
        )

    def new_block(self, proof: str, previous_hash: Optional[str] = None):
        # If previous hash is not provided, but current (previous block exists,
        # we can automatically fill the hash.
        if previous_hash is None and self.current:
            previous_hash = self.hash(self.current)

        block = Block(self.index, self.mempool, proof, previous_hash)

        # Clearing the mempool.
        self.mempool = []
        # Incrementing block index.
        self.index += 1
        # Setting new current block.
        block.previous = self.current
        self.current = block
        return block

    def mine(self, initial_difficulty: int = 1, amount_to_mine: int = 1, infinitely: bool = False):
        while infinitely or amount_to_mine:
            proof = self.mine_block(initial_difficulty)
            print(f"Mined new block #{self.index} with proof {proof}")
            self.new_block(proof)
            # Let's increase difficulty
            initial_difficulty += 1
            amount_to_mine -= 1

    @staticmethod
    def mine_block(difficulty: int):
        while new_hash := sha256(str(getrandbits(32)).encode()).hexdigest():
            if new_hash.startswith("0" * difficulty):
                return new_hash

    @staticmethod
    def hash(block: Block):
        return

    def get_block(self, index: int):
        if not self.current:
            raise ValueError("There are no blocks yet!")

        if index > self.index:
            raise ValueError(f"Not enough blocks yet in the blockchain! Wanted: {index}, exists: {self.index}.")

        head = self.current
        while index < head.index:
            head = head.previous
        return head

    def __str__(self):
        head = self.current
        chain = ""
        if head:
            chain += str(head)
            while head := head.previous:
                chain += " --> "
                chain += str(head)

        return f"Blockchain({chain})"


if __name__ == '__main__':
    blockchain = Blockchain()
    print(blockchain)

    # Adding random strings for now instead of actual hashes.
    blockchain.add_transaction("Alice", "Bob", 2)
    blockchain.add_transaction("Bob", "Alice", 3)
    blockchain.add_transaction("Bob", "Alice", 4)
    blockchain.add_transaction("Alice", "Bob", 5)

    blockchain.mine(3, 4)
    print(blockchain)

    b = blockchain.get_block(1)
    print(b, b.transactions)
