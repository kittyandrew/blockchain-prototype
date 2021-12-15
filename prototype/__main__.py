from sanic.response import json
from sanic import Sanic
import argparse
import asyncio
import logging

from . import Blockchain, BlockJson, Block


# blockchain = Blockchain("Andrew", "050802")
blockchain = Blockchain("Andrew", "05080")
app = Sanic("Blockchain Server")


@app.route("/api/health", methods=["GET"])
async def health_status(_request):
    return json({"status": 200, "health": "ok"})


async def start_bg(_app, _loop):
    blockchain.eal_bg_mining_task = asyncio.create_task(blockchain.background_mining())


async def stop_bg(_app, _loop):
    if blockchain.eal_bg_mining_task:
        blockchain.eal_bg_mining_task.cancel()


@app.route("/gossip/new_block", methods=["POST"])
async def receive_new_block(request):
    data = request.json
    peer: str = data["peer"]
    block_data: BlockJson = data["block"]
    logging.debug("Received block data via gossip: %s ...", block_data)

    try:
        block = Block.from_json(block_data)
        logging.info("Received a block via gossip: %s ...", block)
    except Exception:
        logging.info("Failed to convert data to a valid block ...")
        return json({"status": 400})

    # Adding new peer to the peer list, if not already known.
    if peer != blockchain.host and peer not in blockchain.peers:
        blockchain.peers.append(peer)

    if block.header.previous_hash != blockchain.eal_hash_header(blockchain.eal_current.header, blockchain.eal_current.header.nonce):
        return json({"status": 400, "message": "Block is ignored!", "reason": "The block does not correspond to a current chain!"})

    if not block.header.proof or not block.header.proof.endswith(blockchain.eal_difficulty):
        return json({"status": 400, "message": "Block is invalid!", "reason": "Proof of work is invalid!"})

    verified_proof = blockchain.eal_hash_header(block.header, block.header.nonce)
    if block.header.proof != verified_proof:
        return json({"status": 400, "message": "Block is invalid!", "reason": "Proof of work doesn't match!"})

    logging.info("Successfully validated a gossip block!")
    # Stop mining while we are syncing..
    if blockchain.eal_bg_mining_task:
        blockchain.eal_bg_mining_task.cancel()

    # Adding a new block to the blockchain.
    blockchain.eal_add_block(block)

    # Resume mining..
    blockchain.eal_bg_mining_task = asyncio.create_task(blockchain.background_mining())
    # logging.info("Tasks: %s", asyncio.Task.all_tasks())
    asyncio.create_task(blockchain.propagate_to_peers(block, [p for p in blockchain.peers if peer != p]))
    return json({"status": 200})


@app.route("/gossip/chain/length", methods=["GET"])
async def get_current_chain_length(_request):
    return json({"status": 200, "length": blockchain.eal_index})


@app.route("/gossip/chain/full", methods=["GET"])
async def get_full_current_chain(_request):
    return json({"status": 200, "chain": [b.to_json() for b in blockchain.full_chain]})


if __name__ == "__main__":
    formatter = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
    date_format = "%d-%b-%y %H:%M:%S"
    logging.basicConfig(format=formatter, datefmt=date_format, level=logging.INFO)

    parser = argparse.ArgumentParser(description="Blockchain prototype #TODO")
    parser.add_argument("-p", "--port", type=int, help="port number")
    parser.add_argument("--host", type=str, help="host address", default="0.0.0.0")
    parser.add_argument("--peers", type=str, nargs="+", help="other peers to connect to")
    args = parser.parse_args()

    if not args.port:
        raise RuntimeError("was not able to determine a local port")

    if args.peers:
        blockchain.peers.extend(args.peers)

    # GENESIS BLOCK
    header = blockchain.eal_new_header("Evstratiev")
    header.proof = "05082002"
    blockchain.eal_new_block(header)

    # Setting the own host value
    blockchain.host = f"{args.host}:{args.port}"

    app.after_server_start(start_bg)
    app.after_server_stop(stop_bg)
    app.run(host=args.host, port=args.port, debug=False, access_log=False, workers=1)
