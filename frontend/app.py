import streamlit as st
import requests
from pymongo import MongoClient

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost"


# ####################################################
# # NOTE: TESTING ONLY
# # MongoDB connection details
# MONGO_URL = "mongodb://mongo:27017"
# DATABASE_NAME = "user_balance"
# USER_COLLECTION = "users"

# # Connect to MongoDB
# client = MongoClient(MONGO_URL)
# db = client[DATABASE_NAME]
# user_collection = db[USER_COLLECTION]

# # Function to increase user balance
# def increase_user_balance(username, amount):
#     user = user_collection.find_one({"username": username})
#     if user:
#         new_balance = user["balance"] + amount
#         user_collection.update_one({"username": username}, {"$set": {"balance": new_balance}})
#         return new_balance
#     else:
#         st.error("User not found")
#         return None
# ####################################################

# Function to increase user balance
def increase_user_balance(username, amount):
    response = requests.put(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/users/{username}/balance/increase", json={"amount": amount})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to increase balance: {response.json().get('detail', 'Unknown error')}")
        return None





st.title("Admin Dashboard")

# Function to fetch all users
def get_all_users():
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/users/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch users.")
        return []

# Create a user
st.header("Create User")
username = st.text_input("Username")
balance = st.number_input("Initial Balance", min_value=0.0, format="%.2f")
if st.button("Create User"):
    response = requests.post(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/users/", json={"username": username, "balance": balance})
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
get_username = st.selectbox("Select User", user_list) if users else ""
if get_username and st.button("Get Balance"):
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/users/{get_username}/balance/")
    if response.status_code == 200:
        user_data = response.json()
        st.info(f"User: {user_data['username']}, Balance: {user_data['balance']}")
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")



# Deduct balance using select box
st.header("Deduct User Balance")
deduct_username = st.selectbox("Select User to Deduct From", user_list) if users else ""
deduct_amount = st.number_input("Amount to Deduct", min_value=0.0, format="%.2f")
chat_id = st.text_input("Chat ID")
if deduct_username and st.button("Deduct Balance"):
    response = requests.put(
        f"{DATABASE_API_URL}:{DATABASE_API_PORT}/users/{deduct_username}/balance/deduct",
        json={"chat_id": chat_id, "amount": -deduct_amount}
    )
    if response.status_code == 200:
        user_data = response.json()
        st.info(f"New Balance for {user_data['username']}: {user_data['balance']}")
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# ####################################################
# # NOTE: TESTING ONLY
# # Increase user balance using select box
# st.header("Increase User Balance")
# increase_user = st.selectbox("Select User to Increase Balance", user_list) if users else ""
# increase_amount = st.number_input("Amount to Increase", min_value=0.0, format="%.2f")
# if increase_user and st.button("Increase Balance") and increase_amount > 0:
#     new_balance = increase_user_balance(increase_user, increase_amount)
#     if new_balance is not None:
#         st.info(f"New Balance for {increase_user}: {new_balance}")
# Select user and increase balance
st.header("Increase User Balance")
increase_user = st.selectbox("Select User to Increase Balance", user_list) if users else ""
increase_amount = st.number_input("Amount to Increase", min_value=0.0, format="%.2f")

if increase_user and st.button("Increase Balance") and increase_amount > 0:
    result = increase_user_balance(increase_user, increase_amount)
    if result:
        st.info(f"New Balance for {result['username']}: {result['new_balance']}")
# ####################################################


# View transactions using select box
st.header("View User Transactions")
transact_username = st.selectbox("Select User to View Transactions", user_list) if users else ""
if transact_username and st.button("Get Transactions"):
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/users/{transact_username}/transactions/")
    print(response)
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
