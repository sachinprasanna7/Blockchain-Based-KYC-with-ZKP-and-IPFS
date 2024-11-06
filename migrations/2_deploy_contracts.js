// migrations/2_deploy_contracts.js
const KYCContract = artifacts.require("KYC");

module.exports = function(deployer) {
  deployer.deploy(KYCContract);
};
