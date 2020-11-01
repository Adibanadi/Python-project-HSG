from flask import Flask
from flask import request
import json
import requests
import hashlib as hasher
import datetime as date
import string
import random

node = Flask(__name__)


# Define what a block is,
# including function returning the hash of the block
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        seq = (str(x) for x in (
            self.index, self.timestamp, self.data, self.previous_hash))
        sha.update(''.join(seq).encode('utf-8'))
        return sha.hexdigest()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict()) + "\n"



# Define a blockchain as a collection of blocks, includes:
# Store the transactions of this node in a list which will be appended with new transactions made
# Store the blocks of this node's chain in a list which will be appended with newly created blocks
class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    # Generate genesis block and append it to the chain
    # Has index 0, previous_hash 0
    def create_genesis_block(self):
        # Hardcode time so all nodes have the same genesis block
        genesis_block = Block(0, date.datetime.now(), {
            "proof-of-work": None,
            "transactions": None,
        }, "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    # Function adding a new block
    def add_block(self, block: Block):
        self.chain.append(block)

    # Validate the block if
    #  1. previous hash included in the block equals the hash of the previous block
    #  2. proof of work is valid
    def valid_block(self, block: Block) -> bool:
        # If chain is empty we can add any block
        if len(self.chain) == 0:
            return True

        if self.last_block.hash != block.previous_hash:
            return False

        answer = block.data["proof-of-work"]
        if not self.proof_validation(answer):
            return False

        return True

    # Proof of work algorithm - helping function required for the proof of work below
    # Takes the challenge (which is defined as the hash of the last block)
    # and appends a random string of 25 characters to it
    def generation(self, challenge):
        size = 25
        answer = "".join(
            random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(size))
        attempt = challenge + answer
        return attempt, answer

    # Proof of work algorithm
    # 1. Defines the challenge: the hash of the last block
    # 2. Uses the generation function above, which generates a new random "answer",
    # until the attempt (which combines challenge and answer)
    # is associated with a hash that starts with a given required amount of 0's.
    # 3. Returns the answer for which the attempt was associated with a valid hash,
    # which fulfils the requirement.
    # Open points: 1. the time a miner needs to create a a new block.2. Difficulty adjusting.
    # 3. Instead of using the last hash as challenge, using data from the transactions
    # (like code below, but its not yet working)
    # challenge = hasher.sha256(block.encode()).hexdigest()
    def proof_of_work(self, last_hash):
        challenge = last_hash
        while True:
            attempt, answer = self.generation(challenge)
            shaHash = hasher.sha256(attempt.encode("utf-8"))
            solution = shaHash.hexdigest()
            if solution.startswith("0000"):
                return answer

    # Testing if the proof of work actually meets the criteria
    # getting the hash from the last block and the answer from the proof of work
    # and check if it starts if a given amount of 0's
    def proof_validation(self, answer):
        challenge = self.last_block.hash
        return hasher.sha256((challenge + answer).encode("utf-8")) \
            .hexdigest() \
            .startswith("0000")

    # Mine a new block by figuring out the proof of work and
    # adding the mining transaction as data in a new block to the blockchain
    def mine(self, miner_address) -> Block:

        previous_block = self.last_block
        proof_of_work = self.proof_of_work(previous_block.hash)
        self.unconfirmed_transactions.append({"from": "network", "to": miner_address, "amount": 1})

        new_block = Block(index=previous_block.index + 1,
                          data={
                              "proof-of-work": proof_of_work,
                              "transactions": self.unconfirmed_transactions,
                          },
                          timestamp=date.datetime.now(),
                          previous_hash=previous_block.hash)

        self.add_block(new_block)
        self.unconfirmed_transactions = []

        return new_block

    def validate_and_register_chain(self, chain) -> bool:
        for block_data in chain:
            block = block_from_request(block_data)
            if not self.valid_block(block):
                return False

            self.add_block(block)

        return True


# Create copy of node's blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# Store the url data of every other node in the network
# so that we can communicate with them
peer_nodes = set()


@node.route('/add_transaction', methods=['POST'])
def transaction():
    # On each new POST request, we extract the transaction data
    transaction_data = request.get_json()
    blockchain.unconfirmed_transactions.append({
        "from": transaction_data["from"],
        "to": transaction_data["to"],
        "amount": transaction_data['amount'],
    })

    return "Transaction submission successful", 201


@node.route('/blocks', methods=['GET'])
def get_blocks():
    blocks = []
    for block in blockchain.chain:
        blocks.append(block.to_dict())

    return json.dumps(blocks)


def find_new_chains():
    # Get the blockchains of every other node
    other_chains = []
    for node_url in peer_nodes:
        # Get their chains using a GET request
        block = requests.get(node_url + "/blocks").content
        # Convert the JSON object to a Python dictionary
        block = json.loads(block)
        # Add it to our list
        other_chains.append(block)

    return other_chains


@node.route('/consensus', methods=['GET'])
def consensus():
    global blockchain

    for chain in find_new_chains():
        new_blockchain = Blockchain()

        if not new_blockchain.validate_and_register_chain(chain):
            continue

        if len(new_blockchain.chain) > len(blockchain.chain):
            blockchain = new_blockchain

    return "Made consensus with all other nodes", 200


@node.route('/mine', methods=['POST'])
def mine():
    miner_address = request.get_json()["miner"]

    new_block = blockchain.mine(miner_address)

    announce_new_block(new_block)

    # Let the user know that a block was mined
    return new_block.to_json()


# When another node mines a new block it notifies us
# using this route with the new block.
@node.route('/add_block', methods=['POST'])
def add_block():
    block_data = request.get_json()

    block = block_from_request(block_data)

    if not blockchain.valid_block(block):
        return "Block is invalid and not added to our blockchain", 400

    blockchain.add_block(block)

    return "Block has been added to our blockchain", 201


@node.route('/register_node', methods=['POST'])
def register_node():
    data = request.get_json()
    node_address = data["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peer_nodes.add(node_address)

    return "Accepted node"


def announce_new_block(block: Block):
    for peer in peer_nodes:
        url = "{}/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url, data=block.to_json(), headers=headers)


def block_from_request(block_data) -> Block:
    return Block(block_data["index"],
                 block_data["timestamp"],
                 block_data["data"],
                 block_data["previous_hash"])
