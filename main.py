from pprint import pprint

from prototype import Blockchain


def pretty_print_block(blockchain: Blockchain, index: int):
    b = blockchain.eal_get_block(index)
    print( "Outputting genesis block info:")
    print(f"    {b}")
    print(f"    Proof: {b.header.proof}")
    print(f"    Nonce: {b.header.nonce}")
    print( "    Transactions: ", end="")
    pprint(b.transactions)
    print()


if __name__ == '__main__':
    blockchain = Blockchain("Andrew", "0508")
    print("Initial chain:", blockchain)
    print()

    # Note(andrew): Here we are creating a custom genesis block, by first creating new header,
    #     with our arbitrary message as a previous hash (and also adding arbitrary proof). And,
    #     then, we craft new block from the header. Note, that "nonce" in our genesis block is
    #     going to be 0, but it's not a real nonce, because we did not do any actual work to
    #     create this block. Notice, that we don't add 'Coinbase' transaction to the genesis
    #     block (lets not give it to anyone, since it's hardcoded).
    header = blockchain.eal_new_header("Evstratiev")
    header.proof = "05082002"
    blockchain.eal_new_block(header)

    # Note(andrew): Here we are running a mining loop, mining certain amount of blocks before
    #     exiting the program.
    EAL_AMOUNT_TO_MINE = 4

    while EAL_AMOUNT_TO_MINE:
        blockchain.eal_add_transaction("Alice", blockchain.owner_addr, Blockchain.eal_float_to_coin(0.4))
        blockchain.eal_add_transaction("Bob",   blockchain.owner_addr, Blockchain.eal_float_to_coin(0.24))

        blockchain.eal_mine()
        EAL_AMOUNT_TO_MINE -= 1

    # Output the whole blockchain.
    print()
    print("Result chain:", blockchain)

    # Get the first (genesis) block.
    pretty_print_block(blockchain, 1)

    # Get info about second block.
    pretty_print_block(blockchain, 2)
