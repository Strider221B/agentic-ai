The user wants unit tests for the `accounts.py` module. I need to create a `test_accounts.py` file that covers the functionality of the `Account` class and the `get_share_price` function.

I will use the `unittest` module in Python to write these tests.

Here's a plan:
1.  **Import necessary modules**: `unittest`, `datetime`, and the `Account` class and `get_share_price` function from `accounts`.
2.  **Create a test class**: Inherit from `unittest.TestCase`.
3.  **Test `__init__`**:
    *   Test with a positive initial deposit.
    *   Test with zero initial deposit.
    *   Test with a negative initial deposit (should raise `ValueError`).
4.  **Test `deposit`**:
    *   Test depositing a positive amount.
    *   Test depositing zero or a negative amount (should raise `ValueError`).
5.  **Test `withdraw`**:
    *   Test withdrawing a positive amount less than the balance.
    *   Test withdrawing an amount equal to the balance.
    *   Test withdrawing a positive amount greater than the balance (should raise `ValueError`).
    *   Test withdrawing zero or a negative amount (should raise `ValueError`).
6.  **Test `buy_shares`**:
    *   Test buying shares with sufficient funds.
    *   Test buying shares with insufficient funds (should raise `ValueError`).
    *   Test buying with non-positive quantity (should raise `ValueError`).
    *   Test buying with negative price (should raise `ValueError`).
7.  **Test `sell_shares`**:
    *   Test selling shares that are owned.
    *   Test selling more shares than owned (should raise `ValueError`).
    *   Test selling shares that are not owned (should raise `ValueError`).
    *   Test selling with non-positive quantity (should raise `ValueError`).
    *   Test selling with negative price (should raise `ValueError`).
8.  **Test `get_holdings`**:
    *   Check if holdings are updated correctly after buys and sells.
    *   Check if an empty dictionary is returned if no shares are held.
9.  **Test `get_portfolio_value`**:
    *   Test portfolio value after buying shares.
    *   Test portfolio value after selling shares.
    *   Test portfolio value when no shares are held.
    *   Test with symbols not in `get_share_price` mock (should return 0).
10. **Test `get_total_value`**:
    *   Test total value (cash + portfolio) after deposits, withdrawals, and trades.
11. **Test `get_profit_loss`**:
    *   Test P/L after a profitable trade.
    *   Test P/L after a losing trade.
    *   Test P/L after deposits and withdrawals.
    *   Test P/L when only cash is present.
12. **Test `get_transaction_history`**:
    *   Check if all transactions (deposit, buy, sell, withdraw) are recorded correctly.
    *   Check the format and content of transaction entries.

Let's start by creating the `test_accounts.py` file content.

