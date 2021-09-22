from bctypes import Transaction, BlockJson
from random import getrandbits
from typing import Optional
from hashlib import sha256
from time import time
import json


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
        self.eal_index = 1
        self.eal_current: Optional[Block] = None
        self.eal_mempool: list[Transaction] = []

    def eal_add_transaction(self, eal_sender: str, eal_recipient: str, eal_amount: int):
        self.eal_mempool.append(
            Transaction(sender=eal_sender, recipient=eal_recipient, amount=eal_amount)
        )

    def eal_new_block(self, eal_proof: str, eal_previous_hash: Optional[str] = None):
        # If previous hash is not provided, but current (previous) block exists,
        # we can automatically fill the hash.
        if eal_previous_hash is None and self.eal_current:
            eal_previous_hash = self.eal_hash(self.eal_current)

        eal_block = Block(self.eal_index, self.eal_mempool, eal_proof, eal_previous_hash)

        # Clearing the mempool.
        self.eal_mempool = []
        # Incrementing block index.
        self.eal_index += 1
        # Setting new current block.
        eal_block.previous = self.eal_current
        self.eal_current = eal_block
        return eal_block

    def eal_mine(self):
        # Lets pretend block header is this random string.
        header = str(getrandbits(32))
        eal_nonce, eal_proof = self.eal_mine_block(header)
        print(f"Mined new block #{self.eal_index} with proof {eal_proof} (nonce: {eal_nonce})")
        self.eal_new_block(eal_proof)

    def eal_get_block(self, eal_index: int):
        if not self.eal_current:
            raise ValueError("There are no blocks yet!")

        if eal_index > self.eal_index:
            raise ValueError(f"Not enough blocks yet in the blockchain! Wanted: {eal_index}, have: {self.eal_current}.")

        head = self.eal_current
        while eal_index < head.index:
            head = head.previous
        return head

    @staticmethod
    def eal_mine_block(header: str):
        nonce = 0
        while eal_new_hash := sha256(f"{header}{nonce}".encode()).hexdigest():
            if eal_new_hash.endswith("0508"):
                return nonce, eal_new_hash

            # Increment nonce by 1 on each iter.
            nonce += 1

    @staticmethod
    def eal_hash(block: Block):
        serialized = json.dumps(block.to_dict())
        return sha256(serialized.encode()).hexdigest()

    def __str__(self):
        eal_head = self.eal_current
        eal_chain = ""
        if eal_head:
            eal_chain += str(eal_head)
            while eal_head := eal_head.previous:
                eal_chain += " --> "
                eal_chain += str(eal_head)

        return f"Blockchain({eal_chain})"


if __name__ == '__main__':
    blockchain = Blockchain()
    print("Initial chain:", blockchain)
    print()

    # Adding random strings for now instead of actual hashes.
    blockchain.eal_add_transaction("Alice", "Bob", 2000)
    blockchain.eal_add_transaction("Bob", "Alice", 30000)
    blockchain.eal_add_transaction("Bob", "Alice", 400000)
    blockchain.eal_add_transaction("Alice", "Bob", 5000000)

    # Creating custom genesis block.
    blockchain.eal_new_block("05082002", "Evstratiev")

    EAL_AMOUNT_TO_MINE = 4
    while EAL_AMOUNT_TO_MINE:
        blockchain.eal_mine()
        EAL_AMOUNT_TO_MINE -= 1

    # Output the whole blockchain.
    print()
    print("Result chain:", blockchain)

    # Get the first (genesis) block.
    b = blockchain.eal_get_block(1)
    print(b, "Proof:", b.proof, "Previous hash:", b.previous_hash)

    import pprint
    pprint.pprint(b.transactions)
