from flask import Flask, render_template, request, flash, redirect, url_for
from kyc import convertDataToJSON, pinJSONtoIPFS, initContract, w3
from datetime import datetime
from zkp import ZKProof
from pprint import pprint
from web3.exceptions import ContractLogicError
from flask import jsonify

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize KYC contract and ZK proof
kyccontract = initContract()
zkp = ZKProof()

# Helper function to calculate age
def calculate_age(dob):
    birth_date = datetime.strptime(dob, "%d/%m/%Y")
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Route for the landing page
@app.route("/landing", methods=["GET"])
def landing():
    return render_template("landing_page.html")

# Route for KYC Registration
@app.route("/register", methods=["POST"])
def kyc_register():
    # Collect data from form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    dob = request.form.get("dob")
    email = request.form.get("email")
    nationality = request.form.get("nationality")
    occupation = request.form.get("occupation")
    user_id = request.form.get("user_id")
    
    # Calculate age and generate ZKP proof
    age = calculate_age(dob)
    zkp_proof = zkp.generate_proof(age)

    # Convert data to JSON and pin to IPFS
    json_data = convertDataToJSON(first_name, last_name, dob, age, email, nationality, occupation, zkp_proof)
    report_uri = pinJSONtoIPFS(json_data)
    
    try:
        tx_hash = kyccontract.functions.registerKYC(user_id, report_uri, zkp_proof).transact({"from": user_id})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        flash("KYC Report Registered Successfully", "success")
        return render_template("kyc_result.html", receipt=receipt, report_uri=report_uri, user_id=user_id, zkp_proof=zkp_proof)

    except ContractLogicError as e:
        error_message = "Account already exists. Please update the KYC instead."
        return render_template("kyc_form.html", error_message=error_message)

# Route for KYC Update
@app.route("/update", methods=["POST"])
def kyc_update():
    # Collect data from form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    dob = request.form.get("dob")
    email = request.form.get("email")
    nationality = request.form.get("nationality")
    occupation = request.form.get("occupation")
    user_id = request.form.get("user_id")
    
    # Calculate age and generate ZKP proof
    age = calculate_age(dob)
    zkp_proof = zkp.generate_proof(age)

    # Convert data to JSON and pin to IPFS
    json_data = convertDataToJSON(first_name, last_name, dob, age, email, nationality, occupation, zkp_proof)
    report_uri = pinJSONtoIPFS(json_data)
    
    # Update KYC in the smart contract
    tx_hash = kyccontract.functions.updateKYC(user_id, report_uri).transact(
        {"from": user_id}
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Display the result
    flash("KYC Report Updated Successfully", "success")
    return render_template("kyc_updation_result.html", receipt=receipt, report_uri=report_uri, user_id=user_id, zkp_proof=zkp_proof)

# Route for the form
@app.route("/", methods=["GET"])
def form():
    return render_template("kyc_form.html")

# Route for Admin Login
@app.route("/admin_login", methods=["POST"])
def admin_login():
    password = request.form.get("password")
    role = request.form.get("role")

    # Check if the password is correct for the role
    if role == "admin" and password == "admin123":
        return redirect(url_for("admin_page"))
    elif role == "bank" and password == "bank123":
        return redirect(url_for("bank_page"))

    flash("Incorrect password. Please try again.", "danger")
    return redirect(url_for("form"))

# Route for the admin page
@app.route("/admin_page")
def admin_page():
    return render_template("admin_page.html")

# Route for the admin page with form data
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        
        if "check_validity" in request.form:
            validity_message = kyccontract.functions.checkValidity(user_id).call()
            return jsonify({"validity_message": validity_message})

        elif "get_client_count" in request.form:
            client_count = kyccontract.functions.getClientCount().call()
            return jsonify({"client_count": client_count})

        elif "get_client_info" in request.form:
            client_info = kyccontract.functions.Clientdatabase(user_id).call()
            return jsonify({
                "user_id": client_info[0],
                "report_uri": client_info[1],
                "used": client_info[2],
                "end_date": client_info[3],
                "zkp_proof": client_info[4]
            })

    return render_template("admin_page.html")

# Route for the bank page (optional, if needed)
@app.route("/bank_page")
def bank_page():
    return render_template("bank_page.html")

@app.route("/bank", methods=["GET", "POST"])
def bank():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        
        if "verify_age" in request.form:
            age_verification = kyccontract.functions.verifyAge(user_id).call()
            return jsonify({"age_verification": age_verification})

    return render_template("bank_page.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)