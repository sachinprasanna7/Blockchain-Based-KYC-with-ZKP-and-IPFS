// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract KYC {

    struct Client {
        address userID;
        string report_uri;
        bool used;
        uint end_date;
        string zkp_proof;
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


    // Characters: Letters + Digits
    string internal characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

    // Simple hash function to generate a 32-character pseudo-random string
    function simpleHash(uint256 age) public view returns (string memory) {
        string memory input = age >= 18 ? "age_above_18" : "age_below_18";
        
        bytes memory str = bytes(input);
        uint256 hash = 0;
        for (uint i = 0; i < str.length; i++) {
            hash = (hash * 31 + uint8(str[i])) % (10**32); // Use a multiplier and modulo to get a number
        }

        bytes memory result = new bytes(32);
        for (uint i = 0; i < 32; i++) {
            uint8 index = uint8(hash % 62); // There are 62 characters (26 + 26 + 10)
            result[i] = bytes(characters)[index];
            hash = hash / 62;  // Update hash to pick the next character
        }
        return string(result);
    }

    
    // Register KYC
    function registerKYC(address userID, string memory report_uri, string memory zkp_proof) public returns(bool) { 
        require(!Clientdatabase[userID].used, "Account already Exists");
        
        emit NewClient(userID, report_uri);
       
        Clientdatabase[userID] = Client(userID, report_uri, true, block.timestamp + 365 days, zkp_proof);
        appendClientInfo(userID);
       
       return Clientdatabase[userID].used;
    }

    // Update KYC
    function updateKYC(address userID, string memory newreport_uri) public returns(string memory) {
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


    // Verify the user's age based on ZKP commitment
    function verifyAge(address userID) public view returns (string memory) {
        // Retrieve the client's stored proof
        string memory zkpProof = Clientdatabase[userID].zkp_proof;
        
        // Compare the keccak256 hashes of the stored proof and expected proof for age >= 18
        if (keccak256(abi.encodePacked(zkpProof)) == keccak256(abi.encodePacked(simpleHash(18)))) {
            return "Verified: User is 18 or older";
        } else {
            return "Verification failed: User is under 18";
        }
    }
}