import time
import json
import requests

from bolt11 import decode


def check_for_payment(invoice):
    """
    Check the payment status of an invoice.

    Parameters:
    - invoice: The invoice object containing the details.

    Returns:
    - True if the invoice is settled (paid).
    - False otherwise.
    """
    print(invoice)
    verify_url = invoice['verify']

    response = requests.get(verify_url)
    if response.status_code == 200:
        status = response.json().get('status')
        settled = response.json().get('settled', False)

        print(f"Status: {status}")
        print(f"Settled: {settled}")

        if settled:
            print("Invoice has been paid! 🎉")
            return True
        else:
            print("Invoice has not been settled yet.")
            return False
    else:
        print("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        print(response.status_code, response.text)
        return False
    

















def create_invoice(amount: int = 100, ln_address: str = "turkeybiscuit@getalby.com"):
    """
    Create a lightning invoice.
    
    Parameters:
    - amount: Amount in satoshis.
    - ln_address: The lightning network address to receive the payment.
    
    Returns:
    - Invoice details as a dictionary if successful.
    - Error message if the request fails.
    """
    url = "https://api.getalby.com/lnurl/generate-invoice"
    params = {
        "ln": ln_address,
        "amount": amount * 1000,  # in millisats
        "comment": f"Purchased {amount * 30} PlebChat tokens 🗣️🤖💬"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Successfully created the invoice
        invoice_details = response.json()
        invoice_details['amount'] = amount  # Adding the amount to the invoice details
        print("Invoice created!")
        print(json.dumps(invoice_details, indent=4))  # Pretty print the invoice details
        return invoice_details
    else:
        # Failed to create the invoice
        error_message = f"Failed to create invoice: {response.status_code} {response.text}"
        print(error_message)
        return {"error": error_message}
















def load_invoice_from_file(file_path='invoice.json'):
    """
    Load the stored invoice from a JSON file.

    Parameters:
    - file_path: The path to the JSON file containing the stored invoice.

    Returns:
    - The invoice details as a dictionary if the file is successfully read and parsed.
    - None if the file does not exist or an error occurs during reading/parsing.
    """
    try:
        with open(file_path, 'r') as file:
            invoice = json.load(file)
        return invoice
    except FileNotFoundError:
        print("Invoice file not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
        return None
    





def return_stored_invoice():
    invoice = load_invoice_from_file()

    if invoice is None:
        return None

    pr = invoice['invoice']['pr']
    invoice_date = decode(pr).date
    print(f"Invoice created: {invoice_date}")

    amount = decode(pr).amount_msat / 1000
    tags = decode(pr).tags

    # Check for expiry tag
    if not tags.has("expire_time"):  # Simplified tag reference
        print("ERROR: Invoice is missing an expiry tag")
        expiry = 3600  # Default to 1 hour
    else:
        expiry = tags.get("expire_time").data
        print(f"Expiry: {expiry} seconds")

    # Current time in seconds since epoch
    now = int(time.time())
    print(f"Now: {now}")
    # Invoice expiry time in seconds since epoch
    invoice_expiry = invoice_date + expiry
    # Time remaining in seconds
    time_remaining = invoice_expiry - now
    print(f"Time remaining: {time_remaining} seconds")

    if time_remaining < 60:  # Less than 60 seconds remaining
        print("ERROR: Invoice has expired")
        return None

    print(f"Amount: {amount} sats")
    return invoice







# def check_for_payment(file_path='invoice.json'):
#     """
#     Check the payment status of an invoice.

#     Parameters:
#     - file_path: The path to the JSON file containing the stored invoice.

#     Returns:
#     - True if the invoice is settled (paid).
#     - False otherwise.
#     """
#     invoice = return_stored_invoice(file_path)

#     if invoice is None:
#         print("No valid invoice found.")
#         return False

#     verify_url = invoice['invoice']['verify']

#     response = requests.get(verify_url)
#     if response.status_code == 200:
#         status = response.json().get('status')
#         settled = response.json().get('settled', False)

#         print(f"Status: {status}")
#         print(f"Settled: {settled}")

#         if settled:
#             print("Invoice has been paid! 🎉")
#             return True
#         else:
#             print("Invoice has not been settled yet.")
#             return False
#     else:
#         print("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
#         print(response.status_code, response.text)
#         return False










if __name__ == "__main__":
    pass
    # invoice = create_invoice(100)
    # print(invoice)
    
    # print(load_invoice_from_file())

    return_stored_invoice()
