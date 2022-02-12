from dataclasses import dataclass, field

from app.core.exceptions import WrongWalletRequestException
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.repositories import IWalletRepository


@dataclass
class InMemoryWalletRepository(IWalletRepository):
    wallets: dict[int, list[Wallet]] = field(default_factory=dict)
    last_wallet: int = 0

    def get_wallets(self, user: User) -> list[Wallet]:
        return self.wallets.get(user.id, [])

    def add_wallet(self, wallet: Wallet) -> Wallet:
        wallet.address = self.last_wallet
        if self.wallets.get(wallet.user_id) is None:
            self.wallets[wallet.user_id] = [wallet]
        else:
            self.wallets[wallet.user_id].append(wallet)
        self.last_wallet += 1
        return wallet

    def get_wallet(self, address: int) -> Wallet:
        for wallets in self.wallets.values():
            # user wallets
            for wallet in wallets:
                if wallet.address == address:
                    return wallet
        raise WrongWalletRequestException()

    def update_wallet(self, wallet: Wallet) -> None:
        for wallet in self.wallets[wallet.user_id]:
            if wallet.address == wallet.address:
                wallet.balance = wallet.balance
                return
