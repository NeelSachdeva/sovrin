import pytest
from prompt_toolkit.contrib.regular_languages.compiler import compile
from plenum.cli.helper import getUtilGrams, getNodeGrams, getClientGrams, getAllGrams
from plenum.test.cli.test_command_reg_ex import checkIfMatched
from sovrin.cli.helper import getNewClientGrams


@pytest.fixture("module")
def grammar():
    grams = getClientGrams() + getNewClientGrams()
    return compile("".join(grams))


def test_send_attrib_reg_ex(grammar):
    checkIfMatched(grammar, 'send ATTRIB dest=LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU= raw={"legal org": "BRIGHAM YOUNG UNIVERSITY, PROVO, UT", "email":"mail@byu.edu"}')


def test_init_attr_repo_reg_ex(grammar):
    checkIfMatched(grammar, "initialize mock attribute repo")


def test_add_attr_reg_ex(grammar):
    checkIfMatched(grammar, "add attribute first_name=Tyler,last_name=Ruff,birth_date=12/17/1991,undergrad=True,postgrad=True,expiry_date=12/31/2101 for Tyler")


def test_req_cred_reg_ex(grammar):
    checkIfMatched(grammar,
                   "request credential Degree version 1.0 from o7NzafnAlkhNaEM5njaH+I7Y19BEbEORmFB13p87zhM= for Tyler")


def test_gen_cred_reg_ex(grammar):
    checkIfMatched(grammar, "generate credential for Tyler for Degree version 1.0 with uvalue")


def test_store_cred_reg_ex(grammar):
    checkIfMatched(grammar, "store credential A=avalue, e=evalue, vprime=vprimevalue for proof proofid as tyler-degree")


def test_list_cred_reg_ex(grammar):
    checkIfMatched(grammar, "list CRED")


def test_gen_verif_nonce_reg_ex(grammar):
    checkIfMatched(grammar, "generate verification nonce")


def test_prep_proof_reg_ex(grammar):
    checkIfMatched(grammar, "prepare proof of degree using nonce mynonce for undergrad")


def test_verify_proof_reg_ex(grammar):
    checkIfMatched(grammar, "verify status is undergrad in proof degreeproof")
