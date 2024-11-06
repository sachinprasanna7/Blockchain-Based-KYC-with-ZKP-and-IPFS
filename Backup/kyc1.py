import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from web3.auto import w3
# from Crypto.Cipher import AES  # For encryption
# import base64

load_dotenv()

headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

print(headers)

''' Encryption with AES
# def encrypt_data(data, key):
#     cipher = AES.new(key.encode('utf-8'), AES.MODE_EAX)
#     nonce = cipher.nonce
#     ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
#     return base64.b64encode(nonce + ciphertext).decode('utf-8')

# # Decrypt data if needed (only the user knows the key)
# def decrypt_data(encrypted_data, key):
#     decoded_data = base64.b64decode(encrypted_data)
#     nonce = decoded_data[:16]
#     ciphertext = decoded_data[16:]
#     cipher = AES.new(key.encode('utf-8'), AES.MODE_EAX, nonce=nonce)
#     plaintext = cipher.decrypt(ciphertext).decode('utf-8')
#     return plaintext
'''

# Convert data to JSON
def convertDataToJSON(first_name, last_name, dob, user_name, occupation, age, zkp_proof):
    data = {
        "pinataOptions": {"cidVersion": 1},
        "pinataContent": {
            "name": "KYC Report",
            "first_name": first_name,
            "last_name":  last_name,
            "date_of_birth": dob,
            "occupation": occupation,
            "age": age,
            "zkp_proof": zkp_proof
        },  
    }

    return json.dumps(data)

# Pin JSON to IPFS
def pinJSONtoIPFS(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS", data=json, headers=headers
    )
    ipfs_hash = r.json()["IpfsHash"]
    return f"ipfs://{ipfs_hash}"


# Initialize contract
def initContract():
    with open(Path("kyccontract.json")) as json_file:
        abi = json.load(json_file)
    return w3.eth.contract(address=os.getenv("KYC_ADDRESS"), abi=abi)

