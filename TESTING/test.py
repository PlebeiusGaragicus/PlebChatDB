import time
import requests

TOKENS_PER_SAT = 10

def create_invoice(user_uuid, sats: int = 100):
    """
    Generates a new invoice via LNURL API and returns the invoice data.
    """
    ln_address = "turkeybiscuit@getalby.com"
    url = "https://api.getalby.com/lnurl/generate-invoice"
    params = {
        "ln": ln_address,
        "amount": sats * 1000,  # in millisats
        "comment": f"Purchased {sats * TOKENS_PER_SAT} tokens"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        invoice_data = response.json()['invoice']
        invoice_data['user'] = user_uuid
        invoice_data['amount'] = sats  # Store the amount in satoshis
        invoice_data['created_at'] = time.time()
        return invoice_data
    else:
        raise Exception(f"Failed to create invoice: {response.status_code} {response.text}")


if __name__ == "__main__":
    r = create_invoice("test_user", 100)
    print(r)
