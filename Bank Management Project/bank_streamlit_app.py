import json
import secrets
import string
import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
import shutil
import streamlit as st
from datetime import datetime
import re
import io
import csv

DATA_FILE = Path("data.json")

# ---------- Storage helpers ----------
def _read_data():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except Exception:
        return []

def _atomic_write(data):
    tmp = NamedTemporaryFile("w", delete=False, encoding="utf-8")
    try:
        tmp.write(json.dumps(data, indent=2))
        tmp.flush()
        tmp.close()
        shutil.move(tmp.name, DATA_FILE)
    finally:
        try:
            tmp.close()
        except Exception:
            pass

# ---------- Security helpers ----------
def _hash_pin(pin: str, salt: str) -> str:
    return hashlib.sha256((pin + salt).encode("utf-8")).hexdigest()

def _generate_account_no(length: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def _is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

# ---------- Core bank logic ----------
class Bank:
    def __init__(self):
        self.data = _read_data()

    def save(self):
        _atomic_write(self.data)

    def find_user(self, account_no: str):
        for user in self.data:
            if user.get("accountNo") == account_no:
                return user
        return None

    def create_account(self, name: str, age: int, email: str, pin: str) -> dict:
        name = name.strip()
        email = email.strip()
        if not name:
            raise ValueError("Name is required")
        if age < 18:
            raise ValueError("Minimum age is 18")
        if not _is_valid_email(email):
            raise ValueError("Enter a valid email")
        if len(pin) != 4 or not pin.isdigit():
            raise ValueError("PIN must be 4 digits")

        for _ in range(200):
            acc = _generate_account_no(10)
            if not self.find_user(acc):
                break
        else:
            raise RuntimeError("Unable to generate unique account number")

        salt = secrets.token_hex(8)
        user = {
            "name": name,
            "age": age,
            "email": email,
            "pin_salt": salt,
            "pin_hash": _hash_pin(pin, salt),
            "accountNo": acc,
            "balance": 0,
            "created_at": datetime.utcnow().isoformat(),
            "transactions": []
        }
        self.data.append(user)
        self.save()
        return user

    def authenticate(self, account_no: str, pin: str):
        user = self.find_user(account_no)
        if not user:
            return None
        expected = user.get("pin_hash")
        salt = user.get("pin_salt")
        if expected == _hash_pin(pin, salt):
            return user
        return None

    def deposit(self, account_no: str, amount: int, note: str = ""):
        if amount <= 0 or amount > 1000000:
            raise ValueError("Amount must be between 1 and 1,000,000")
        user = self.find_user(account_no)
        if not user:
            raise ValueError("Account not found")
        user["balance"] = int(user.get("balance", 0)) + int(amount)
        user["transactions"].append({
            "ts": datetime.utcnow().isoformat(),
            "type": "deposit",
            "amount": int(amount),
            "balance": user["balance"],
            "note": note,
        })
        self.save()
        return user["balance"]

    def withdraw(self, account_no: str, amount: int, note: str = ""):
        if amount <= 0:
            raise ValueError("Invalid amount")
        user = self.find_user(account_no)
        if not user:
            raise ValueError("Account not found")
        if user.get("balance", 0) < amount:
            raise ValueError("Insufficient balance")
        user["balance"] = int(user.get("balance", 0)) - int(amount)
        user["transactions"].append({
            "ts": datetime.utcnow().isoformat(),
            "type": "withdraw",
            "amount": int(amount),
            "balance": user["balance"],
            "note": note,
        })
        self.save()
        return user["balance"]

    def update_details(self, account_no: str, **kwargs):
        user = self.find_user(account_no)
        if not user:
            raise ValueError("Account not found")
        if "name" in kwargs and kwargs["name"] is not None:
            user["name"] = kwargs["name"].strip()
        if "email" in kwargs and kwargs["email"] is not None:
            if not _is_valid_email(kwargs["email"]):
                raise ValueError("Enter a valid email")
            user["email"] = kwargs["email"].strip()
        if "pin" in kwargs and kwargs["pin"]:
            pin = kwargs["pin"]
            if len(pin) != 4 or not pin.isdigit():
                raise ValueError("PIN must be 4 digits")
            salt = secrets.token_hex(8)
            user["pin_salt"] = salt
            user["pin_hash"] = _hash_pin(pin, salt)
        self.save()
        return user

    def delete_account(self, account_no: str):
        user = self.find_user(account_no)
        if not user:
            raise ValueError("Account not found")
        self.data.remove(user)
        self.save()
        return True

# ---------- Streamlit UI ----------
bank = Bank()

st.set_page_config(page_title="Simple Bank • Streamlit", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

# top bar
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Simple Bank — Demo")
    st.markdown("A local demo for learning Streamlit and Python. Not for real money.")
with col2:
    if st.session_state.user:
        st.metric("Logged in as", st.session_state.user.get("name"))
    else:
        st.write(" ")

menu = st.sidebar.selectbox("Choose action", [
    "Home",
    "Create Account",
    "Login",
    "Admin: Accounts",
])

if menu == "Home":
    st.header("Welcome")
    st.write("This demo supports account creation, login, deposits, withdrawals, and transaction history.")
    st.info("PINs are hashed with a per-account salt. This is a demo only.")

if menu == "Create Account":
    st.header("Create a new account")
    with st.form("create_form"):
        name = st.text_input("Full name")
        age = st.number_input("Age", min_value=0, max_value=120, value=18)
        email = st.text_input("Email")
        pin = st.text_input("4-digit PIN", max_chars=4, type="password")
        submitted = st.form_submit_button("Create account")
        if submitted:
            try:
                user = bank.create_account(name, int(age), email, pin)
                st.success("Account created successfully 🎉")
                st.write("Your account number (store it safely):")
                st.code(user["accountNo"])
            except Exception as e:
                st.error(str(e))

if menu == "Login":
    st.header("Account login")
    if st.session_state.user:
        st.success(f"You are logged in as {st.session_state.user['name']}")
        st.write(f"Account: `{st.session_state.user['accountNo']}`")
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()
        with cols[1]:
            if st.button("Refresh from disk"):
                bank.data = _read_data()
                st.session_state.user = bank.find_user(st.session_state.user["accountNo"]) or None
                st.rerun()

        st.subheader("Account dashboard")
        user = st.session_state.user
        left, right = st.columns([2, 1])
        with left:
            st.markdown("**Quick actions**")
            action = st.selectbox("Choose an action", ["Show details", "Deposit", "Withdraw", "Update details", "Delete account", "Transactions"])

            if action == "Show details":
                st.write("### Details")
                safe_view = {k: v for k, v in user.items() if k not in ("pin_hash", "pin_salt")}
                st.json(safe_view)

            if action == "Deposit":
                st.write("### Deposit")
                with st.form("dep_form"):
                    amt = st.number_input("Amount", min_value=1, value=100)
                    note = st.text_input("Note (optional)")
                    submit = st.form_submit_button("Deposit")
                    if submit:
                        try:
                            newbal = bank.deposit(user["accountNo"], int(amt), note)
                            st.success(f"Deposited ₹{amt}. New balance: ₹{newbal}")
                            st.session_state.user = bank.find_user(user["accountNo"])
                        except Exception as e:
                            st.error(str(e))

            if action == "Withdraw":
                st.write("### Withdraw")
                with st.form("wd_form"):
                    amt = st.number_input("Amount", min_value=1, value=100)
                    note = st.text_input("Note (optional)")
                    submit = st.form_submit_button("Withdraw")
                    if submit:
                        try:
                            newbal = bank.withdraw(user["accountNo"], int(amt), note)
                            st.success(f"Withdrawn ₹{amt}. New balance: ₹{newbal}")
                            st.session_state.user = bank.find_user(user["accountNo"])
                        except Exception as e:
                            st.error(str(e))

            if action == "Update details":
                st.write("### Update details")
                with st.form("upd_form"):
                    new_name = st.text_input("Name", value=user["name"])
                    new_email = st.text_input("Email", value=user["email"])
                    new_pin = st.text_input("New 4-digit PIN (leave blank to keep)", max_chars=4, type="password")
                    submit = st.form_submit_button("Update")
                    if submit:
                        try:
                            updated = bank.update_details(user["accountNo"], name=new_name, email=new_email, pin=new_pin)
                            st.success("Details updated")
                            st.session_state.user = bank.find_user(user["accountNo"])
                        except Exception as e:
                            st.error(str(e))

            if action == "Delete account":
                st.write("### Delete account")
                st.warning("This will permanently remove your account and all transactions.")
                confirm = st.text_input("Type DELETE to confirm", key="del_confirm")
                if st.button("Delete account"):
                    if confirm == "DELETE":
                        try:
                            bank.delete_account(user["accountNo"])
                            st.success("Account deleted.")
                            st.session_state.user = None
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    else:
                        st.info("Type DELETE to confirm deletion")

            if action == "Transactions":
                st.write("### Transaction history")
                txs = user.get("transactions", [])
                if not txs:
                    st.info("No transactions yet")
                else:
                    rows = list(reversed(txs))
                    st.table([
                        {"time": r["ts"], "type": r["type"], "amount": r["amount"], "balance": r["balance"], "note": r.get("note", "")}
                        for r in rows
                    ])
                    csv_buf = io.StringIO()
                    writer = csv.writer(csv_buf)
                    writer.writerow(["ts", "type", "amount", "balance", "note"])
                    for r in rows:
                        writer.writerow([r["ts"], r["type"], r["amount"], r["balance"], r.get("note", "")])
                    st.download_button("Download transactions CSV", data=csv_buf.getvalue(), file_name=f"tx_{user['accountNo']}.csv")

        with right:
            st.metric("Balance", f"₹{user.get('balance', 0)}")
            st.write("Account created:")
            st.write(user.get("created_at"))

    else:
        with st.form("login_form"):
            acc = st.text_input("Account number")
            pin = st.text_input("PIN", type="password")
            login = st.form_submit_button("Login")
        if login:
            user = bank.authenticate(acc.strip(), pin)
            if not user:
                st.error("Invalid account number or PIN")
            else:
                st.session_state.user = user
                st.success(f"Welcome, {user['name']}")
                st.rerun()

if menu == "Admin: Accounts":
    st.header("Admin — Accounts")
    st.write("This view lists stored accounts. PINs are not shown. Admin password required.")
    admin_pass = st.text_input("Admin password", type="password")
    if admin_pass == "admin123":
        st.success("Admin unlocked")
        accounts = bank.data
        if not accounts:
            st.info("No accounts yet")
        else:
            view = [
                {
                    "accountNo": a.get("accountNo"),
                    "name": a.get("name"),
                    "age": a.get("age"),
                    "email": a.get("email"),
                    "balance": a.get("balance"),
                    "created_at": a.get("created_at"),
                    "tx_count": len(a.get("transactions", [])),
                }
                for a in accounts
            ]
            st.dataframe(view)
            as_csv = io.StringIO()
            cw = csv.writer(as_csv)
            cw.writerow(["accountNo", "name", "age", "email", "balance", "created_at", "tx_count"])
            for r in view:
                cw.writerow([r[k] for k in ["accountNo", "name", "age", "email", "balance", "created_at", "tx_count"]])
            st.download_button("Download accounts CSV", data=as_csv.getvalue(), file_name="accounts.csv")
    elif admin_pass:
        st.error("Wrong admin password")

st.caption("Note: This is a demo app for learning and shouldn't be used for real money or production without proper security.")
