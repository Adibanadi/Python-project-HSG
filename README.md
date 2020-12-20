# **Creating a Blockchain with Python**

Group project#2241. Creating a blockchain with *Python*.

## About

This is a student project of the University of St. Gallen in the course of Programming with Advanced Languages. We created a simple blockchain which is a single chain of blocks as a source of global truth. On the blockchain, our newly generated HSG coin can be transferred (creating a transactions). The transaction is verified through a validation process. 
The user can interact with the blockchain using a simple HTTP network (JSON entries) and can add new nodes to the network. 

The basis of the code follows the tutorials of [IBM](https://developer.ibm.com/technologies/blockchain/tutorials/develop-a-blockchain-application-from-scratch-in-python/) and [Medium](https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b). We combined various features of the tutorials to create a fully functioning blockchain.

In addition to the basic blockchain, we created a proof-of-work mechanism of which the difficulty of the challenge can be adjusted. Also, there is the possibility to add different nodes to get a fully decentralized network on your computer.

## Prerequisites

The program works with Python3 and your local terminal (cmd) using the Flask library (to create a simple HTTP network).

Thus, the following is needed:

* Install [Python](https://www.python.org/downloads/)
* Install [Git](https://git-scm.com/downloads) 
* Install [cURL](https://stackoverflow.com/a/9507379) (to interact with the HTTP network)

## Instructions to Run the Blockchain

The instructions work for both, Mac OS X and Windows.

### 1. Cloning the Project

1. Create a folder to save the blockchain application on your computer.
2. Open the terminal (cmd)
3. Enter *cd* and the path to the file above (e.g. “/pathname/”)
4. Enter *git clone* and https://github.com/Adibanadi/Python-project-HSG (this creates a local copy of the project)
5. Enter *cd* and *”Python-project-HSG”*. This defines the cloned folder as your directory



### 2. Install the Dependencies

1. Enter *pip install Flask*
2. Enter *pip install requests*

Note: This installs the relevant dependencies.

### 3. Start the Blockchain Application

* Enter *python run.py* 

Note: “python” connects to the application. “run.py” is a document in our project which was cloned
Note: The blockchain application now should be up and running at port 5003. This is the first node.

### 4. Perform the Different Functionalities with the Application

Open another terminal to perform functionalities. 
To understand what each functionality does, refer to the [ReadMe_Code Structure](https://github.com/Adibanadi/Python-project-HSG/blob/main/README_Code%20Structure.md). 
For all functionalities the default host address is *http://127.0.0.1:5003/* . However you can replace it with the address you are using.

### 4.1 Mine

To execute mine, enter the following command in the terminal:

```sh
curl -X POST -H "Content-Type: application/json" -d "{\"miner\":\"MyName\"}" http://127.0.0.1:5003/mine
```
Enter your miner name and it will be assigned as a value to the key “miner” (i.e. replace *MyName*)

### 4.2 Transaction

To execute a transaction, enter the following command in the terminal:


```sh
curl -X POST -H "Content-Type: application/json" -d "{\"from\":\"MyName\", \"to\": \"OtherName\", \"amount\": 5}" http://127.0.0.1:5003/add_transaction
```

Enter your own name and it will be assigned as a value to the key “from” (i.e. replace *MyName*).
Enter the recipient’s name and it will be assigned as a value to the key “to” (i.e. replace *OtherName*).
Enter the amount of coins you want to send by assigning it as a value to key “amount” (i.e. replace *5*).
Note: the transaction is submitted, but not yet added to the blockchain. First a new block must be mined, using the mine function. 

### 4.3 Blocks

To see all the blocks of the current Blockchain, enter the following command in the terminal:

```sh
curl http://127.0.0.1:5003/blocks
```

Note: As already described in 4.2, only transactions that were mined will be displayed.

### 5. Add New Node Serves, Which Then Can Interact

So far there was only one participant in the blockchain, to connect more participants new nodes have to be added.
To start a new node, open a *new terminal session*.

Go to the directory where you saved the code. Enter: *cd* and *”../Pyhton-project-HSG”*
For the second node, use the prepared file. Enter: *python run2.py*
Note: You should now have two nodes running. However, they are not connected yet.

### 5.1 Register Other Node

To register another node, enter the code below (in the terminal, where you are operating the blockchain): 
Note: This connects nodes with each other by adding them to each other’s peer network.

```sh
curl -X POST -H "Content-Type: application/json" -d "{\"node_address\":\"http://127.0.0.1:5003\"}" http://127.0.0.1:5005/register_other_node
```

* As explained above, you can change the default address of your local host address if you use a different one (i.e. replace *http://127.0.0.1:5003\*) 
* It is also possible to change the default address of you peer node (i.e. replace * http://127.0.0.1:5005/*)

Note: Bear in mind that if you follow the tutorial step-by-step, you don’t have to change any address.

### 5.2 Consensus

To make sure that both nodes are using the same blockchain you have to use the consensus command. It ensures that both nodes run the longest blockchain. The consensus command will compare the local chain with the network and synchronize them.
To make sure the blockchain is properly working you have to enter the following command for *every* node connected to the network. After executing the command, replace the address with the addresses from the other nodes.

```sh
curl -X GET http://127.0.0.1:5003/consensus
curl -X GET http://127.0.0.1:5005/consensus
```

Note: Both nodes are now connected and can both mine blocks for the same blockchain. 
Note: If you want to double-check, if the consensus worked, enter for the new HTTP address the /blocks code:

```sh
curl http://127.0.0.1:5005/blocks
```


## Files

ReadMe:
* [ReadMe_Code Structure](https://github.com/Adibanadi/Python-project-HSG/blob/main/README_Code%20Structure.md)

Code: 
* [/HSG_coin.py](https://github.com/Adibanadi/Python-project-HSG/blob/main/HSG_coin.py)
* [/run.py](https://github.com/Adibanadi/Python-project-HSG/blob/main/run.py)
* [/run2.py](https://github.com/Adibanadi/Python-project-HSG/blob/main/run2.py)
* [/run3.py](https://github.com/Adibanadi/Python-project-HSG/blob/main/run3.py)

## Description

A simple blockchain containing basic elements which uses the Flask library of Python to create a simple HTTP network for interaction. It is possible to add transactions, mining, and to check the length of the blockchain. 

Mining is based on a specific proof-of-work algorithm, which takes the hash of the last generated block as a challenge to “solve the puzzle” to successfully mine a new block. The implemented consensus algorithm creates a “universal source of truth” in the sense that transactions are validated through mined blocks. The blockchains are broadcasted to the network and only the longest blockchain is accepted and kept.

Additionally, there is the possibility to add different nodes to the network to get a decentralized network on your computer. 

The blockchain can be extended indefinitely.

The structure of our code and a detailed description of it can be found in a separate [ReadMe_Code Structure](https://github.com/Adibanadi/Python-project-HSG/blob/main/README_Code%20Structure.md).

## Sources

The following tutorials were used to build the blockchain in Python.

Tutorial for the blockchain: 
[Medium - Build tiniest blockchain](https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b)

Tutorial for adding nodes:
[IBM - Develop a blockchain](https://developer.ibm.com/technologies/blockchain/tutorials/develop-a-blockchain-application-from-scratch-in-python/)


## Contributors

* Michèle Fiori
* Fabio Gschwind
* Adrian Wyss

## Possible Extension

A possible extension would be a fully integrated web environment for the blockchain without having to operate from the Terminal. For example, HTML/CSS learners could take our code and integrate it into a web application.

