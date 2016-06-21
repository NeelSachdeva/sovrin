import pprint

from charm.core.math.integer import randomPrime

from anoncreds.protocol.utils import encodeAttrs
from plenum.common.txn import DATA, ORIGIN
from plenum.common.txn import TXN_TYPE
from plenum.common.util import getlogger
from plenum.test.helper import genHa
from sovrin.common.txn import CRED_DEF
from sovrin.test.helper import genTestClient, submitAndCheck

logger = getlogger()


def cryptoNumber(bitLength: int=100):
    return randomPrime(bitLength)


credDef = dict(type="JC1",
               ha={'ip': "10.10.10.10",
                   'port': 7897},
               keys={
                   "master_secret": cryptoNumber(),
                   "n": cryptoNumber(),
                   "S": cryptoNumber(),
                   "Z": cryptoNumber(),
                   "attributes": {
                       "first_name": cryptoNumber(),
                       "last_name": cryptoNumber(),
                       "birth_date": cryptoNumber(),
                       "expire_date": cryptoNumber(),
                       "undergrad": cryptoNumber(),
                       "postgrad": cryptoNumber(),
                   }
               })

attributes = {
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1970-01-01",
    "expire_date": "2300-01-01",
    "undergrad": "True",
    "postgrad": "False"
}

attrNames = list(attributes.keys())


def testAnonCredFlow(looper, tdir, nodeSet, issuerSigner, proverSigner,
                     verifierSigner, addedIPV):
    # TODO Some interactions happen in fixtures and helper methods.
    # TODO Add logging statements to them as well.
    # TODO Must talk about BYU and Tyler in the log statements, not in
    # TODO  abstract terms.
    # TODO Add sleep() or read_input() to stop and highlight specific things.

    # 3 Sovrin clients acting as Issuer, Signer and Verifier
    issuer = genTestClient(nodeSet, tmpdir=tdir, peerHA=genHa)
    prover = genTestClient(nodeSet, tmpdir=tdir, peerHA=genHa)
    verifier = genTestClient(nodeSet, tmpdir=tdir, peerHA=genHa)

    # Adding signers
    issuer.signers[issuerSigner.identifier] = issuerSigner
    logger.info("Key pair for Issuer created \n"
                "Public key is {} \n"
                "Private key is stored on disk\n".format(issuerSigner.verstr))
    prover.signers[proverSigner.identifier] = proverSigner
    logger.info("Key pair for Prover created \n"
                "Public key is {} \n"
                "Private key is stored on disk\n".format(proverSigner.verstr))
    verifier.signers[verifierSigner.identifier] = verifierSigner
    logger.info("Key pair for Verifier created \n"
                "Public key is {} \n"
                "Private key is stored on disk\n".format(
                    verifierSigner.verstr))

    # Issuer's attribute repository
    attrRepo = {proverSigner.identifier: attributes}
    issuer.attrRepo = attrRepo
    name1 = "Qualifications"
    version1 = "1.0"
    issuerId = 'issuer1'
    proverId = 'prover1'
    verifierId = 'verifier1'
    interactionId = 'LOGIN-1'

    # Issuer publishes credential definition to Sovrin ledger
    issuer.credentialDefinitions = {(name1, version1): credDef}
    logger.info("Issuer: Creating version {} of credential definition"
                " for {}".format(version1, name1))
    print("Credential definition: ")
    pprint.pprint(credDef)  # Pretty-printing the big object.
    op = {ORIGIN: issuerSigner.verstr, TXN_TYPE: CRED_DEF, DATA: credDef}
    logger.info("Issuer: Writing credential definition to "
                "Sovrin Ledger...")
    submitAndCheck(looper, issuer, op, identifier=issuerSigner.identifier)

    # Prover requests Issuer for credential (out of band)
    logger.info("Prover: Requested credential from Issuer")
    # Issuer issues a credential for prover
    logger.info("Issuer: Creating credential for "
                "{}".format(proverSigner.verstr))
    cred = issuer.createCredential(proverId, name1, version1)
    logger.info("Prover: Received credential from "
                "{}".format(issuerSigner.verstr))

    # Prover intends to prove certain attributes to a Verifier
    proofId = 'proof1'

    # Verifier issues a nonce
    logger.info("Prover: Requesting Nonce from verifier…")
    logger.info("Verifier: Nonce received from prover"
                " {}".format(proverId))
    nonce = verifier.generateNonce(interactionId)
    logger.info("Verifier: Nonce sent.")
    logger.info("Prover: Nonce received")
    prover.proofs[proofId]['nonce'] = nonce

    # Prover discovers Issuer's credential definition
    prover.credentialDefinitions = {(issuerId, attrNames): credDef}
    revealedAttrs = ["undergrad"]
    logger.info("Prover: Preparing proof for attributes: "
                "{}".format(revealedAttrs))
    logger.info("Prover: Proof prepared.")
    proof = prover.prepare_proof(cred, encodeAttrs(attrNames),
                                 revealedAttrs, nonce)
    logger.info("Prover: Proof submitted")
    logger.info("Verifier: Proof received.")
    logger.info("Verifier: Looking up Credential Definition"
                " on Sovrin Ledger...")
    prover.proofs[proofId] = proof

    # Verifier fetches the credential definition from ledger
    verifier.credentialDefinitions = {
        (issuerId, name1, version1): credDef
    }

    # Verifier verifies proof
    logger.info("Verifier: Verifying proof...")
    verified = verifier.verify_proof(proof, nonce,
                                     attrNames, revealedAttrs)
    logger.info("Verifier: Proof verified.")
    assert verified
    logger.info("Prover: Proof accepted.")