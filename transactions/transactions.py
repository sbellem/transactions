import pybitcointools

from pycoin.key.BIP32Node import BIP32Node
from pycoin.encoding import EncodingError

from services.daemonservice import BitcoinDaemonService, RegtestDaemonService
from services.blockrservice import BitcoinBlockrService


SERVICES = ['daemon', 'blockr', 'regtest']


class Transactions(object):
    """
    Transactions: Bitcoin for Humans

    All amounts are in satoshi
    """

    # Transaction fee per 1k bytes
    _min_tx_fee = 10000
    # dust
    _dust = 600

    def __init__(self, service='blockr', testnet=False, username='', password='', host='', port=''):
        """
        Args:
            service (str): currently supports _blockr_ for blockr.io and and _daemon_ for bitcoin daemon. Defaults to _blockr_
            testnet (bool): use True if you want to use tesnet. Defaults to False
            username (str): username to connect to the bitcoin daemon
            password (str): password to connect to the bitcoin daemon
            hosti (str): host of the bitcoin daemon
            port (str): port of the bitcoin daemon

        """
        self.testnet = testnet

        if service not in SERVICES:
            raise Exception("Service '{}' not supported".format(service))
        if service == 'daemon':
            self._service = BitcoinDaemonService(username, password, host, port, testnet)
        elif service == 'blockr':
            self._service = BitcoinBlockrService(testnet)
        elif service == 'regtest':
            self.testnet = True
            self._service = RegtestDaemonService(username, password, host, port, testnet)

        self._min_tx_fee = self._service._min_transaction_fee
        self._dust = self._service._min_dust

    def push(self, tx):
        """
        Args:
            tx: hex of signed transaction
        Returns:
            pushed transaction

        """
        self._service.push_tx(tx)
        return pybitcointools.txhash(tx)

    def get(self, hash, account="*", max_transactions=100, min_confirmations=6, raw=False):
        """
        Args:
            hash: can be a bitcoin address or a transaction id. If it's a
                bitcoin address it will return a list of transactions up to
                ``max_transactions`` a list of unspents with confirmed
                transactions greater or equal to ``min_confirmantions``
            account (Optional[str]): used when using the bitcoind. bitcoind
                does not provide an easy way to retrieve transactions for a
                single address. By using account we can retrieve transactions
                for addresses in a  specific account
        Returns:
            transaction

        """
        if len(hash) < 64:
            txs = self._service.list_transactions(hash, account=account, max_transactions=max_transactions)
            unspents = self._service.list_unspents(hash, min_confirmations=min_confirmations)
            return {'transactions': txs, 'unspents': unspents}
        else:
            return self._service.get_transaction(hash, raw=raw)

    def import_address(self, address, account="", rescan=False):
        if self._service.name.startswith('BitcoinDaemonService') or \
                self._service.name.startswith('RegtestDaemonService'):
            self._service.import_address(address, account, rescan=rescan)

    def simple_transaction(self, from_address, to, op_return=None, min_confirmations=6):
        """
        Args:
            from_address (str): bitcoin address originating the transaction
            to: tuple of ``(to_address, amount)`` or list of tuples ``[(to_addr1, amount1), (to_addr2, amount2)]``. Amounts are in *satoshi*
            op_return (str): ability to set custom ``op_return``
            min_confirmations (int): minimal number of required confirmations

        Returns:
            transaction

        """
        to = [to] if not isinstance(to, list) else to
        amount = sum([amount for addr, amount in to])
        n_outputs = len(to) + 1     # change
        if op_return:
            n_outputs += 1

        # select inputs
        inputs, change = self._select_inputs(from_address, amount, n_outputs, min_confirmations=min_confirmations)
        outputs = [{'address': to_address, 'value': amount} for to_address, amount in to]
        outputs += [{'address': from_address, 'value': change}]

        #add op_return
        if op_return:
            outputs += [{'script': self._op_return_hex(op_return), 'value': 0}]
        tx = self.build_transaction(inputs, outputs)
        return tx

    def build_transaction(self, inputs, outputs):
        """
        Thin wrapper around ``pybitcointools.mktx(inputs, outputs)``

        Args:
            inputs (dict): inputs in the form of
                ``{'output': 'txid:vout', 'value': amount in satoshi}``
            outputs (dict): outputs in the form of
                ``{'address': to_address, 'value': amount in satoshi}``
        Returns:
            transaction
        """
        # prepare inputs and outputs for pybitcointools
        inputs = [{'output': '{}:{}'.format(input['txid'], input['vout']),
                   'value': input['amount']} for input in inputs]
        tx = pybitcointools.mktx(inputs, outputs)
        return tx

    def sign_transaction(self, tx, master_password, path=''):
        """
        Args:
            tx: hex transaction to sign
            master_password: master password for BIP32 wallets. Can be either a
                master_secret or a wif
            path (Optional[str]): optional path to the leaf address of the
                BIP32 wallet. This allows us to retrieve private key for the
                leaf address if one was used to construct the transaction.
        Returns:
            signed transaction

        .. note:: Only BIP32 hierarchical deterministic wallets are currently
            supported.

        """
        netcode = 'XTN' if self.testnet else 'BTC'

        # check if its a wif
        try:
            BIP32Node.from_text(master_password)
            return pybitcointools.signall(tx, master_password)
        except EncodingError:
            # if its not get the wif from the master secret
            return pybitcointools.signall(tx, BIP32Node.from_master_secret(master_password, netcode=netcode).subkey_for_path(path).wif())

    def _select_inputs(self, address, amount, n_outputs=2, min_confirmations=6):
        # selects the inputs to fulfill the amount
        # returns a list of inputs and the change
        unspents = self.get(address, min_confirmations=min_confirmations)['unspents']
        if len(unspents) == 0:
            raise Exception("No spendable outputs found")

        unspents = sorted(unspents, key=lambda d: d['amount'])
        balance = 0
        inputs = []
        fee = self._service._min_transaction_fee
        try:
            # get coins to fulfill the amount
            while balance < amount + fee:
                unspent = unspents.pop()
                balance += unspent['amount']
                inputs.append(unspent)
                # update estimated fee
                fee = self.estimate_fee(len(inputs), n_outputs)
        except IndexError:
            raise Exception("Not enough balance in the wallet")

        change = balance - amount - fee
        change = change if change > self._dust else 0

        return inputs, change

    def _op_return_hex(self, op_return):
        return "6a%x%s" % (len(op_return), op_return.encode('hex'))

    def estimate_fee(self, n_inputs, n_outputs):
        # estimates transaction fee based on number of inputs and outputs
        estimated_size = 10 + 148 * n_inputs + 34 * n_outputs
        return (estimated_size / 1000 + 1) * self._min_tx_fee

    def decode(self, tx):
        """
        Decodes the given transaction.

        Args:
            tx: hex of transaction
        Returns:
            decoded transaction

        .. note:: Only supported for blockr.io at the moment.

        """
        if self._service != 'blockr':
            raise NotImplementedError('Currently only supported for "blockr.io"')
        return self._service.decode(tx)
