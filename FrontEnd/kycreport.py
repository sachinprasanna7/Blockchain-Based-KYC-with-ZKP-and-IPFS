import sys
from kyc import convertDataToJSON, pinJSONtoIPFS, initContract, w3, encrypt_data
from pprint import pprint

kyccontract = initContract()

# Create KYC report with encryption
def createkycReport():
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    dob = input("Date of birth mm/dd/yyyy: ")
    email = input("Email: ")
    nationality = input("Nationality: ")
    occupation = input("Occupation: ")
    user_id = input("User ID: ")
    image = input("Driv Lic image_uri: ")
    
    encryption_key = input("Enter encryption key: ")  # User's secret encryption key

    # Encrypt the KYC data
    json_data = convertDataToJSON(first_name, last_name, dob, email, nationality, occupation, image)
    encrypted_data = encrypt_data(json_data, encryption_key)
    
    report_uri = pinJSONtoIPFS(encrypted_data)

    return user_id, report_uri

def kycreport(user_id, report_uri):
    tx_hash = kyccontract.functions.registerKYC(user_id, report_uri).transact(
        {"from": user_id}
    )
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def kycupdate(user_id, report_uri):
    tx_hash = kyccontract.functions.updateKYC(user_id, report_uri).transact(
        {"from": user_id}
    )
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

# ZKP for age verification
def verifyZKP(user_id, is_over_18):
    tx_hash = kyccontract.functions.verifyZKP(user_id, is_over_18).transact(
        {"from": user_id}
    )
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def main():
    if sys.argv[1] == "report":
        user_id, report_uri = createkycReport()
        receipt = kycreport(user_id, report_uri)
        pprint(receipt)
        print("Report IPFS Hash:", report_uri)

    if sys.argv[1] == "update":
        user_id, report_uri = createkycReport()
        receipt = kycupdate(user_id, report_uri)
        pprint(receipt)
        print("Report IPFS Hash:", report_uri)

    if sys.argv[1] == "verifyZKP":
        user_id = input("User ID: ")
        is_over_18 = input("Is user over 18 (true/false)? ") == "true"
        receipt = verifyZKP(user_id, is_over_18)
        pprint(receipt)
        print("ZKP verified")

main()