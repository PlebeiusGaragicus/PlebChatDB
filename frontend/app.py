import streamlit as st
import requests

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost:{DATABASE_API_PORT}"

# Helper function to handle increase user balance
def increase_user_balance(username, amount):
    response = requests.put(f"{DATABASE_API_URL}/users/balance/increase", json={"username": username, "amount": amount})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to increase balance: {response.json().get('detail', 'Unknown error')}")
        return None

st.title("Admin Dashboard")

# Function to fetch all users
def get_all_users():
    response = requests.get(f"{DATABASE_API_URL}/users/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch users.")
        return []

# Create a user
st.header("Create User")
username = st.text_input("Username")
balance = st.number_input("Initial Balance", min_value=0)
if st.button("Create User"):
    response = requests.post(f"{DATABASE_API_URL}/users/", json={"username": username, "balance": balance})
    if response.status_code == 200:
        st.success(f"User {username} created successfully!")
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# Fetch all users and their balances
st.header("All Users")
users = get_all_users()
if users:
    user_dict = {user["username"]: user["balance"] for user in users}
    user_list = list(user_dict.keys())
    st.write(user_dict)

# Get user balance using select box
st.header("Get User Balance")
if users:
    get_username = st.selectbox("Select User", user_list)
    if st.button("Get Balance"):
        response = requests.get(f"{DATABASE_API_URL}/balance/", json={"username": get_username})
        if response.status_code == 200:
            user_data = response.json()
            st.info(f"User: {user_data['username']}, Balance: {user_data['balance']}")
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# Deduct balance using select box
st.header("Deduct User Balance")
if users:
    deduct_username = st.selectbox("Select User to Deduct From", user_list)
    deduct_amount = st.number_input("Amount to Deduct", min_value=0)
    chat_id = st.text_input("Chat ID")
    if st.button("Deduct Balance"):
        response = requests.put(
            f"{DATABASE_API_URL}/tx/",
            json={"username": deduct_username, "chat_id": chat_id, "amount": -deduct_amount}
        )
        if response.status_code == 200:
            user_data = response.json()
            st.info(f"New Balance for {user_data['username']}: {user_data['balance']}")
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# Increase user balance using select box
st.header("Increase User Balance")
if users:
    increase_user = st.selectbox("Select User to Increase Balance", user_list)
    increase_amount = st.number_input("Amount to Increase", min_value=0)

    if st.button("Increase Balance"):
        result = increase_user_balance(increase_user, increase_amount)
        if result:
            st.info(f"New Balance for {result['username']}: {result['new_balance']}")

# View invoices using select box
st.header("View User Invoices")
if users:
    invoice_username = st.selectbox("Select User to View Invoices", user_list)
    if st.button("Get Invoices"):
        response = requests.post(f"{DATABASE_API_URL}/invoices/", json={"username": invoice_username})
        if response.status_code == 200:
            invoices = response.json()
            st.write(invoices)
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# View transactions using select box
st.header("View User Transactions")
if users:
    transact_username = st.selectbox("Select User to View Transactions", user_list)
    if st.button("Get Transactions"):
        response = requests.post(f"{DATABASE_API_URL}/usage/", json={"username": transact_username})
        try:
            response.raise_for_status()
            transactions = response.json()
            st.write(transactions)
        except requests.exceptions.HTTPError:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
        except ValueError:
            st.error("Failed to decode JSON response")

# Clean up invoices
st.header("Clean Up Invoices (TESTING ONLY)")
if users:
    cleanup_user = st.selectbox("Select User to Clean Up Invoices", user_list)
    if st.button("Clean Up Invoices"):
        response_pending = requests.post(
            f"{DATABASE_API_URL}/admin/cleanup/pending/",
            json={"username": cleanup_user}
        )
        response_archived = requests.post(
            f"{DATABASE_API_URL}/admin/cleanup/archived/",
            json={"username": cleanup_user}
        )
        if response_pending.status_code == 200 and response_archived.status_code == 200:
            st.success(f"Cleaned up pending and archived invoices for user {cleanup_user}!")
        else:
            st.error("Failed to clean up invoices.")
