# Cryptographically Enforced Access Control with a Predicate Encryption (PE) scheme for a Personal Health Record (PHR) system

This project was developed for the "Secure Data Management" course at the University of Twente in 2022. This repository contains the implementation of a demonstrator that implements Cryptographically Enforced Access Control with a Predicate Encryption (PE) scheme for a Personal Health Record (PHR) system. The version of the system presented here was developed with a Multi-Authentication Predicate Encryption scheme, where multiple actors can be authorities who issue read/write keys.

The main reference for this project are:

- "Decentralizing attribute-based encryption", from Allison Lewko and Brent Waters;
- "Cryptographically Enforced Data Access Control in Personal Health Record Systems", from GK .Ragesh and K. Baskaran;
- "Ciphertext-Policy Attribute-Based Encryption: An Expressive, Efficient, and Provably Secure Realization", from Brent Waters.

## System requirements

- Python 3.7
- Charm library (check https://jhuisi.github.io/charm/index.html)
- PBC library (check https://crypto.stanford.edu/pbc/download.html)

The code was tested in a Debian-based Linux machine.

## Running the code

To run the demo, just run `python3.7 main.py`.