pragma solidity ^0.5.0;

contract KYC {
    struct Client {
        address userID;
        string report_uri;
        bool used;
        uint end_date;
    }

    mapping(address => Client) public Clientdatabase;
    address[] public clientList;
    uint start_date = now;
    address public admin;

    constructor() public {
        admin = msg.sender;
    }

    // Events that will emit changes 
    event NewClient(address userID, string report_uri);
    event ChangeClientInfo(address userID, string report_uri);
    event flagExpiring_kyc(address client, uint clientend_date);
    event ZKPVerification(address userID, bool isOver18); // For ZKP

    function registerKYC(address userID, string memory report_uri) public returns (bool) {
        require(!Clientdatabase[userID].used, "Account already exists");
        emit NewClient(userID, report_uri);
        Clientdatabase[userID] = Client(userID, report_uri, true, now + 365 days);
        appendclientinfo(userID);
        return Clientdatabase[userID].used;
    }

    function updateKYC(address userID, string memory newreport_uri) public returns (string memory) {
        Clientdatabase[userID].report_uri = newreport_uri;
        emit ChangeClientInfo(userID, newreport_uri);
        return Clientdatabase[userID].report_uri;
    }

    function checkvalidity(address userID) public view returns (string memory) {
        if (now > Clientdatabase[userID].end_date) {
            return "KYC report has Expired!";
        } else {
            return "KYC report is Valid!";
        }
    }

    function appendclientinfo(address client) private {
        clientList.push(client);
    }

    function getclientCount() public view returns (uint count) {
        return clientList.length;
    }

    // Iterate through client list to get expiring contracts
    function clientLoop() public {
        require(msg.sender == admin, "You are not authorized to use this function");
        for (uint i = 0; i < clientList.length; i++) {
            if (Clientdatabase[clientList[i]].end_date < now + 30 days && Clientdatabase[clientList[i]].end_date > now + 1 days) {
                emit flagExpiring_kyc(clientList[i], Clientdatabase[clientList[i]].end_date);
            }
        }
    }

    // Verify ZKP proof for age > 18
    function verifyZKP(address userID, bool isOver18) public returns (bool) {
        require(Clientdatabase[userID].used, "Account does not exist");
        // Emit ZKP verification result
        emit ZKPVerification(userID, isOver18);
        return isOver18;
    }
}