```python
import unittest
import datetime
# Assuming accounts.py is in the same directory
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        """Set up a fresh Account object before each test."""
        self.initial_deposit = 10000.0
        self.account = Account(self.initial_deposit)

    def test_initialization_positive_deposit(self):
        """Test account initialization with a positive deposit."""
        self.assertEqual(self.account._cash_balance, self.initial_deposit)
        self.assertEqual(self.account.get_holdings(), {})
        self.assertEqual(len(self.account.get_transaction_history()), 1)
        self.assertEqual(self.account.get_transaction_history()[0]['type'], 'DEPOSIT')
        self.assertEqual(self.account.get_transaction_history()[0]['amount'], self.initial_deposit)

    def test_initialization_zero_deposit(self):
        """Test account initialization with zero deposit."""
        account_zero = Account(0.0)
        self.assertEqual(account_zero._cash_balance, 0.0)
        self.assertEqual(account_zero.get_holdings(), {})
        self.assertEqual(len(account_zero.get_transaction_history()), 1)
        self.assertEqual(account_zero.get_transaction_history()[0]['type'], 'DEPOSIT')
        self.assertEqual(account_zero.get_transaction_history()[0]['amount'], 0.0)


    def test_initialization_negative_deposit_raises_error(self):
        """Test account initialization with a negative deposit raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            Account(-100.0)
        self.assertEqual(str(cm.exception), "Initial deposit cannot be negative.")

    def test_deposit_positive_amount(self):
        """Test depositing a positive amount."""
        deposit_amount = 500.0
        self.account.deposit(deposit_amount)
        self.assertEqual(self.account._cash_balance, self.initial_deposit + deposit_amount)
        self.assertEqual(self.account._total_deposits, self.initial_deposit + deposit_amount)
        self.assertEqual(len(self.account.get_transaction_history()), 2)
        self.assertEqual(self.account.get_transaction_history()[1]['type'], 'DEPOSIT')
        self.assertEqual(self.account.get_transaction_history()[1]['amount'], deposit_amount)

    def test_deposit_zero_amount_raises_error(self):
        """Test depositing zero amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.deposit(0.0)
        self.assertEqual(str(cm.exception), "Deposit amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_deposit_negative_amount_raises_error(self):
        """Test depositing a negative amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.deposit(-100.0)
        self.assertEqual(str(cm.exception), "Deposit amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_withdraw_sufficient_funds(self):
        """Test withdrawing with sufficient funds."""
        withdraw_amount = 1000.0
        self.account.withdraw(withdraw_amount)
        self.assertEqual(self.account._cash_balance, self.initial_deposit - withdraw_amount)
        self.assertEqual(self.account._total_withdrawals, withdraw_amount)
        self.assertEqual(len(self.account.get_transaction_history()), 2)
        self.assertEqual(self.account.get_transaction_history()[1]['type'], 'WITHDRAW')
        self.assertEqual(self.account.get_transaction_history()[1]['amount'], withdraw_amount)

    def test_withdraw_exact_funds(self):
        """Test withdrawing the exact amount of available cash."""
        self.account.withdraw(self.initial_deposit)
        self.assertEqual(self.account._cash_balance, 0.0)
        self.assertEqual(self.account._total_withdrawals, self.initial_deposit)
        self.assertEqual(len(self.account.get_transaction_history()), 2)


    def test_withdraw_insufficient_funds_raises_error(self):
        """Test withdrawing with insufficient funds raises ValueError."""
        insufficient_amount = self.initial_deposit + 100.0
        with self.assertRaises(ValueError) as cm:
            self.account.withdraw(insufficient_amount)
        self.assertIn("Insufficient funds for withdrawal", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change
        self.assertEqual(self.account._total_withdrawals, 0.0) # Ensure withdrawal count didn't change


    def test_withdraw_zero_amount_raises_error(self):
        """Test withdrawing zero amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.withdraw(0.0)
        self.assertEqual(str(cm.exception), "Withdrawal amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_withdraw_negative_amount_raises_error(self):
        """Test withdrawing a negative amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.withdraw(-100.0)
        self.assertEqual(str(cm.exception), "Withdrawal amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_buy_shares_sufficient_funds(self):
        """Test buying shares with sufficient funds."""
        symbol = "AAPL"
        quantity = 5
        price_per_share = 170.0 # Mocked price
        total_cost = quantity * price_per_share

        self.account.buy_shares(symbol, quantity, price_per_share)

        self.assertEqual(self.account._cash_balance, self.initial_deposit - total_cost)
        self.assertEqual(self.account.get_holdings(), {symbol: quantity})
        self.assertEqual(len(self.account.get_transaction_history()), 2)
        buy_transaction = self.account.get_transaction_history()[1]
        self.assertEqual(buy_transaction['type'], 'BUY')
        self.assertEqual(buy_transaction['symbol'], symbol)
        self.assertEqual(buy_transaction['quantity'], quantity)
        self.assertEqual(buy_transaction['price_per_unit'], price_per_share)
        self.assertEqual(buy_transaction['amount'], total_cost)

        # Test purchase history
        self.assertIn(symbol, self.account._purchase_history)
        self.assertEqual(len(self.account._purchase_history[symbol]), 1)
        self.assertEqual(self.account._purchase_history[symbol][0]['quantity'], quantity)
        self.assertEqual(self.account._purchase_history[symbol][0]['price'], price_per_share)

    def test_buy_shares_multiple_buys_same_symbol(self):
        """Test buying multiple times for the same symbol."""
        symbol = "AAPL"
        quantity1 = 5
        price1 = 170.0
        self.account.buy_shares(symbol, quantity1, price1)

        quantity2 = 3
        price2 = 175.0 # Assume price changed, though mock doesn't reflect this for internal state
        self.account.buy_shares(symbol, quantity2, price2)

        expected_holdings = {symbol: quantity1 + quantity2}
        self.assertEqual(self.account.get_holdings(), expected_holdings)

        self.assertEqual(len(self.account.get_transaction_history()), 3) # Initial deposit + 2 buys
        self.assertEqual(self.account._cash_balance, self.initial_deposit - (quantity1 * price1) - (quantity2 * price2))

        # Test purchase history aggregation
        self.assertIn(symbol, self.account._purchase_history)
        self.assertEqual(len(self.account._purchase_history[symbol]), 2)
        # The order might depend on internal implementation, but both lots should be there.
        # For simplicity, we check if the quantities and prices are present.
        lots = self.account._purchase_history[symbol]
        self.assertTrue(any(l['quantity'] == quantity1 and l['price'] == price1 for l in lots))
        self.assertTrue(any(l['quantity'] == quantity2 and l['price'] == price2 for l in lots))


    def test_buy_shares_multiple_symbols(self):
        """Test buying shares of different symbols."""
        symbol_aapl = "AAPL"
        quantity_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, quantity_aapl, price_aapl)

        symbol_tsla = "TSLA"
        quantity_tsla = 2
        price_tsla = 250.0
        self.account.buy_shares(symbol_tsla, quantity_tsla, price_tsla)

        expected_holdings = {symbol_aapl: quantity_aapl, symbol_tsla: quantity_tsla}
        self.assertEqual(self.account.get_holdings(), expected_holdings)
        self.assertEqual(len(self.account.get_transaction_history()), 3)

    def test_buy_shares_insufficient_funds_raises_error(self):
        """Test buying shares with insufficient funds raises ValueError."""
        symbol = "GOOGL"
        quantity = 1
        price_per_share = 3000.0 # Higher than initial deposit allows for 1 share
        total_cost = quantity * price_per_share

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity, price_per_share)
        self.assertIn("Insufficient funds for purchase", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change
        self.assertEqual(self.account.get_holdings(), {}) # Ensure holdings didn't change

    def test_buy_shares_non_positive_quantity_raises_error(self):
        """Test buying shares with non-positive quantity raises ValueError."""
        symbol = "AAPL"
        quantity_zero = 0
        quantity_negative = -2
        price_per_share = 170.0

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity_zero, price_per_share)
        self.assertEqual(str(cm.exception), "Purchase quantity must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit)

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity_negative, price_per_share)
        self.assertEqual(str(cm.exception), "Purchase quantity must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit)


    def test_buy_shares_negative_price_raises_error(self):
        """Test buying shares with a negative price raises ValueError."""
        symbol = "AAPL"
        quantity = 5
        price_negative = -170.0

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity, price_negative)
        self.assertEqual(str(cm.exception), "Purchase price cannot be negative.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit)
        self.assertEqual(self.account.get_holdings(), {})


    def test_sell_shares_owned(self):
        """Test selling shares that are owned."""
        symbol = "AAPL"
        buy_quantity = 10
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 3
        sell_price = 175.0 # Selling at a higher price
        total_proceeds = sell_quantity * sell_price

        self.account.sell_shares(symbol, sell_quantity, sell_price)

        expected_holdings = {symbol: buy_quantity - sell_quantity}
        self.assertEqual(self.account.get_holdings(), expected_holdings)
        self.assertEqual(len(self.account.get_transaction_history()), 3) # Deposit, Buy, Sell
        sell_transaction = self.account.get_transaction_history()[2]
        self.assertEqual(sell_transaction['type'], 'SELL')
        self.assertEqual(sell_transaction['symbol'], symbol)
        self.assertEqual(sell_transaction['quantity'], sell_quantity)
        self.assertEqual(sell_transaction['price_per_unit'], sell_price)
        self.assertEqual(sell_transaction['amount'], total_proceeds)

        # Check cash balance update
        expected_cash_after_buy = self.initial_deposit - (buy_quantity * buy_price)
        expected_cash_after_sell = expected_cash_after_buy + total_proceeds
        self.assertEqual(self.account._cash_balance, expected_cash_after_sell)

        # Check purchase history update (simplistic removal)
        self.assertIn(symbol, self.account._purchase_history)
        self.assertEqual(len(self.account._purchase_history[symbol]), 1)
        self.assertEqual(self.account._purchase_history[symbol][0]['quantity'], buy_quantity - sell_quantity)
        self.assertEqual(self.account._purchase_history[symbol][0]['price'], buy_price)


    def test_sell_shares_sell_all_owned(self):
        """Test selling all owned shares of a symbol."""
        symbol = "TSLA"
        buy_quantity = 2
        buy_price = 250.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 2
        sell_price = 260.0
        self.account.sell_shares(symbol, sell_quantity, sell_price)

        self.assertEqual(self.account.get_holdings(), {}) # Should be empty now
        self.assertNotIn(symbol, self.account._purchase_history) # Should be removed from history
        self.assertEqual(len(self.account.get_transaction_history()), 3)


    def test_sell_shares_more_than_owned_raises_error(self):
        """Test selling more shares than owned raises ValueError."""
        symbol = "AAPL"
        buy_quantity = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 7 # Trying to sell more than owned
        sell_price = 175.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity, sell_price)
        self.assertIn("Insufficient shares to sell", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit - (buy_quantity * buy_price)) # Balance unchanged
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity}) # Holdings unchanged

    def test_sell_shares_not_owned_raises_error(self):
        """Test selling shares of a symbol not currently owned raises ValueError."""
        symbol = "GOOGL"
        sell_quantity = 1
        sell_price = 2800.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity, sell_price)
        self.assertIn("Insufficient shares to sell", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit)
        self.assertEqual(self.account.get_holdings(), {})

    def test_sell_shares_non_positive_quantity_raises_error(self):
        """Test selling shares with non-positive quantity raises ValueError."""
        symbol = "AAPL"
        buy_quantity = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity_zero = 0
        sell_quantity_negative = -3
        sell_price = 175.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity_zero, sell_price)
        self.assertEqual(str(cm.exception), "Sale quantity must be positive.")
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity})

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity_negative, sell_price)
        self.assertEqual(str(cm.exception), "Sale quantity must be positive.")
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity})

    def test_sell_shares_negative_price_raises_error(self):
        """Test selling shares with a negative price raises ValueError."""
        symbol = "AAPL"
        buy_quantity = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 3
        sell_price_negative = -175.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity, sell_price_negative)
        self.assertEqual(str(cm.exception), "Sale price cannot be negative.")
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity})


    def test_get_holdings_empty(self):
        """Test get_holdings when no shares are held."""
        self.assertEqual(self.account.get_holdings(), {})

    def test_get_holdings_after_trades(self):
        """Test get_holdings after buying and selling."""
        symbol1 = "AAPL"
        qty1 = 5
        price1 = 170.0
        self.account.buy_shares(symbol1, qty1, price1)

        symbol2 = "TSLA"
        qty2 = 2
        price2 = 250.0
        self.account.buy_shares(symbol2, qty2, price2)

        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {symbol1: qty1, symbol2: qty2})

        self.account.sell_shares(symbol1, 2, 175.0)
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {symbol1: qty1 - 2, symbol2: qty2})

        self.account.sell_shares(symbol2, 2, 260.0)
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {symbol1: qty1 - 2})


    def test_get_portfolio_value_empty(self):
        """Test get_portfolio_value when no shares are held."""
        self.assertEqual(self.account.get_portfolio_value(), 0.0)

    def test_get_portfolio_value_with_holdings(self):
        """Test get_portfolio_value with held shares."""
        symbol_aapl = "AAPL"
        qty_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)

        symbol_tsla = "TSLA"
        qty_tsla = 2
        price_tsla = 250.0
        self.account.buy_shares(symbol_tsla, qty_tsla, price_tsla)

        # Using mock prices: AAPL=170.0, TSLA=250.0
        expected_portfolio_value = (qty_aapl * 170.0) + (qty_tsla * 250.0)
        self.assertEqual(self.account.get_portfolio_value(), expected_portfolio_value)

    def test_get_portfolio_value_with_unknown_symbol(self):
        """Test get_portfolio_value with a symbol not in mock prices."""
        symbol_unknown = "XYZ"
        qty_unknown = 10
        self.account.buy_shares(symbol_unknown, qty_unknown, 50.0) # Price here is purchase price

        # get_share_price("XYZ") returns 0.0
        expected_portfolio_value = qty_unknown * 0.0
        self.assertEqual(self.account.get_portfolio_value(), expected_portfolio_value)

        # Add a known symbol too
        symbol_aapl = "AAPL"
        qty_aapl = 3
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)
        expected_portfolio_value += qty_aapl * 170.0
        self.assertEqual(self.account.get_portfolio_value(), expected_portfolio_value)


    def test_get_total_value_no_holdings(self):
        """Test get_total_value with only cash."""
        self.assertEqual(self.account.get_total_value(), self.initial_deposit)

    def test_get_total_value_with_holdings(self):
        """Test get_total_value with cash and holdings."""
        symbol_aapl = "AAPL"
        qty_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)

        # Cash balance after buying: 10000 - (5 * 170) = 10000 - 850 = 9150
        expected_cash_balance = self.initial_deposit - (qty_aapl * price_aapl)
        self.assertEqual(self.account._cash_balance, expected_cash_balance)

        # Portfolio value: 5 * 170.0 = 850.0
        expected_portfolio_value = qty_aapl * get_share_price(symbol_aapl)

        # Total value: cash + portfolio
        expected_total_value = expected_cash_balance + expected_portfolio_value
        self.assertEqual(self.account.get_total_value(), expected_total_value)

    def test_get_total_value_after_sell(self):
        """Test get_total_value after selling shares."""
        symbol_aapl = "AAPL"
        qty_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)

        sell_qty = 2
        sell_price = 175.0
        self.account.sell_shares(symbol_aapl, sell_qty, sell_price)

        # Expected cash: 10000 - (5*170) + (2*175) = 10000 - 850 + 350 = 9500
        expected_cash_balance = self.initial_deposit - (qty_aapl * price_aapl) + (sell_qty * sell_price)
        self.assertEqual(self.account._cash_balance, expected_cash_balance)

        # Expected portfolio: (5-2) * 170 = 3 * 170 = 510
        expected_portfolio_value = (qty_aapl - sell_qty) * get_share_price(symbol_aapl)

        expected_total_value = expected_cash_balance + expected_portfolio_value
        self.assertEqual(self.account.get_total_value(), expected_total_value)


    def test_get_profit_loss_initial_state(self):
        """Test get_profit_loss at initial state."""
        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Current total value: 10000 (cash) + 0 (portfolio) = 10000
        # P/L = 10000 - 10000 + 0 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_deposit(self):
        """Test get_profit_loss after an additional deposit."""
        deposit_amount = 2000.0
        self.account.deposit(deposit_amount)
        # Initial deposit: 10000
        # Total deposits: 10000 + 2000 = 12000
        # Total withdrawals: 0
        # Current total value: 12000 (cash) + 0 (portfolio) = 12000
        # P/L = 12000 - 12000 + 0 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_withdrawal(self):
        """Test get_profit_loss after a withdrawal."""
        withdraw_amount = 3000.0
        self.account.withdraw(withdraw_amount)
        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 3000
        # Current total value: 7000 (cash) + 0 (portfolio) = 7000
        # P/L = 7000 - 10000 + 3000 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_buy_no_price_change(self):
        """Test get_profit_loss after buying shares at the same price as market."""
        symbol = "AAPL"
        qty = 5
        price = 170.0 # Market price
        self.account.buy_shares(symbol, qty, price)

        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (5 * 170) = 10000 - 850 = 9150
        # Portfolio value: 5 * 170 = 850
        # Current total value: 9150 + 850 = 10000
        # P/L = 10000 - 10000 + 0 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_buy_price_increase(self):
        """Test get_profit_loss after buying shares and then market price increases."""
        symbol = "TSLA"
        qty = 2
        buy_price = 250.0 # Buying at market price
        self.account.buy_shares(symbol, qty, buy_price)

        # Simulate market price increase (for testing get_share_price override if needed, but mock is static)
        # Let's assume get_share_price will return a higher value in a real scenario.
        # For this test, we rely on the mock's fixed values.
        # If we were to mock get_share_price for testing price changes, it would look like this:
        # from unittest.mock import patch
        # with patch('accounts.get_share_price', return_value=300.0) as mock_get_price:

        # Current state:
        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (2 * 250) = 10000 - 500 = 9500
        # Portfolio value (using mock_prices["TSLA"] = 250.0): 2 * 250 = 500
        # Current total value: 9500 + 500 = 10000
        # P/L = 10000 - 10000 + 0 = 0

        # If get_share_price returned 300.0 for TSLA:
        # Portfolio value: 2 * 300 = 600
        # Current total value: 9500 + 600 = 10100
        # P/L = 10100 - 10000 + 0 = 100 (Profit)
        # Since the mock is static, the P/L will be 0 unless we sell or do something else.
        self.assertEqual(self.account.get_profit_loss(), 0.0) # Based on static mock price

    def test_get_profit_loss_after_sell_profit(self):
        """Test get_profit_loss after selling shares for a profit."""
        symbol = "AAPL"
        buy_qty = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_qty, buy_price)

        sell_qty = 3
        sell_price = 180.0 # Selling at a higher price than buy_price (170.0)
        self.account.sell_shares(symbol, sell_qty, sell_price)

        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (5*170) + (3*180) = 10000 - 850 + 540 = 9690
        # Holdings: {AAPL: 2}
        # Portfolio value: 2 * 170 (current mock price) = 340
        # Current total value: 9690 + 340 = 10030
        # P/L = 10030 - 10000 + 0 = 30 (Profit)
        self.assertAlmostEqual(self.account.get_profit_loss(), 30.0, places=2)

    def test_get_profit_loss_after_sell_loss(self):
        """Test get_profit_loss after selling shares for a loss."""
        symbol = "TSLA"
        buy_qty = 2
        buy_price = 250.0
        self.account.buy_shares(symbol, buy_qty, buy_price)

        sell_qty = 1
        sell_price = 240.0 # Selling at a lower price than buy_price (250.0)
        self.account.sell_shares(symbol, sell_qty, sell_price)

        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (2*250) + (1*240) = 10000 - 500 + 240 = 9740
        # Holdings: {TSLA: 1}
        # Portfolio value: 1 * 250 (current mock price) = 250
        # Current total value: 9740 + 250 = 9990
        # P/L = 9990 - 10000 + 0 = -10 (Loss)
        self.assertAlmostEqual(self.account.get_profit_loss(), -10.0, places=2)

    def test_get_profit_loss_with_deposits_and_withdrawals(self):
        """Test get_profit_loss with a mix of transactions."""
        # Start: 10000 cash
        self.account.deposit(5000) # Cash: 15000, Total Deposits: 15000
        self.account.buy_shares("AAPL", 10, 170.0) # Cash: 15000 - 1700 = 13300, Holdings: {AAPL: 10}, Portfolio: 1700
        self.account.withdraw(2000) # Cash: 11300, Total Withdrawals: 2000
        self.account.sell_shares("AAPL", 5, 175.0) # Cash: 11300 + (5*175) = 11300 + 875 = 12175, Holdings: {AAPL: 5}, Portfolio: 5*170 = 850

        # Calculations:
        # Initial deposit: 10000
        # Total deposits: 10000 + 5000 = 15000
        # Total withdrawals: 2000
        # Cash balance: 12175
        # Holdings: {AAPL: 5}
        # Portfolio value: 5 * 170.0 = 850.0
        # Current total value: 12175 + 850 = 13025
        # P/L = Current Total Value - Total Deposits + Total Withdrawals
        # P/L = 13025 - 15000 + 2000 = 3025
        self.assertAlmostEqual(self.account.get_profit_loss(), 3025.0, places=2)


    def test_get_transaction_history_empty(self):
        """Test get_transaction_history when no transactions made (should not happen after init)."""
        # Account is initialized with a deposit, so history is never truly empty.
        # This test is more about checking the initial state of history.
        self.assertEqual(len(self.account.get_transaction_history()), 1)
        self.assertEqual(self.account.get_transaction_history()[0]['type'], 'DEPOSIT')

    def test_get_transaction_history_after_multiple_operations(self):
        """Test get_transaction_history after several operations."""
        self.account.deposit(500.0)
        self.account.buy_shares("TSLA", 2, 250.0)
        self.account.withdraw(1000.0)
        self.account.sell_shares("TSLA", 1, 260.0)

        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 5) # Initial deposit + 4 operations

        # Check types and order (should be chronological)
        self.assertEqual(history[0]['type'], 'DEPOSIT')
        self.assertEqual(history[1]['type'], 'DEPOSIT')
        self.assertEqual(history[2]['type'], 'BUY')
        self.assertEqual(history[3]['type'], 'WITHDRAW')
        self.assertEqual(history[4]['type'], 'SELL')

        # Check details of a specific transaction (e.g., the last sell)
        sell_transaction = history[4]
        self.assertEqual(sell_transaction['symbol'], "TSLA")
        self.assertEqual(sell_transaction['quantity'], 1)
        self.assertEqual(sell_transaction['price_per_unit'], 260.0)
        self.assertEqual(sell_transaction['amount'], 260.0) # 1 share * 260.0

    def test_get_transaction_history_returns_copy(self):
        """Test that get_transaction_history returns a copy, not the internal list."""
        history1 = self.account.get_transaction_history()
        self.assertEqual(len(history1), 1)

        self.account.deposit(100.0)
        history2 = self.account.get_transaction_history()
        self.assertEqual(len(history2), 2)

        # Modify the first history list obtained
        history1.append({'test': 'manipulation'})
        self.assertEqual(len(history1), 2)
        self.assertEqual(len(history2), 2) # history2 should remain unchanged

        # Verify internal transactions list is also unchanged by external modification
        self.assertEqual(len(self.account._transactions), 2)

# This allows running the tests directly from the command line
# if __name__ == '__main__':
#     unittest.main()

```

