// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract KYC {

    struct Client {
        address userID;
        string report_uri;
        bool used;
        uint end_date;
        string zkp_commitment;
        bytes32 zkp_salt;  // Store the salt used for the hash
    }
    
    // Stores userID => Client
    mapping (address => Client) public Clientdatabase;
    address[] public clientList;   // Create a list to loop through and get expiring KYC reports
    
    uint start_date = block.timestamp; // start date of KYC
    address public admin; // contract administrator
    
    constructor() {
        admin = msg.sender;
    }
    
    // Events
    event NewClient(address userID, string report_uri); 
    event ChangeClientInfo(address userID, string report_uri); 
    event FlagExpiringKYC(address client, uint clientend_date); 
    
    // Register KYC
    function registerKYC(address userID, string memory report_uri, string memory zkp_commitment) public returns(bool) { 
        require(!Clientdatabase[userID].used, "Account already Exists");
        
        // Salt to be used in the proof verification, derived from the sender and block data
        bytes32 salt = keccak256(abi.encodePacked(block.timestamp, msg.sender, userID));
        
        emit NewClient(userID, report_uri);
       
        Clientdatabase[userID] = Client(userID, report_uri, true, block.timestamp + 365 days, zkp_commitment, salt);
        appendClientInfo(userID);
       
       return Clientdatabase[userID].used;
    }

    // Update KYC
    function updateKYC(address userID, string memory newreport_uri) public returns(string memory) {

        require(Clientdatabase[userID], "Account does not Exist! Register First!")
        Clientdatabase[userID].report_uri = newreport_uri;
        emit ChangeClientInfo(userID, newreport_uri);
        return Clientdatabase[userID].report_uri;
    }

    // Check KYC validity
    function checkValidity(address userID) public view returns(string memory) {
        if (block.timestamp > Clientdatabase[userID].end_date) {
            return "KYC report has Expired!";
        }
        else {
            return "KYC report is Valid!";
        }
    } 

    // Add each new client to the client list
    function appendClientInfo(address client) private {
        clientList.push(client);
    }

    // Get total client count
    function getClientCount() public view returns(uint count) {
        return clientList.length;
    }

    // Iterate through client list to get expiring contracts
    function clientLoop() public {  
        require(msg.sender == admin, "You are not authorized to use this function");
        
        for (uint i = 0; i < clientList.length; i++) {
            if (Clientdatabase[clientList[i]].end_date < block.timestamp + 30 days && Clientdatabase[clientList[i]].end_date > block.timestamp + 1 days) {
                emit FlagExpiringKYC(clientList[i], Clientdatabase[clientList[i]].end_date);
            }
        }
    }

    // Hash function to replicate Python's _hash with salt
    function _hash(string memory x, bytes32 salt) private pure returns (bytes32) {
        return keccak256(abi.encodePacked(x, salt));
    }

    // Verify the user's age based on ZKP commitment
    function verifyAge(address userID) public view returns(string memory) {
        string memory zkpCommitment = Clientdatabase[userID].zkp_commitment;
        bytes32 salt = Clientdatabase[userID].zkp_salt;
        
        bytes32 v = _hash(zkpCommitment, salt);  // Commitment based on age threshold

        if (v == _hash("age_above_18", salt)) {
            return "Verified: User is 18 or older";
        } else if (v == _hash("age_below_18", salt)) {
            return "Verification failed: User is under 18";
        } else {
            return "Verification failed: No valid ZKP found";
        }
    }
}