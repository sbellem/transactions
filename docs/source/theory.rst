######
Theory
######

The intent here is to provide some kind of fundamental knowledge with respect
to bitcoin. 

As a starting point the material therein is currently heavily inspired by the
draft version of the book `Bitcoin and Cryptocurrency Technologies`_ by

    * `Arvind Narayanan <http://randomwalker.info/>`_, Princeton University
    * `Joseph Bonneau <http://jbonneau.com/>`_, Princeton University
    * `Edward Felten <https://www.cs.princeton.edu/~felten/>`_, Princeton University
    * `Andrew Miller <https://cs.umd.edu/~amiller/>`_, University of Maryland
    * `Steven Goldfeder <https://www.cs.princeton.edu/~stevenag/>`_, Princeton University
    * `Jeremy Clark <http://users.encs.concordia.ca/~clark/>`_, Concordia University

The long term intention is to extend the material as much as it makes sense
meanwhile weaving a connection to the engineering side of bitcoin.


.. _computer-science-of-bitcoin:

***************************
Computer Science of Bitcoin
***************************
The goal of this section is to dwell on the fundamentals of bitcoin from the
point of view of data structures and algorithms.

Some of the key concepts are:

    * secure hash functions
    * hash pointers and pointer-based acyclic data structures
    * digital signatures
    * cryptocurrencies


Cryptographic Hash Functions
============================
Very briefly, a basic hash function has three main characteristics:

* input value is a string of any size
* output value is of fixed size (i.e.: 256 bits)
* for a string of n bits, the hash function has a running time of O(n)

.. note;; The output value of hash function is also called the hash.

This is more or less good enough to implement a hash table.

In order to make the basic hash function cryptographically secure, three
additional characteristics are required:

* collision‐resistance
* hiding
* puzzle‐friendliness

A hash collition means that for two different input strings the hash function
returns the same hash.

Hash functions have collisions since the number of possible inputs is infinite
whereas the number of possible outputs is finite.

collision‐resistance
  A hash function is collision-resistant if it is not possible to find its
  collisions.

hiding
  Reverse engineering a hash function is not possible. That is, given the hash
  of a hash function, the input string cannot be found.

puzzle‐friendliness
  Very roughly this means that one can pick a puzzle id, k, and bind it to a
  target result y, such that it is difficult to find a value x, which when fed
  to the hash function in combination with k, will yield y. By difficult, is
  meant that there are no better approaches than random trials, and that
  finding x requires substantial time, more than 2^n for if y has n bits.


Hash function in use in Bitcoin
-------------------------------
Several cryptocurrencies like Bitcoin use SHA-256 for verifying transactions
and calculating proof-of-work or proof-of-stake. [#sha256_bitcoin]_

For a more in-depth study of SHA-256 one may consult
`Descriptions of SHA-256, SHA-384, and SHA-512`_ by NIST.



Hash Pointer -based Data Structures
===================================
A hash pointer, points to a location where data is stored along, with the hash
of that data at a given point in time.

Using a hash pointer one can retrieve the data, and verify that the data hasn't
changed.

Using hash pointers, one can build various pointer-based acyclic data
structures such as linked lists, trees, and more generally directed acyclic
graphs.

The bitcoin blockchain can be viewed as a linked list of binary trees, relying
on hash pointers. The hash pointer -based linked list is more precisely called
a hash chain, whereas the hash pointer -based binary tree is called a hash
tree, or `Merkle tree`_, named after its inventor `Ralph Merkle`_.

The hash tree is used to store blocks of transactions, meanwhile the hash
chain is used to link the blocks together.

.. note:: Binary hash trees make it relatively efficient to show the chain of
    transactions a transaction is linked to within a tree. For a tree with n
    transactions, only about log(n) transactions are necessary.


.. _merkle tree: https://en.wikipedia.org/wiki/Merkle_tree
.. _ralph merkle: https://en.wikipedia.org/wiki/Ralph_Merkle


Digital Signatures
==================
A digital signature requires three steps:

* private / public key pair generation
* signature
* verification

Expressed in code:

.. code-block:: python

    private_key, public_key = generate_key_pair(key_size, passphrase=None)

    signature = sign(private_key, message)

    is_valid = verify(public_key, message, signature)

There are two important requirements, one somewhat obvious, and the other more
complex.

* Valid signatures must verify. That is:

.. code-block:: python

    verify(public_key, message, sign(private_key, message)) is True

* Reverse engineering the digital signature scheme, aka forging signatures
  is computationally impossible. That is, for any given message for which the
  the signature, and public key are known, it is not possible to find the
  private key, or to figure out how to create new valid signatures for
  different messages.


Digital signature used in Bitcoin
---------------------------------
For its digital signatures Bitcoin uses the Elliptic Curve Digital Signature
Algorithm (`ECDSA`_).

.. _ecdsa: https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm


Public Keys as Identities & Bitcoin Addresses
---------------------------------------------
Using a digital signature scheme, public keys can be used as identities. In
Bitcoin, public keys are used to identify the sender and receiver in a
transaction. Bitcoin refers to these public keys as "addresses". The sender
can sign the transaction with their private key, meanwhile the receiver can
verify the signature of the transaction using the public key of the sender.


Two simple Cryptocurrency Models
================================
.. _bitcoin-network:



***************
Bitcoin Network
***************

.. todo:: Explain what the bitcoin network is.

    * Its peer-to-peer characteristics.

    Keywords
        nodes, topology, publishing transactions, propagation times, gossip
        protocol


Decentralization
================

Distributed Consensus
=====================


The Blockchain
==============



Proof-of-Work
=============




.. _bitcoin-addresses:

*****************
Bitcoin Addresses
*****************

.. todo:: Explain what a bitcoin address is, starting from the point of view of
    a public key as an identity.

    Keywords
        digital signature, public key & private key pair, hash functions


.. _bitcoin-transactions:

********************
Bitcoin Transactions
********************

.. todo:: Explain what bitcoin transactions are.

    Keywords
        signature, validation, double spend, block creation






**********
References
**********

.. [#sha256_bitcoin] https://en.wikipedia.org/wiki/SHA-2#Applications



.. _Bitcoin and Cryptocurrency Technologies: https://d28rh4a8wq0iu5.cloudfront.net/bitcointech/readings/princeton_bitcoin_book.pdf

.. _Descriptions of SHA-256, SHA-384, and SHA-512:  https://web.archive.org/web/20130526224224/http://csrc.nist.gov/groups/STM/cavp/documents/shs/sha256-384-512.pdf
.. _merkle tree: https://en.wikipedia.org/wiki/Merkle_tree
.. _ralph merkle: https://en.wikipedia.org/wiki/Ralph_Merkle
