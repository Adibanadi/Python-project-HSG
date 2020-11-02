from flask import Flask
from flask import request
import json
import requests
import hashlib as hasher
import datetime as date
import string
import random

node = Flask(__name__)


# Part 1: Definition of a block, a blockchain, and functions
# which can be performed on these


# Define what a block is,
# including function returning the hash of the block
class Block:
<<<<<<< HEAD
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

    # Helper function returning the information on a block as a dictionary
    # Improves transparency of further functionalities (in terms of code)
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    # Helper function transforms the information on a block (as defined above)
    # into the json format used for communication over server
    def to_json(self) -> str:
        return json.dumps(self.to_dict()) + "\n"


# Helper function which extracts the information about a block
# used in other functions below
def block_from_request(block_data) -> Block:
    return Block(block_data["index"],
                 block_data["timestamp"],
                 block_data["data"],
                 block_data["previous_hash"])


# Define a blockchain as a collection of blocks
# Includes various functions how blocks are connected, minded, validated, and added
# Stores the unconfirmed transactions of this node in a list
# Stores the blocks of this node's chain in a list which will be appended with newly created blocks
class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    # Generate genesis block and append it to the chain
    # Has index 0 and previous_hash 0
    def create_genesis_block(self):
        genesis_block = Block(0, date.datetime.now(), {
            "proof-of-work": None,
            "transactions": None,
        }, "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, block: Block):
        self.chain.append(block)

    # Proof of work: Work required to mine a new block
    # I. Helping function required for the subsequent proof of work algorithm
    # Takes the challenge (which is defined as the hash of the last block)
    # and appends a random string of 25 characters to it
    def generation(self, challenge):
        size = 25
        answer = "".join(
            random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(size))
        attempt = challenge + answer
        return attempt, answer

    # II. Proof of work algorithm
    # 1. Defines the challenge: the hash of the last block
    # 2. Uses the generation function above, which generates a new random "answer",
    # until the attempt (which combines challenge and answer) is associated with a hash
    # that starts with a given required amount of 0's.
    # 3. Returns the answer for which the attempt was associated with a valid hash,
    # which fulfils the requirement.
    # TODO Open points: 1. the time a miner needs to create a a new block.2. Difficulty adjusting.
    # TODO 3. Instead of using the last hash as challenge, using data from the transactions
    # TODO (like code below, but its not yet working) challenge = hasher.sha256(block.encode()).hexdigest()
    def proof_of_work(self, last_hash):
        challenge = last_hash
        while True:
            attempt, answer = self.generation(challenge)
            shaHash = hasher.sha256(attempt.encode("utf-8"))
            solution = shaHash.hexdigest()
            if solution.startswith("0000"):
                return answer

    # Function which tests if the proof of work meets the criteria
    # Gets the hash from the last block and the answer from the proof of work
    # and check if it starts if a given amount of 0's.
    def proof_validation(self, answer):
        challenge = self.last_block.hash
        return hasher.sha256((challenge + answer).encode("utf-8")) \
            .hexdigest() \
            .startswith("0000")

    # Function which tests if an added block is valid, i.e. if
    #  1. the previous hash included in the block equals the hash of the previous block
    #  2. the proof of work is valid
    def valid_block(self, block: Block) -> bool:
        # If chain is empty we can add any block, which is the genesis block
        if len(self.chain) == 0:
            return True

        if self.last_block.hash != block.previous_hash:
            return False

        answer = block.data["proof-of-work"]
        if not self.proof_validation(answer):
            return False

        return True

    # Function required to create consensus (see below in part 2)
    # which checks the data of each block in a chain if it is valid
    # based on the function above
    def validate_and_register_chain(self, chain) -> bool:
        for block_data in chain:
            block = block_from_request(block_data)
            if not self.valid_block(block):
                return False

            self.add_block(block)

        return True

    # Function to mine a new block
    # Figures out the proof of work,
    # Adds the mining transaction as data in a new block to the blockchain
    # After which it resets the list of unconfirmed transactions, as these have been confirmed
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


# Part 2: Definition of endpoints how users of nodes can execute commands
# including how they can interact
# Can be called by users using the their host address + any '/command'


# Create copy of node's blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# Store the host address data of every other node in the network
# so that communication between them is possible
peer_nodes = set()


# Endpoint which allows user to mine a block if he enters '/mine'
# 1. The user defines "miner" (his own name) in his request,
# which is extracted as miner_address, to which
# 2. block is sent from the network upon successful mining
# 3. The node then automatically announces to all other nodes
# that it has mined a new block
# 4. The user receives information about the new block
@node.route('/mine', methods=['POST'])
def mine():
    miner_address = request.get_json()["miner"]

    new_block = blockchain.mine(miner_address)

    announce_new_block(new_block)

    return new_block.to_json()


# When a block is mined by a node,
# it announces this to all other nodes in its peer nodes
# and receives status if validated by other nodes or not
def announce_new_block(block: Block):
    for peer in peer_nodes:
        url = "{}/share_block".format(peer)
        headers = {'Content-Type': "application/json"}
        response = requests.post(url, data=block.to_json(), headers=headers)
        print(response)


# For each of the other nodes the mining node calls the following endpoint
# which is executed on these nodes host addresses.
# Extracts the information about the new block,
# checks it for its validity, whereby if not valid checks for consensus
# (this ensures that if the node's own blockchain is not the most current
# one, this does not hinder the validation)
# and then informs the mining node (user) if validated or not.
# For each other node on which the validation ran successfully,
# this specific other node receives a message
# that a new block mined by another node was added to its blockchain.
@node.route('/share_block', methods=['POST'])
def share_block():
    block_data = request.get_json()

    block = block_from_request(block_data)

    if not blockchain.valid_block(block):
        consensus()
        return "Block is invalid and not added to the shared blockchain", 400

    blockchain.add_block(block)
    print("Added new block mined by different node to blockchain")
    return "Block has been added to the shared blockchain", 201


# Endpoint which allows user to send coins to another if he enters '/transaction'
# Extracts transaction information on each POST request
# and adds it to the unconfirmed transactions list
# (Note: transaction is not yet executed, only when next block is mined)
@node.route('/add_transaction', methods=['POST'])
=======
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

# Generate genesis block
def create_genesis_block():
  # Manually construct a block with
  # index zero and arbitrary previous hash
  return Block(0, date.datetime.now(), {
    "proof-of-work": 9,
    "transactions": None
  }, "0")

# A completely random address of the owner of this node
miner_address = "random-miner-address"
# This node's blockchain copy
blockchain = []
blockchain.append(create_genesis_block())
# Store the transactions that
# this node has in a list
this_nodes_transactions = []
# Store the url data of every
# other node in the network
# so that we can communicate
# with them
peer_nodes = []
# A variable to deciding if we're mining or not
mining = True

@node.route('/txion', methods=['POST'])
>>>>>>> f32d57560d1b10b90a342ab80cdd5700f713d723
def transaction():
    transaction_data = request.get_json()
    blockchain.unconfirmed_transactions.append({
        "from": transaction_data["from"],
        "to": transaction_data["to"],
        "amount": transaction_data['amount'],
    })

    return "Transaction submission successful", 201


# Endpoint which allows user to add another node to its network
# if he enters '/register_other_node'
# Requires user to define "node_address" of other node in his request
# by manually entering the specific node's host address
@node.route('/register_other_node', methods=['POST'])
def register_other_node():
    data = request.get_json()
    node_address = data["node_address"]
    if not node_address:
        return "Invalid data", 400

    peer_nodes.add(node_address)

    # At the same time,
    # 1. adds own host address to registered node's peer list
    # 2. requests from the added node its list of other peers
    # which it filters for the ones not yet in its peer nodes.
    # 3. adds these to its peers list, itself to theirs, and requests their peer nodes list.

    # Returns the user's own host address which must be deleted from nodes list
    current_url = request.host_url.strip("/")
    url = "{}/add_to_peers_network".format(node_address)
    headers = {'Content-Type': "application/json"}
    response = requests.post(url, data=json.dumps({"node_address": current_url}), headers=headers)
    new_peer_nodes = set(response.json())
    new_peer_nodes.remove(current_url)
    new_peer_nodes = new_peer_nodes - peer_nodes
    peer_nodes.update(new_peer_nodes)
    for peer_node in new_peer_nodes:
        url = "{}/add_to_peers_network".format(peer_node)
        headers = {'Content-Type': "application/json"}
        requests.post(url, data={"node_address": current_url}, headers=headers)

    return "Accepted node"


# Helper function for the registering of new nodes function above
# Endpoint executed on the host address of the node which is being registered
# Adds the address of the requesting node to the other node's peer network
# And gets this node's list of peers
@node.route('/add_to_peers_network', methods=['POST'])
def add_to_peers_network():
    data = request.get_json()
    node_address = data["node_address"]
    if not node_address:
        return "Invalid data", 400

    peer_nodes.add(node_address)

    return json.dumps(list(peer_nodes)), 200

# Note: After a node has been added to network (own list of peers),
# perform consensus to align the blockchains


# Endpoint which allows users to achieve consensus on some version of the chain
# Aims at ensuring consistency/integrity of the chain
@node.route('/consensus', methods=['GET'])
def perform_consensus():
    consensus()

    return "Made consensus with all other nodes", 200


# Consensus algorithm iterates over chain of each user (each node) and
# 1. checks if each block in this chain is valid
# (using the validate_and_register_chain function defined above)
# 2. if valid, checks if it is longer than all other chains over which has been iterated
# based on the rationale that the longest chain is the most current one
# on which the most work has been done
# 3. Lets the user know that consensus has been reached
def consensus():
<<<<<<< HEAD
    global blockchain
    for chain in find_new_chains():
        new_blockchain = Blockchain()

        if not new_blockchain.validate_and_register_chain(chain):
            continue

        if len(new_blockchain.chain) > len(blockchain.chain):
            blockchain = new_blockchain


# Helper function for the consensus algorithm
# Collects the chains of all other nodes in a list
# by requesting the blocks of their chains using a GET request
# and converting the JSON object to a Python dictionary to be added to the list
def find_new_chains():
    other_chains = []
    for node_address in peer_nodes:
        block = requests.get(node_address + "/blocks").content
        block = json.loads(block)
        other_chains.append(block)

    return other_chains


# For each of the other nodes the node performing the consensus calls the following endpoint
# which is executed on these nodes host addresses.
# Collects the blocks of the node's chain in a list
# and stores it in JSON format to be sent to the node performing the consensus
@node.route('/blocks', methods=['GET'])
def get_blocks():
    blocks = []
    for block in blockchain.chain:
        blocks.append(block.to_dict())

    return json.dumps(blocks)
=======
  # Get the blocks from other nodes
  other_chains = find_new_chains()
  # If our chain isn't longest,
  # then we store the longest chain
  longest_chain = blockchain
  for chain in other_chains:
    if len(longest_chain) < len(chain):
      longest_chain = chain
  # If the longest chain isn't ours,
  # then we stop mining and set
  # our chain to the longest one
  blockchain = longest_chain

#Taking the challenge and appending a random string of 25 characters to it
def generation (challenge):
  size = 25
  answer = "".join(random.choice(string.ascii_lowercase+string.ascii_uppercase+string.digits) for x in range(size))
  attempt = challenge + answer
  return attempt, answer

#Taking the hash of the last block and setting it as the challenge
#Using the generation function to create new hashes until it starts with a given amount of 0's.
#Returning the answer which was created with the generation function
#Open points: 1. the time a miner needs to create a a new block. 2. Difficulty adjusting. 3. Instead of using the last hash as challenge, using data from the transactions (like code below, but its not yet working)
#challenge = hasher.sha256(block.encode()).hexdigest()
def proof_of_work(last_hash):
    Found = False
    challenge = last_hash
    start = time.time()
    while Found == False:
        attempt, answer = generation(challenge)
        shaHash = hasher.sha256(attempt.encode("utf-8"))
        solution = shaHash.hexdigest()
        if solution.startswith("0000"):
            TimeTook = time.time() -start
            #print("Time took:",TimeTook)
            Found=True
            return(answer)

#Testing if the proof of work actually meets the creteria
#getting the hash from the last block and the answer from the proof of work and check if it starts if a given amount of 0's
def proof_validation(answer):
  challenge = blockchain[len(blockchain) - 1].hash
  if hasher.sha256((challenge + answer).encode("utf-8")).hexdigest().startswith("0000"):
    return True
  else:
    return False

@node.route('/mine', methods = ['GET'])
def mine():
  # Get the hash of the last block
  last_block = blockchain[len(blockchain) - 1]
  last_hash = last_block.hash
  # Find the proof of work for
  # the current block being mined
  # Note: The program will hang here until a new
  #       proof of work is found
  answer = proof_of_work(last_hash)
  #Testing if the proof is legit and proceeding if everything is okay
  if proof_validation(answer) == False:
    #Comment Adrian: the printing is not yet working and I don't know why (it just crashes if proof not valid, which is kinda okay)
    print("Validation was not successfull, try again.")
  else:
    # Once we find a valid proof of work,
    # we know we can mine a block so 
    # we reward the miner by adding a transaction
    this_nodes_transactions.append(
      { "from": "network", "to": miner_address, "amount": 1 }
    )
    # Now we can gather the data needed
    # to create the new block
    new_block_data = {
      "proof-of-work": answer,
      "transactions": list(this_nodes_transactions)
    }
    new_block_index = last_block.index + 1
    new_block_timestamp = this_timestamp = date.datetime.now()
    last_block_hash = last_block.hash
    # Empty transaction list
    this_nodes_transactions[:] = []
    # Now create the
    # new block!
    mined_block = Block(
      new_block_index,
      new_block_timestamp,
      new_block_data,
      last_block_hash
    )
    blockchain.append(mined_block)
    # Let the client know we mined a block
    return json.dumps({
        "index": new_block_index,
        "timestamp": str(new_block_timestamp),
        "data": new_block_data,
        "hash": last_block_hash
    }) + "\n"

node.run()
>>>>>>> f32d57560d1b10b90a342ab80cdd5700f713d723
