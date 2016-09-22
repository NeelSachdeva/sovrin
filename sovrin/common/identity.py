from plenum.common.txn import TARGET_NYM, TXN_TYPE, NYM, ROLE, STEWARD
from plenum.common.types import Identifier
from sovrin.common.generates_request import GeneratesRequest
from sovrin.common.txn import SPONSOR
from sovrin.common.types import Request


class Identity(GeneratesRequest):
    def __init__(self,
                 identifier: Identifier,
                 sponsor: Identifier=None,
                 verkey=None,
                 role=None,
                 last_synced=None,
                 seqNo=None):

        self.identifier = identifier
        self.sponsor = sponsor

        # None indicates the identifier is a cryptonym
        self.verkey = verkey

        # None indicates the identifier is a cryptonym
        if role and role not in (SPONSOR, STEWARD):
            raise AttributeError("Invalid role {}".format(role))
        self.role = role

        # timestamp for when the ledger was last checked for key replacement or
        # revocation
        self.last_synced = last_synced

        # seqence number of the latest key management transaction for this
        # identifier
        self.seqNo = seqNo

    def _op(self):
        op = {
            TARGET_NYM: self.identifier,
            TXN_TYPE: NYM
        }
        if self.role:
            op[ROLE] = self.role
        return op

    def ledgerRequest(self):
        if not self.seqNo:
            assert self.identifier is not None
            return Request(identifier=self.sponsor, operation=self._op())
