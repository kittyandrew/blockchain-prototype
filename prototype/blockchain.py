from typing import Optional
from hashlib import sha256
from time import time
import asyncio
import aiohttp
import logging
import json

from .typedefs import TransactionJson
from .block_header import BlockHeader
from .block import Block
from . import __version__


class Blockchain:
    ONE_COIN = 100_000_000

    def __init__(self, owner_addr: str, eal_difficulty: str = ""):
        self.owner_addr = owner_addr
        self.eal_difficulty = eal_difficulty

        self.eal_index: int = 1
        self.eal_current: Optional[Block] = None
        self.eal_mempool: list[TransactionJson] = []

        self.eal_bg_mining_task = None

        self.peers: list[str] = []
        self.host: Optional[str] = None

    def eal_add_transaction(self, eal_sender: str, eal_recipient: str, eal_amount: int, eal_index: int = None):
        """
        Method for adding new transactions to the mempool.

        :param eal_sender:  Sender of the transaction.
        :param eal_recipient:  Recipient of the transaction.
        :param eal_amount:  Amount that is being transacted.
        :param eal_index:  Used to insert transactions into specific index in the mempool (i.e. add own mining reward -- coinbase -- as highest priority transaction).
        :return:
        """
        new_transaction = TransactionJson(sender=eal_sender, recipient=eal_recipient, amount=eal_amount)

        if eal_index is None:  self.eal_mempool.append(new_transaction)
        else:                  self.eal_mempool.insert(eal_index, new_transaction)

    def eal_new_header(self, eal_previous_hash: str = None):
        # Note(andrew): If previous hash is not provided, but current (previous) block exists,
        #     we can automatically fill the hash.
        if eal_previous_hash is None and self.eal_current:
            eal_previous_hash = self.eal_hash_header(self.eal_current.header, self.eal_current.header.nonce)

        assert eal_previous_hash is not None, "You have to provide previous hash!"
        return BlockHeader(
            version=__version__,
            index=self.eal_index,
            previous_hash=eal_previous_hash,
            merkle_root=self.eal_make_merkle_root([self.eal_hash(json.dumps(t)) for t in self.eal_mempool]),
            timestamp=time(),
            difficulty=self.eal_difficulty,
            nonce=0,
        )

    def eal_new_block(self, eal_header: Optional[BlockHeader]):
        # Creating instance of the new block and filling headers.
        eal_block = Block(self.eal_mempool, eal_header)

        # Clearing the mempool.
        self.eal_mempool.clear()
        # Incrementing block index.
        self.eal_index += 1
        # Setting new current block.
        eal_block.previous, self.eal_current = self.eal_current, eal_block
        return eal_block

    def eal_add_block(self, eal_block: Block):
        # Clearing the mempool.
        for transaction in eal_block.transactions:
            if transaction in self.eal_mempool:
                self.eal_mempool.remove(transaction)

        # Incrementing block index.
        self.eal_index += 1
        # Setting new current block.
        eal_block.previous, self.eal_current = self.eal_current, eal_block
        return eal_block

    def eal_get_block(self, eal_index: int):
        if not self.eal_current:        raise ValueError("There are no blocks yet!")

        if eal_index > self.eal_index:  raise ValueError(f"Not enough blocks yet in the blockchain! Wanted: {eal_index}, have: {self.eal_current}.")

        if eal_index <= 0:              raise ValueError(f"Index must be an unsigned integer (excluding 0)!")

        head = self.eal_current
        while eal_index != head.header.index:  head = head.previous
        return head

    def eal_hash_header(self, header: BlockHeader, nonce: int):
        to_hash = f"{header.version}{header.index}{header.previous_hash}" \
                f"{header.merkle_root}{header.timestamp}{header.difficulty}{nonce}"
        return self.eal_hash(to_hash)

    async def eal_mine_block(self, header: BlockHeader):
        nonce = 0
        while eal_new_hash := self.eal_hash_header(header, nonce):
            if eal_new_hash.endswith(self.eal_difficulty):
                return nonce, eal_new_hash

            # Increment nonce by 1 on each iter.
            nonce += 1
            # Async yield to be able to process other things in parallel
            await asyncio.sleep(0)

    async def eal_mine(self):
        # Lets add coinbase transaction right now, before mining the block so we will have a valid merkle tree hash.
        self.eal_add_transaction("Coinbase", self.owner_addr, self.eal_float_to_coin(5.), 0)

        # Craft block header to start mining.
        eal_header = self.eal_new_header()
        # Fill the important data after we mined the block.
        eal_header.nonce, eal_header.proof = await self.eal_mine_block(eal_header)
        logging.info("Mined new block #%s with proof %s (nonce: %s)", self.eal_index, eal_header.proof, eal_header.nonce)

        return self.eal_new_block(eal_header)

    async def background_mining(self):
        while True:
            try:
                logging.info("Starting to mine a new block #%s ...", self.eal_index)

                block = await self.eal_mine()
                logging.info("Mined a new block: %s.", block)

                if self.peers:
                    logging.info("Propagating new block to peers (%s) ...", self.peers)
                    await self.propagate_to_peers(block, self.peers)
            except asyncio.CancelledError:
                logging.info("Stopped mining task...")
                break

    async def propagate_to_peers(self, block: Block, peers: list[str]):
        async with aiohttp.ClientSession() as session:
            for peer in peers:
                try:
                    payload = {"peer": self.host, "block": block.to_json()}
                    r = await session.post(f"http://{peer}/gossip/new_block", json=payload)
                    assert r.status == 200

                    data = await r.json()
                    if data.get("status") != 200:
                        logging.warning("Peer %s returned an error: %s ...", peer, data)
                        await self.sync_chains(peer)
                except Exception:
                    logging.info("Failed to talk to peer %s to propagate a block ...", peer)

    async def sync_chains(self, peer):
        async with aiohttp.ClientSession() as session:
            try:
                r = await session.get(f"http://{peer}/gossip/chain/length")
                assert r.status == 200
                data = await r.json()
                if data.get("status") != 200:
                    logging.warning("Peer %s returned an error: %s ...", peer, data)
                    return

                if data["length"] < self.eal_index:
                    return

                r = await session.get(f"http://{peer}/gossip/chain/full")
                assert r.status == 200
                data = await r.json()
                if data.get("status") != 200:
                    logging.warning("Peer %s returned an error: %s ...", peer, data)
                    return

                # TODO: Verify that the genesis block is the same.
                genesis = Block.from_json(data["chain"][0])

                new_current = genesis
                for block_data in data["chain"][1:]:
                    block = Block.from_json(block_data)

                    # TODO: Verify block validity properly.
                    if not block.header.proof or not block.header.proof.endswith(self.eal_difficulty):
                        return

                    block.previous = new_current
                    new_current = block

                self.eal_current = new_current
                self.eal_index = new_current.header.index + 1
            except Exception:
                logging.info("Failed to talk to peer %s to sync chains ...", peer)

    @classmethod
    def eal_float_to_coin(cls, value: float) -> int:
        """
        Turn float input (% of a coin) into smaller units for internal representation (whole number).

        :param value:  Float number representing amount of coins.
        :return:
        """
        # Note(andrew): This rounds number down, so beware you must get rounding error (i.e. you will
        #     get zero, when you try to convert to smaller number than 1 unit).
        return int(value * cls.ONE_COIN)

    @classmethod
    def eal_make_merkle_root(cls, items: list) -> str:
        if not items:
            return ""

        while (length := len(items)) > 1:
            # print(f"Getting merkle root of:", items)

            new_result = list()
            for i in range(0, length, 2):
                # Check if we have one last element, and can't do combined hash of two items.
                if i == length - 1:  item = items[i] + items[i]
                else:                item = items[i] + items[i + 1]

                new_result.append(cls.eal_hash(item))
            items = new_result
        return items[0]

    @staticmethod
    def eal_hash(serialized: str):
        return sha256(sha256(serialized.encode()).digest()).hexdigest()

    @property
    def full_chain(self):
        chain = []
        head = self.eal_current
        if head:
            chain.append(head)
            while head.previous:
                head = head.previous
                chain.append(head)

        return list(reversed(chain))

    def __str__(self):
        eal_head = self.eal_current
        eal_chain = ""
        if eal_head:
            eal_chain += str(eal_head)
            while eal_head := eal_head.previous:
                eal_chain += " --> "
                eal_chain += str(eal_head)

        return f"Blockchain({eal_chain})"
