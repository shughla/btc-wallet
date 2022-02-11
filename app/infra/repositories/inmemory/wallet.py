from dataclasses import dataclass, field

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
