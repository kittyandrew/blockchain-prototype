from typing import Optional

from .typedefs import BlockHeaderJson


class BlockHeader:
    __slots__ = ("version", "index", "previous_hash", "merkle_root", "timestamp", "difficulty", "nonce", "proof")

    def __init__(self, version: str, index: int, previous_hash: str, merkle_root: str, timestamp: float, difficulty: str, nonce: int, proof: Optional[str] = None):
        self.version = version
        self.index = index
        self.previous_hash = previous_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce

        self.proof = proof

    def to_json(self):
        return BlockHeaderJson(
            version=self.version,
            index=self.index,
            previous_hash=self.previous_hash,
            merkle_root=self.merkle_root,
            timestamp=self.timestamp,
            difficulty=self.difficulty,
            nonce=self.nonce,
            proof=self.proof,
        )

    @classmethod
    def from_json(cls, data: BlockHeaderJson) -> "BlockHeader":
        return cls(
            data["version"], data["index"], data["previous_hash"], data["merkle_root"],
            data["timestamp"], data["difficulty"], data["nonce"], data["proof"]
        )
