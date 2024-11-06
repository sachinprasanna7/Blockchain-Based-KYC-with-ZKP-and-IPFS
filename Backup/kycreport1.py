import sys
from kyc import convertDataToJSON, pinJSONtoIPFS
from kyc import initContract, w3
from pprint import pprint
from zkp import ZKProof 
from datetime import datetime

kyccontract = initContract()
zkp = ZKProof()

def calculate_age(dob):
    birth_date = datetime.strptime(dob, "%d/%m/%Y")
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Create KYC report with encryption
def createkycReport():

    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    dob = input("Date of birth dd/mm/yyyy: ")
    user_name = input("User Name: ")
    occupation = input("Occupation: ")
    age = calculate_age(dob)
    print("Age is ", age)

    zkp_proof = zkp.generate_proof(age)
    print("ZKP Proof:", zkp_proof)
    
    # encryption_key = input("Enter a 16, 24, or 32-character encryption key: ")
    # while len(encryption_key) not in (16, 24, 32):
    #     print("Invalid key length. The key must be 16, 24, or 32 characters long.")
    #     encryption_key = input("Enter a valid encryption key: ")

    # Encrypt the KYC data

    json_data = convertDataToJSON(first_name, last_name, dob, user_name, occupation, age, zkp_proof)

    # can you verify the zkp proof

    print("json_data", json_data)

    # verification_result = zkp.verify()
    # print(verification_result)


    # encrypted_data = encrypt_data(json_data, encryption_key)

    # print("Encrypted Data:", encrypted_data)
    report_uri = pinJSONtoIPFS(json_data)

    return user_name, report_uri


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
        user_id, report_uri, age = createkycReport()
        receipt = kycreport(user_id, report_uri)
        pprint(receipt)
        print("Report IPFS Hash:", report_uri)

    elif sys.argv[1] == "update":
        user_id, report_uri, _ = createkycReport()
        receipt = kycupdate(user_id, report_uri)
        pprint(receipt)
        print("Report IPFS Hash:", report_uri)

    # elif sys.argv[1] == "verifyZKP":
    #     user_id = input("User ID: ")
    #     dob = input("Enter user's date of birth (dd/mm/yyyy): ")
    #     age = calculate_age(dob)
    #     receipt = verifyZKP(user_id, age)
    #     pprint(receipt)
    #     print("ZKP verified: User is 18 or older" if age >= 18 else "ZKP verification failed: User is under 18")

    if sys.argv[1] == "help":
        user_id, report_uri = createkycReport()
        print("Report IPFS Hash:", report_uri)
        print("User ID:", user_id)

main()