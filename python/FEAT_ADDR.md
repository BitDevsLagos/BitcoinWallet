
# Feature: Address Management and QR Code Generation (Updated)

This document tracks the implementation of address management (Bech32 for now) and QR code generation for receiving addresses in the `BitcoinWallet` class.

## 1. Branch

All work is being done on the `feat/address` branch, created from the `python` branch.

## 2. Dependency Updates

The following dependency will be added to `requirements.txt` (for future QR code generation):

- `qrcode[pil]`: For generating QR code images.

After adding, run:
```
pip install -r requirements.txt
```

## 3. `BitcoinWallet` Class Enhancements (`bitcoin_wallet/wallet.py`)

### Address Generation

- The `BitcoinWallet` class now provides a `get_address()` method that returns a Bech32 (P2WPKH) address with the correct prefix for the selected network:
  - If `network='bitcoin'`, the address starts with `bc1` (mainnet).
  - If `network='testnet'`, the address starts with `tb1` (testnet).
- The address returned is always in Bech32 format for now.

#### Example usage:
```python
wallet = BitcoinWallet(network='bitcoin')
print(wallet.get_address())  # Outputs a bc1... address
```

### QR Code Generation (Planned)

- A method for generating QR codes for addresses will be added in a future update.

## 4. Testing (`tests/test_wallet.py`)

The test suite has been updated to cover the new functionality:

- **Test Bech32 Address Format:**
  - Tests verify that `get_address()` returns a valid Bech32 address (starting with `bc1` for mainnet).

## 5. `.gitignore`

The `.gitignore` file will be updated to include `*.png` to prevent QR code image files from being accidentally committed to the repository (when QR code feature is added).

---

## Next Feature: Address Type Choice

The next address-related feature will allow users to choose whether to generate a legacy P2PKH address or a modern Bech32 address, via a method parameter or class option.
