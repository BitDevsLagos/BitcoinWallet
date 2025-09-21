# Project Summary: Python Bitcoin Wallet

This document provides a formal summary of the Python implementation of the BitcoinWallet project.

## 1. Core Module: `bitcoin_wallet/wallet.py`

The central component of this implementation is the `BitcoinWallet` class, located in `bitcoin_wallet/wallet.py`.

### 1.1. Design Philosophy

The `BitcoinWallet` class is designed as a simple, in-memory utility for generating Bitcoin keys. It focuses on a single responsibility: creating a master key pair and mnemonic phrase according to BIP39 standards.

Key characteristics include:
- **Stateless Operation:** The class operates entirely in-memory and does not interact with the filesystem. No wallet files are created or read.
- **Ease of Use:** It provides a straightforward interface for generating wallets from scratch or loading them from an existing mnemonic.

### 1.2. Core Functionality

An instance of the `BitcoinWallet` class provides the following methods:

-   `__init__(self, mnemonic=None, ...)`: The constructor initializes a wallet. If a `mnemonic` is provided, it uses it; otherwise, it generates a new 12-word mnemonic phrase.
-   `get_mnemonic()`: Returns the wallet's mnemonic phrase as a string.
-   `get_master_private_key()`: Returns the master private key in Wallet Import Format (WIF).
-   `get_master_public_key()`: Returns the master public key as a hex-encoded string.

## 2. Unit Testing

The project includes a comprehensive test suite to ensure the reliability and correctness of the `BitcoinWallet` class.

-   **Test Module:** `tests/test_wallet.py`
-   **Framework:** `pytest`
-   **Execution:** Tests are run via the `pytest` command from the project root.

### 2.1. Test Coverage

The test suite validates the following behaviors:
-   Correct instantiation of a new wallet with a generated mnemonic.
-   Correct instantiation from a pre-existing mnemonic.
-   Deterministic key generation (i.e., the same mnemonic always produces the same keys).
-   Verification that different mnemonics produce different keys.

## 3. Development History & Key Decisions

-   **Initial Implementation:** An earlier version of the wallet class included filesystem interactions for wallet storage. This was deemed ambiguous and was replaced by the current in-memory design.
-   **Bug Fix (Post-Testing):** During the test implementation phase, a bug was identified in the `get_master_private_key` method. The code was incorrectly accessing the `.wif` attribute as a property instead of calling it as a method (`.wif()`). This was corrected to ensure the method returns the private key as a string, allowing the unit tests to pass.
-   **Unit Testing:** Unit testing might not work on `python` 3.13. Create venv in `python` < 3.13.