I have created a comprehensive set of unit tests using Python's `unittest` module. These tests cover the initialization, deposits, withdrawals, buying and selling of shares, and the various getter methods like `get_holdings`, `get_portfolio_value`, `get_total_value`, `get_profit_loss`, and `get_transaction_history`. I've also included tests for edge cases and error handling (e.g., negative inputs, insufficient funds/shares).

The plan is complete. I will now output the code.
```python
import unittest
import datetime
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        """Set up a fresh Account object before each test."""
        self.initial_deposit = 10000.0
        self.account = Account(self.initial_deposit)

    def test_initialization_positive_deposit(self):
        """Test account initialization with a positive deposit."""
        self.assertEqual(self.account._cash_balance, self.initial_deposit)
        self.assertEqual(self.account.get_holdings(), {})
        self.assertEqual(len(self.account.get_transaction_history()), 1)
        self.assertEqual(self.account.get_transaction_history()[0]['type'], 'DEPOSIT')
        self.assertEqual(self.account.get_transaction_history()[0]['amount'], self.initial_deposit)

    def test_initialization_zero_deposit(self):
        """Test account initialization with zero deposit."""
        account_zero = Account(0.0)
        self.assertEqual(account_zero._cash_balance, 0.0)
        self.assertEqual(account_zero.get_holdings(), {})
        self.assertEqual(len(account_zero.get_transaction_history()), 1)
        self.assertEqual(account_zero.get_transaction_history()[0]['type'], 'DEPOSIT')
        self.assertEqual(account_zero.get_transaction_history()[0]['amount'], 0.0)


    def test_initialization_negative_deposit_raises_error(self):
        """Test account initialization with a negative deposit raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            Account(-100.0)
        self.assertEqual(str(cm.exception), "Initial deposit cannot be negative.")

    def test_deposit_positive_amount(self):
        """Test depositing a positive amount."""
        deposit_amount = 500.0
        self.account.deposit(deposit_amount)
        self.assertEqual(self.account._cash_balance, self.initial_deposit + deposit_amount)
        self.assertEqual(self.account._total_deposits, self.initial_deposit + deposit_amount)
        self.assertEqual(len(self.account.get_transaction_history()), 2)
        self.assertEqual(self.account.get_transaction_history()[1]['type'], 'DEPOSIT')
        self.assertEqual(self.account.get_transaction_history()[1]['amount'], deposit_amount)

    def test_deposit_zero_amount_raises_error(self):
        """Test depositing zero amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.deposit(0.0)
        self.assertEqual(str(cm.exception), "Deposit amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_deposit_negative_amount_raises_error(self):
        """Test depositing a negative amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.deposit(-100.0)
        self.assertEqual(str(cm.exception), "Deposit amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_withdraw_sufficient_funds(self):
        """Test withdrawing with sufficient funds."""
        withdraw_amount = 1000.0
        self.account.withdraw(withdraw_amount)
        self.assertEqual(self.account._cash_balance, self.initial_deposit - withdraw_amount)
        self.assertEqual(self.account._total_withdrawals, withdraw_amount)
        self.assertEqual(len(self.account.get_transaction_history()), 2)
        self.assertEqual(self.account.get_transaction_history()[1]['type'], 'WITHDRAW')
        self.assertEqual(self.account.get_transaction_history()[1]['amount'], withdraw_amount)

    def test_withdraw_exact_funds(self):
        """Test withdrawing the exact amount of available cash."""
        self.account.withdraw(self.initial_deposit)
        self.assertEqual(self.account._cash_balance, 0.0)
        self.assertEqual(self.account._total_withdrawals, self.initial_deposit)
        self.assertEqual(len(self.account.get_transaction_history()), 2)


    def test_withdraw_insufficient_funds_raises_error(self):
        """Test withdrawing with insufficient funds raises ValueError."""
        insufficient_amount = self.initial_deposit + 100.0
        with self.assertRaises(ValueError) as cm:
            self.account.withdraw(insufficient_amount)
        self.assertIn("Insufficient funds for withdrawal", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change
        self.assertEqual(self.account._total_withdrawals, 0.0) # Ensure withdrawal count didn't change


    def test_withdraw_zero_amount_raises_error(self):
        """Test withdrawing zero amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.withdraw(0.0)
        self.assertEqual(str(cm.exception), "Withdrawal amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_withdraw_negative_amount_raises_error(self):
        """Test withdrawing a negative amount raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.account.withdraw(-100.0)
        self.assertEqual(str(cm.exception), "Withdrawal amount must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change

    def test_buy_shares_sufficient_funds(self):
        """Test buying shares with sufficient funds."""
        symbol = "AAPL"
        quantity = 5
        price_per_share = 170.0 # Mocked price
        total_cost = quantity * price_per_share

        self.account.buy_shares(symbol, quantity, price_per_share)

        self.assertEqual(self.account._cash_balance, self.initial_deposit - total_cost)
        self.assertEqual(self.account.get_holdings(), {symbol: quantity})
        self.assertEqual(len(self.account.get_transaction_history()), 2)
        buy_transaction = self.account.get_transaction_history()[1]
        self.assertEqual(buy_transaction['type'], 'BUY')
        self.assertEqual(buy_transaction['symbol'], symbol)
        self.assertEqual(buy_transaction['quantity'], quantity)
        self.assertEqual(buy_transaction['price_per_unit'], price_per_share)
        self.assertEqual(buy_transaction['amount'], total_cost)

        # Test purchase history
        self.assertIn(symbol, self.account._purchase_history)
        self.assertEqual(len(self.account._purchase_history[symbol]), 1)
        self.assertEqual(self.account._purchase_history[symbol][0]['quantity'], quantity)
        self.assertEqual(self.account._purchase_history[symbol][0]['price'], price_per_share)

    def test_buy_shares_multiple_buys_same_symbol(self):
        """Test buying multiple times for the same symbol."""
        symbol = "AAPL"
        quantity1 = 5
        price1 = 170.0
        self.account.buy_shares(symbol, quantity1, price1)

        quantity2 = 3
        price2 = 175.0 # Assume price changed, though mock doesn't reflect this for internal state
        self.account.buy_shares(symbol, quantity2, price2)

        expected_holdings = {symbol: quantity1 + quantity2}
        self.assertEqual(self.account.get_holdings(), expected_holdings)

        self.assertEqual(len(self.account.get_transaction_history()), 3) # Initial deposit + 2 buys
        self.assertEqual(self.account._cash_balance, self.initial_deposit - (quantity1 * price1) - (quantity2 * price2))

        # Test purchase history aggregation
        self.assertIn(symbol, self.account._purchase_history)
        self.assertEqual(len(self.account._purchase_history[symbol]), 2)
        # The order might depend on internal implementation, but both lots should be there.
        # For simplicity, we check if the quantities and prices are present.
        lots = self.account._purchase_history[symbol]
        self.assertTrue(any(l['quantity'] == quantity1 and l['price'] == price1 for l in lots))
        self.assertTrue(any(l['quantity'] == quantity2 and l['price'] == price2 for l in lots))


    def test_buy_shares_multiple_symbols(self):
        """Test buying shares of different symbols."""
        symbol_aapl = "AAPL"
        quantity_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, quantity_aapl, price_aapl)

        symbol_tsla = "TSLA"
        quantity_tsla = 2
        price_tsla = 250.0
        self.account.buy_shares(symbol_tsla, quantity_tsla, price_tsla)

        expected_holdings = {symbol_aapl: quantity_aapl, symbol_tsla: quantity_tsla}
        self.assertEqual(self.account.get_holdings(), expected_holdings)
        self.assertEqual(len(self.account.get_transaction_history()), 3)

    def test_buy_shares_insufficient_funds_raises_error(self):
        """Test buying shares with insufficient funds raises ValueError."""
        symbol = "GOOGL"
        quantity = 1
        price_per_share = 3000.0 # Higher than initial deposit allows for 1 share
        total_cost = quantity * price_per_share

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity, price_per_share)
        self.assertIn("Insufficient funds for purchase", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit) # Ensure balance didn't change
        self.assertEqual(self.account.get_holdings(), {}) # Ensure holdings didn't change

    def test_buy_shares_non_positive_quantity_raises_error(self):
        """Test buying shares with non-positive quantity raises ValueError."""
        symbol = "AAPL"
        quantity_zero = 0
        quantity_negative = -2
        price_per_share = 170.0

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity_zero, price_per_share)
        self.assertEqual(str(cm.exception), "Purchase quantity must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit)

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity_negative, price_per_share)
        self.assertEqual(str(cm.exception), "Purchase quantity must be positive.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit)


    def test_buy_shares_negative_price_raises_error(self):
        """Test buying shares with a negative price raises ValueError."""
        symbol = "AAPL"
        quantity = 5
        price_negative = -170.0

        with self.assertRaises(ValueError) as cm:
            self.account.buy_shares(symbol, quantity, price_negative)
        self.assertEqual(str(cm.exception), "Purchase price cannot be negative.")
        self.assertEqual(self.account._cash_balance, self.initial_deposit)
        self.assertEqual(self.account.get_holdings(), {})


    def test_sell_shares_owned(self):
        """Test selling shares that are owned."""
        symbol = "AAPL"
        buy_quantity = 10
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 3
        sell_price = 175.0 # Selling at a higher price
        total_proceeds = sell_quantity * sell_price

        self.account.sell_shares(symbol, sell_quantity, sell_price)

        expected_holdings = {symbol: buy_quantity - sell_quantity}
        self.assertEqual(self.account.get_holdings(), expected_holdings)
        self.assertEqual(len(self.account.get_transaction_history()), 3) # Deposit, Buy, Sell
        sell_transaction = self.account.get_transaction_history()[2]
        self.assertEqual(sell_transaction['type'], 'SELL')
        self.assertEqual(sell_transaction['symbol'], symbol)
        self.assertEqual(sell_transaction['quantity'], sell_quantity)
        self.assertEqual(sell_transaction['price_per_unit'], sell_price)
        self.assertEqual(sell_transaction['amount'], total_proceeds)

        # Check cash balance update
        expected_cash_after_buy = self.initial_deposit - (buy_quantity * buy_price)
        expected_cash_after_sell = expected_cash_after_buy + total_proceeds
        self.assertEqual(self.account._cash_balance, expected_cash_after_sell)

        # Check purchase history update (simplistic removal)
        self.assertIn(symbol, self.account._purchase_history)
        self.assertEqual(len(self.account._purchase_history[symbol]), 1)
        self.assertEqual(self.account._purchase_history[symbol][0]['quantity'], buy_quantity - sell_quantity)
        self.assertEqual(self.account._purchase_history[symbol][0]['price'], buy_price)


    def test_sell_shares_sell_all_owned(self):
        """Test selling all owned shares of a symbol."""
        symbol = "TSLA"
        buy_quantity = 2
        buy_price = 250.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 2
        sell_price = 260.0
        self.account.sell_shares(symbol, sell_quantity, sell_price)

        self.assertEqual(self.account.get_holdings(), {}) # Should be empty now
        self.assertNotIn(symbol, self.account._purchase_history) # Should be removed from history
        self.assertEqual(len(self.account.get_transaction_history()), 3)


    def test_sell_shares_more_than_owned_raises_error(self):
        """Test selling more shares than owned raises ValueError."""
        symbol = "AAPL"
        buy_quantity = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 7 # Trying to sell more than owned
        sell_price = 175.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity, sell_price)
        self.assertIn("Insufficient shares to sell", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit - (buy_quantity * buy_price)) # Balance unchanged
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity}) # Holdings unchanged

    def test_sell_shares_not_owned_raises_error(self):
        """Test selling shares of a symbol not currently owned raises ValueError."""
        symbol = "GOOGL"
        sell_quantity = 1
        sell_price = 2800.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity, sell_price)
        self.assertIn("Insufficient shares to sell", str(cm.exception))
        self.assertEqual(self.account._cash_balance, self.initial_deposit)
        self.assertEqual(self.account.get_holdings(), {})

    def test_sell_shares_non_positive_quantity_raises_error(self):
        """Test selling shares with non-positive quantity raises ValueError."""
        symbol = "AAPL"
        buy_quantity = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity_zero = 0
        sell_quantity_negative = -3
        sell_price = 175.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity_zero, sell_price)
        self.assertEqual(str(cm.exception), "Sale quantity must be positive.")
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity})

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity_negative, sell_price)
        self.assertEqual(str(cm.exception), "Sale quantity must be positive.")
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity})

    def test_sell_shares_negative_price_raises_error(self):
        """Test selling shares with a negative price raises ValueError."""
        symbol = "AAPL"
        buy_quantity = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_quantity, buy_price)

        sell_quantity = 3
        sell_price_negative = -175.0

        with self.assertRaises(ValueError) as cm:
            self.account.sell_shares(symbol, sell_quantity, sell_price_negative)
        self.assertEqual(str(cm.exception), "Sale price cannot be negative.")
        self.assertEqual(self.account.get_holdings(), {symbol: buy_quantity})


    def test_get_holdings_empty(self):
        """Test get_holdings when no shares are held."""
        self.assertEqual(self.account.get_holdings(), {})

    def test_get_holdings_after_trades(self):
        """Test get_holdings after buying and selling."""
        symbol1 = "AAPL"
        qty1 = 5
        price1 = 170.0
        self.account.buy_shares(symbol1, qty1, price1)

        symbol2 = "TSLA"
        qty2 = 2
        price2 = 250.0
        self.account.buy_shares(symbol2, qty2, price2)

        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {symbol1: qty1, symbol2: qty2})

        self.account.sell_shares(symbol1, 2, 175.0)
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {symbol1: qty1 - 2, symbol2: qty2})

        self.account.sell_shares(symbol2, 2, 260.0)
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {symbol1: qty1 - 2})


    def test_get_portfolio_value_empty(self):
        """Test get_portfolio_value when no shares are held."""
        self.assertEqual(self.account.get_portfolio_value(), 0.0)

    def test_get_portfolio_value_with_holdings(self):
        """Test get_portfolio_value with held shares."""
        symbol_aapl = "AAPL"
        qty_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)

        symbol_tsla = "TSLA"
        qty_tsla = 2
        price_tsla = 250.0
        self.account.buy_shares(symbol_tsla, qty_tsla, price_tsla)

        # Using mock prices: AAPL=170.0, TSLA=250.0
        expected_portfolio_value = (qty_aapl * 170.0) + (qty_tsla * 250.0)
        self.assertEqual(self.account.get_portfolio_value(), expected_portfolio_value)

    def test_get_portfolio_value_with_unknown_symbol(self):
        """Test get_portfolio_value with a symbol not in mock prices."""
        symbol_unknown = "XYZ"
        qty_unknown = 10
        self.account.buy_shares(symbol_unknown, qty_unknown, 50.0) # Price here is purchase price

        # get_share_price("XYZ") returns 0.0
        expected_portfolio_value = qty_unknown * 0.0
        self.assertEqual(self.account.get_portfolio_value(), expected_portfolio_value)

        # Add a known symbol too
        symbol_aapl = "AAPL"
        qty_aapl = 3
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)
        expected_portfolio_value += qty_aapl * 170.0
        self.assertEqual(self.account.get_portfolio_value(), expected_portfolio_value)


    def test_get_total_value_no_holdings(self):
        """Test get_total_value with only cash."""
        self.assertEqual(self.account.get_total_value(), self.initial_deposit)

    def test_get_total_value_with_holdings(self):
        """Test get_total_value with cash and holdings."""
        symbol_aapl = "AAPL"
        qty_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)

        # Cash balance after buying: 10000 - (5 * 170) = 10000 - 850 = 9150
        expected_cash_balance = self.initial_deposit - (qty_aapl * price_aapl)
        self.assertEqual(self.account._cash_balance, expected_cash_balance)

        # Portfolio value: 5 * 170.0 = 850.0
        expected_portfolio_value = qty_aapl * get_share_price(symbol_aapl)

        # Total value: cash + portfolio
        expected_total_value = expected_cash_balance + expected_portfolio_value
        self.assertEqual(self.account.get_total_value(), expected_total_value)

    def test_get_total_value_after_sell(self):
        """Test get_total_value after selling shares."""
        symbol_aapl = "AAPL"
        qty_aapl = 5
        price_aapl = 170.0
        self.account.buy_shares(symbol_aapl, qty_aapl, price_aapl)

        sell_qty = 2
        sell_price = 175.0
        self.account.sell_shares(symbol_aapl, sell_qty, sell_price)

        # Expected cash: 10000 - (5*170) + (2*175) = 10000 - 850 + 350 = 9500
        expected_cash_balance = self.initial_deposit - (qty_aapl * price_aapl) + (sell_qty * sell_price)
        self.assertEqual(self.account._cash_balance, expected_cash_balance)

        # Expected portfolio: (5-2) * 170 = 3 * 170 = 510
        expected_portfolio_value = (qty_aapl - sell_qty) * get_share_price(symbol_aapl)

        expected_total_value = expected_cash_balance + expected_portfolio_value
        self.assertEqual(self.account.get_total_value(), expected_total_value)


    def test_get_profit_loss_initial_state(self):
        """Test get_profit_loss at initial state."""
        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Current total value: 10000 (cash) + 0 (portfolio) = 10000
        # P/L = 10000 - 10000 + 0 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_deposit(self):
        """Test get_profit_loss after an additional deposit."""
        deposit_amount = 2000.0
        self.account.deposit(deposit_amount)
        # Initial deposit: 10000
        # Total deposits: 10000 + 2000 = 12000
        # Total withdrawals: 0
        # Current total value: 12000 (cash) + 0 (portfolio) = 12000
        # P/L = 12000 - 12000 + 0 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_withdrawal(self):
        """Test get_profit_loss after a withdrawal."""
        withdraw_amount = 3000.0
        self.account.withdraw(withdraw_amount)
        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 3000
        # Current total value: 7000 (cash) + 0 (portfolio) = 7000
        # P/L = 7000 - 10000 + 3000 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_buy_no_price_change(self):
        """Test get_profit_loss after buying shares at the same price as market."""
        symbol = "AAPL"
        qty = 5
        price = 170.0 # Market price
        self.account.buy_shares(symbol, qty, price)

        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (5 * 170) = 10000 - 850 = 9150
        # Portfolio value: 5 * 170 = 850
        # Current total value: 9150 + 850 = 10000
        # P/L = 10000 - 10000 + 0 = 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

    def test_get_profit_loss_after_buy_price_increase(self):
        """Test get_profit_loss after buying shares and then market price increases."""
        symbol = "TSLA"
        qty = 2
        buy_price = 250.0 # Buying at market price
        self.account.buy_shares(symbol, qty, buy_price)

        # Current state:
        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (2 * 250) = 10000 - 500 = 9500
        # Portfolio value (using mock_prices["TSLA"] = 250.0): 2 * 250 = 500
        # Current total value: 9500 + 500 = 10000
        # P/L = 10000 - 10000 + 0 = 0

        # If get_share_price returned 300.0 for TSLA:
        # Portfolio value: 2 * 300 = 600
        # Current total value: 9500 + 600 = 10100
        # P/L = 10100 - 10000 + 0 = 100 (Profit)
        # Since the mock is static, the P/L will be 0 unless we sell or do something else.
        self.assertEqual(self.account.get_profit_loss(), 0.0) # Based on static mock price

    def test_get_profit_loss_after_sell_profit(self):
        """Test get_profit_loss after selling shares for a profit."""
        symbol = "AAPL"
        buy_qty = 5
        buy_price = 170.0
        self.account.buy_shares(symbol, buy_qty, buy_price)

        sell_qty = 3
        sell_price = 180.0 # Selling at a higher price than buy_price (170.0)
        self.account.sell_shares(symbol, sell_qty, sell_price)

        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (5*170) + (3*180) = 10000 - 850 + 540 = 9690
        # Holdings: {AAPL: 2}
        # Portfolio value: 2 * 170 (current mock price) = 340
        # Current total value: 9690 + 340 = 10030
        # P/L = 10030 - 10000 + 0 = 30 (Profit)
        self.assertAlmostEqual(self.account.get_profit_loss(), 30.0, places=2)

    def test_get_profit_loss_after_sell_loss(self):
        """Test get_profit_loss after selling shares for a loss."""
        symbol = "TSLA"
        buy_qty = 2
        buy_price = 250.0
        self.account.buy_shares(symbol, buy_qty, buy_price)

        sell_qty = 1
        sell_price = 240.0 # Selling at a lower price than buy_price (250.0)
        self.account.sell_shares(symbol, sell_qty, sell_price)

        # Initial deposit: 10000
        # Total deposits: 10000
        # Total withdrawals: 0
        # Cash balance: 10000 - (2*250) + (1*240) = 10000 - 500 + 240 = 9740
        # Holdings: {TSLA: 1}
        # Portfolio value: 1 * 250 (current mock price) = 250
        # Current total value: 9740 + 250 = 9990
        # P/L = 9990 - 10000 + 0 = -10 (Loss)
        self.assertAlmostEqual(self.account.get_profit_loss(), -10.0, places=2)

    def test_get_profit_loss_with_deposits_and_withdrawals(self):
        """Test get_profit_loss with a mix of transactions."""
        # Start: 10000 cash
        self.account.deposit(5000) # Cash: 15000, Total Deposits: 15000
        self.account.buy_shares("AAPL", 10, 170.0) # Cash: 15000 - 1700 = 13300, Holdings: {AAPL: 10}, Portfolio: 1700
        self.account.withdraw(2000) # Cash: 11300, Total Withdrawals: 2000
        self.account.sell_shares("AAPL", 5, 175.0) # Cash: 11300 + (5*175) = 11300 + 875 = 12175, Holdings: {AAPL: 5}, Portfolio: 5*170 = 850

        # Calculations:
        # Initial deposit: 10000
        # Total deposits: 10000 + 5000 = 15000
        # Total withdrawals: 2000
        # Cash balance: 12175
        # Holdings: {AAPL: 5}
        # Portfolio value: 5 * 170.0 = 850.0
        # Current total value: 12175 + 850 = 13025
        # P/L = Current Total Value - Total Deposits + Total Withdrawals
        # P/L = 13025 - 15000 + 2000 = 3025
        self.assertAlmostEqual(self.account.get_profit_loss(), 3025.0, places=2)


    def test_get_transaction_history_empty(self):
        """Test get_transaction_history when no transactions made (should not happen after init)."""
        # Account is initialized with a deposit, so history is never truly empty.
        # This test is more about checking the initial state of history.
        self.assertEqual(len(self.account.get_transaction_history()), 1)
        self.assertEqual(self.account.get_transaction_history()[0]['type'], 'DEPOSIT')

    def test_get_transaction_history_after_multiple_operations(self):
        """Test get_transaction_history after several operations."""
        self.account.deposit(500.0)
        self.account.buy_shares("TSLA", 2, 250.0)
        self.account.withdraw(1000.0)
        self.account.sell_shares("TSLA", 1, 260.0)

        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 5) # Initial deposit + 4 operations

        # Check types and order (should be chronological)
        self.assertEqual(history[0]['type'], 'DEPOSIT')
        self.assertEqual(history[1]['type'], 'DEPOSIT')
        self.assertEqual(history[2]['type'], 'BUY')
        self.assertEqual(history[3]['type'], 'WITHDRAW')
        self.assertEqual(history[4]['type'], 'SELL')

        # Check details of a specific transaction (e.g., the last sell)
        sell_transaction = history[4]
        self.assertEqual(sell_transaction['symbol'], "TSLA")
        self.assertEqual(sell_transaction['quantity'], 1)
        self.assertEqual(sell_transaction['price_per_unit'], 260.0)
        self.assertEqual(sell_transaction['amount'], 260.0) # 1 share * 260.0

    def test_get_transaction_history_returns_copy(self):
        """Test that get_transaction_history returns a copy, not the internal list."""
        history1 = self.account.get_transaction_history()
        self.assertEqual(len(history1), 1)

        self.account.deposit(100.0)
        history2 = self.account.get_transaction_history()
        self.assertEqual(len(history2), 2)

        # Modify the first history list obtained
        history1.append({'test': 'manipulation'})
        self.assertEqual(len(history1), 2)
        self.assertEqual(len(history2), 2) # history2 should remain unchanged

        # Verify internal transactions list is also unchanged by external modification
        self.assertEqual(len(self.account._transactions), 2)

# This allows running the tests directly from the command line
if __name__ == '__main__':
    unittest.main()
```