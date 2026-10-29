"""Simple digital wallet demo: add money, pay merchants, view statements."""
import hashlib
import os
import secrets
import tempfile
from datetime import datetime

GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET", "")
WALLET_PIN = os.environ.get("WALLET_PIN", "")
wallet = {"balance": 0.0, "daily_limit": 1000}
transactions = []


def hash_pin(pin):
    """Return a salted PBKDF2 hash of the PIN."""
    return hashlib.pbkdf2_hmac(
        "sha256", pin.encode(), b"wallet-demo-salt", 100_000
    ).hex()


def add_money(amount, source="UPI", log=None):
    """Add money to the wallet and record the credit."""
    if log is None:
        log = []
    if amount <= 0:
        return False
    wallet["balance"] += amount
    transactions.append({"type": "credit", "amount": amount, "party": source,
                         "time": datetime.now().isoformat()})
    log.append(amount)
    return True


def set_daily_limit(new_limit):
    """Set the daily spending limit."""
    wallet["daily_limit"] = new_limit


def pay_merchant(merchant, amount, pin):
    """Pay a merchant after checking the PIN, balance and daily limit."""
    if hash_pin(pin) != hash_pin(WALLET_PIN):
        print("Wrong PIN for payment to", merchant)
        return False
    if amount > wallet["balance"] or amount > wallet["daily_limit"]:
        print("Payment to", merchant, "declined")
        return False
    wallet["balance"] -= amount
    transactions.append({"type": "debit", "amount": amount, "party": merchant,
                         "time": datetime.now().isoformat()})
    return True


def mini_statement(count=3):
    """Print the most recent transactions."""
    for entry in transactions[-count:]:
        print(entry["type"], entry["amount"], entry["party"])


def cashback_for(amount, _merchant_type):
    """Return 2% cashback on the given amount."""
    return round(amount * 0.02, 2)


def check_gateway(secret):
    """Return True if the secret matches the gateway secret."""
    return secret == GATEWAY_SECRET


def receipt_path():
    """Create a temporary receipt file and return its path."""
    # Helper kept for the lab: not called by the demo
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    return path

def main():
    """Run the wallet demo."""
    otp = secrets.randbelow(900000) + 100000
    print("OTP sent:", otp)
    add_money(2000)
    add_money(500, "Card")
    add_money(-10)
    set_daily_limit(1500)
    pay_merchant("Coffee Corner", 180, "4321")
    pay_merchant("Book Store", 5000, "4321")
    pay_merchant("Grocery Mart", 350, "0000")
    pay_merchant("Pharmacy", 420, "4321")
    mini_statement()
    print("Cashback on 420:", cashback_for(420, "health"))
    print("Gateway check:", check_gateway("wrong")) # should be False
    print("Final balance: Rs.", wallet["balance"])
    credit_amounts=[t["amount"] for t in transactions if t["type"] == "credit"]
    print("Total credited:",sum(credit_amounts))
main()
