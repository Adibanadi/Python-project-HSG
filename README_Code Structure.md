# **How Our Blockchain Is Structured**

Our blockchain is based on two tutorials: [IBM](https://developer.ibm.com/technologies/blockchain/tutorials/develop-a-blockchain-application-from-scratch-in-python/) and [Medium](https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b)

We built a blockchain from scratch in Python, added the possibility to add different nodes to the network (decentralization), and created an enhanced Proof-of-Work (PoW) mechanism to mine blocks.
In the end, we created a blockchain that works: adding transactions, mining blocks (PoW), and broadcasting to the network (consensus) to validate chains to guarantee integrity.

In the following, we demonstrate how our blockchain works and comment on the different blocks of our code.

## 1. Definition of a Block, Blockchain, and Functions

The class block mainly includes the definition of blocks and functions returning the hash of the block.

### 1.1 Defining a block

```sh
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()
```

Defining a function that is returning the hash of the block.

```sh
    def hash_block(self):
        sha = hasher.sha256()
        seq = (str(x) for x in (
            self.index, self.timestamp, self.data, self.previous_hash))
        sha.update(''.join(seq).encode('utf-8'))
        return sha.hexdigest()
```

Creating a helper function which is returning the information on a block as a dictionary. This improves transparency of further functionalities (in terms of code).

```sh
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }
```

A helper function that transforms the information on a block into the JSON format used for communication over the server. We are creating a simple HTTP server that the user can interact and add transactions, mine etc. JSON format is useful because it transmits our request (such as a transaction) to our server in a request body.

```sh
    def to_json(self) -> str:
        return json.dumps(self.to_dict()) + "\n"
```

A helper function which extracts the information about a block.

```sh
    def block_from_request(block_data) -> Block:
        return Block(block_data["index"],
                 block_data["timestamp"],
                 block_data["data"],
                 block_data["previous_hash"])
```

### 1.2 Defining the blockchain

The blockchain is defined as a collection of blocks. The created class includes various functions how blocks are connected, mined, validated, and added. It stores the unconfirmed transactions of a node in a list. Also, blocks of a node's chain are stored in a list which will be appended with newly created blocks.

```sh
class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
```

We have to define a genesis block and append it to the chain. It has the index 0 and the previous_hash 0.

```sh
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
```

##### Proof of Work (PoW) Mechanism

It defines the computational power needed to create a new block.

First, a helper function required for subsequent PoW algorithm. It takes the challenge (which is defined as the hash of the last block) and appends a random string of 25 characters to it.

```sh 
    def generation(self, challenge):
        size = 25
        answer = "".join(
            random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(size))
        attempt = challenge + answer
        return attempt, answer
```

Second, we define the PoW algorithm.

1. Defines the challenge: the hash of the last block
2. Uses the generation function above, which generates a new random "answer", until the attempt (which combines challenge and answer) is associated with a hash that starts with a given required amount of 0's.
3. Returns the answer for which the attempt was associated with a valid hash, which fulfils the requirement.
 
```sh 
    def proof_of_work(self, last_hash):
        challenge = last_hash
        while True:
            attempt, answer = self.generation(challenge)
            shaHash = hasher.sha256(attempt.encode("utf-8"))
            solution = shaHash.hexdigest()
            if solution.startswith("0000"):
                return answer
```

A function which tests if the proof of work meets the criteria. It gets the hash from the last block and the answer from the proof of work and checks if it starts if a given amount of 0's.

```sh 
    def proof_validation(self, answer):
        challenge = self.last_block.hash
        return hasher.sha256((challenge + answer).encode("utf-8")) \
            .hexdigest() \
            .startswith("0000")
```

A function which tests if an added block is valid. I.e. if
1. the previous hash included in the block equals the hash of the previous block
2. the proof of work is valid

```sh 
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
```

A function required to create consensus (see below in chapter 2). It checks the data of each block in a chain if it is valid based on the function above (valid_block).

```sh  
    def validate_and_register_chain(self, chain) -> bool:
        for block_data in chain:
            block = block_from_request(block_data)
            if not self.valid_block(block):
                return False

            self.add_block(block)

        return True
```

A function to mine a new block. The function figures out the proof of work and adds the mining transaction as data in a new block to the blockchain after which it resets the list of unconfirmed transactions, as these have been confirmed.

```sh
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
```

## 2. Definition of Endpoints 

It defines how users of nodes can execute commands including how they can interact. Can be called by users using their host address + any '/command'

Create a copy of node's blockchain.

```sh
blockchain = Blockchain()
blockchain.create_genesis_block()
```

Store the host address data of every other node in the network so that communication between them is possible.

```sh
peer_nodes = set()
```

### Creating Endpoints

### 2.1 Mine

Endpoint which allows user to mine a block if he enters '/mine'

1. The user defines "miner" (his own name) in his request, which is extracted as miner_address, to which
2. block is sent from the network upon successful mining
3. The node then automatically announces to all other nodes that it has mined a new block
4. The user receives information about the new block

```sh
@node.route('/mine', methods=['POST'])
def mine():
    miner_address = request.get_json()["miner"]

    new_block = blockchain.mine(miner_address)

    announce_new_block(new_block)

    return new_block.to_json()
```

When a block is mined by a node, it announces this to all other nodes in its peer nodes and receives status if validated by other nodes or not.

```sh
def announce_new_block(block: Block):
    for peer in peer_nodes:
        url = "{}/share_block".format(peer)
        headers = {'Content-Type': "application/json"}
        response = requests.post(url, data=block.to_json(), headers=headers)
        print(response)
```

### 2.2 Share block

For each of the other nodes the mining node calls the following endpoint which is executed on these nodes host addresses. It extracts the information about the new block, checks it for its validity, whereby if not valid checks for consensus (this ensures that if the node's own blockchain is not the most current one, this does not hinder the validation) and then informs the mining node (user) if validated or not. For each other node on which the validation ran successfully, this specific other node receives a message that a new block mined by another node was added to its blockchain.
Note: We are using a simple HTTP network. Thus, we are using HTTP status codes such as 200 (“Ok”),  201 ('created') or 400 ('bad_request', 'bad').

```sh
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
```

### 2.3 Add transactions

Endpoint which allows user to send coins to another if he enters '/transaction'. It extracts transaction information on each POST request and adds it to the unconfirmed transactions list (Note: transaction is not yet executed, only when next block is mined!).

```sh
@node.route('/add_transaction', methods=['POST'])
def transaction():
    transaction_data = request.get_json()
    blockchain.unconfirmed_transactions.append({
        "from": transaction_data["from"],
        "to": transaction_data["to"],
        "amount": transaction_data['amount'],
    })

    return "Transaction submission successful", 201
```

### 2.4 Registering other nodes

Endpoint which allows user to add another node to its network if he enters '/register_other_node'. Requires user to define "node_address" of other node in his request by manually entering the specific node's host address.

```sh
@node.route('/register_other_node', methods=['POST'])
def register_other_node():
    data = request.get_json()
    node_address = data["node_address"]
    if not node_address:
        return "Invalid data", 400

    peer_nodes.add(node_address)
```

At the same time,

1. adds own host address to registered node's peer list
2. requests from the added node its list of other peers which it filters for the ones not yet in its peer nodes.
3. adds these to its peers list, itself to theirs, and requests their peer nodes list.

Returns the user's own host address which must be deleted from nodes list.

```sh
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
```

A helper function for the registering of new nodes function above.

* Endpoint executed on the host address of the node which is being registered.
* Adds the address of the requesting node to the other node's peer network
* And gets this node's list of peers

```sh
@node.route('/add_to_peers_network', methods=['POST'])
def add_to_peers_network():
    data = request.get_json()
    node_address = data["node_address"]
    if not node_address:
        return "Invalid data", 400

    peer_nodes.add(node_address)

    return json.dumps(list(peer_nodes)), 200
```

*Note: After a node has been added to network (own list of peers), perform consensus to align the blockchains.*

### 2.5 Consensus

Endpoint which allows users to achieve consensus on some version of the chain. Aims at ensuring consistency/integrity of the chain.

```sh
@node.route('/consensus', methods=['GET'])
def perform_consensus():
    consensus()

    return "Made consensus with all other nodes", 200
```

Consensus algorithm iterates over chain of each user (each node) and

1. checks if each block in this chain is valid (using the validate_and_register_chain function defined above)
2. if valid, checks if it is longer than all other chains over which has been iterated based on the rationale that the longest chain is the most current one on which the most work has been done.
3. Let the users know that consensus has been reached.

```sh
def consensus():
    global blockchain
    for chain in find_new_chains():
        new_blockchain = Blockchain()

        if not new_blockchain.validate_and_register_chain(chain):
            continue

        if len(new_blockchain.chain) > len(blockchain.chain):
            blockchain = new_blockchain
```

A helper function for the consensus algorithm
 
Collects the chains of all other nodes in a list by requesting the blocks of their chains using a GET request and converting the JSON object to a Python dictionary to be added to the list

```sh
def find_new_chains():
    other_chains = []
    for node_address in peer_nodes:
        block = requests.get(node_address + "/blocks").content
        block = json.loads(block)
        other_chains.append(block)

    return other_chains
```

### 2.6 Calling the blockchain

For each of the other nodes the node performing the consensus calls the following endpoint which is executed on these nodes host addresses. Collects the blocks of the node's chain in a list and stores it in JSON format to be sent to the node performing the consensus.

```sh
@node.route('/blocks', methods=['GET'])
def get_blocks():
    blocks = []
    for block in blockchain.chain:
        blocks.append(block.to_dict())

    return json.dumps(blocks)
```
