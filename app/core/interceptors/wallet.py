from dataclasses import dataclass
from typing import Optional, Protocol

from app.core.const import Config
from app.core.exceptions import WrongWalletRequestException
from app.core.models.user import User
from app.core.models.wallet import DefaultWallet, Wallet
from app.core.repositories import IWalletRepository


class IWalletInterceptor(Protocol):
    def create_wallet(self, user: User) -> Optional[Wallet]:
        pass

    def get_wallet(self, user: User, address: int) -> Wallet:
        pass


@dataclass
class WalletInterceptor(IWalletInterceptor):
    wallet_repository: IWalletRepository
    max_wallets: int = Config.MAX_WALLETS_TO_USER

    def create_wallet(self, user: User) -> Optional[Wallet]:
        if len(self.wallet_repository.get_wallets(user)) == self.max_wallets:
            return None
        return self.wallet_repository.add_wallet(DefaultWallet(user_id=user.id))

    def get_wallet(self, user: User, address: int) -> Wallet:
        wallet = self.wallet_repository.get_wallet(address)
        if wallet.user_id != user.id:
            raise WrongWalletRequestException()
        return wallet
