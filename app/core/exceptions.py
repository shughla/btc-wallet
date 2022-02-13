class DuplicateUserApiKeyException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Try again. (You're lucky, Chance of this exception is 1 in 2^192)"
        )


class WrongWalletRequestException(Exception):
    def __init__(self, address: int) -> None:
        super().__init__(f"Unauthorized wallet access: {address}.")


class NotEnoughMoneyException(Exception):
    def __init__(self, address: int) -> None:
        super().__init__(f"Not enough money in wallet: {address}")


class WalletNotFoundException(Exception):
    def __init__(self, address: int) -> None:
        super().__init__(f"Wallet not found with address: {address}")


class MaximumWalletAmountReachedException(Exception):
    def __init__(self, max_amount: int) -> None:
        super().__init__(
            f"Maximum amount of wallets reached for this account: {max_amount}"
        )
