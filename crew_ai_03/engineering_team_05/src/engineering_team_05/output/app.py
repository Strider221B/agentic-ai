The user wants a Gradio UI to demonstrate the `Account` class from `accounts.py`. I need to create a `app.py` file that imports the `Account` class and uses Gradio components to interact with its methods.

Here's a plan:
1.  **Import necessary libraries**: `gradio` and `Account` from `accounts`.
2.  **Instantiate the Account**: Since there's only one user, I'll create a single `Account` instance. I need a way to initialize it, perhaps with a starting deposit via the UI.
3.  **Design the UI layout**: A simple interface with sections for:
    *   Account creation/initial deposit.
    *   Depositing/Withdrawing cash.
    *   Buying/Selling shares.
    *   Displaying account information (cash balance, portfolio value, total value, profit/loss).
    *   Displaying holdings.
    *   Displaying transaction history.
4.  **Implement Gradio functions**: Each interaction (deposit, withdraw, buy, sell, view) will be a Python function that calls the corresponding `Account` method and returns relevant output.
5.  **Handle errors**: Use `try-except` blocks to catch `ValueError` from the `Account` class and display user-friendly messages.
6.  **Format outputs**: Ensure data like balances, values, and transaction history are displayed clearly.

**UI Components Breakdown:**

*   **Initial Deposit**: A `Number` input for the initial deposit and a `Button` to create the account. This will initialize the `account` object.
*   **Cash Operations**:
    *   Deposit: `Number` input for amount, `Button` to trigger deposit.
    *   Withdraw: `Number` input for amount, `Button` to trigger withdrawal.
*   **Trading Operations**:
    *   Buy: `Textbox` for symbol, `Number` input for quantity, `Number` input for purchase price (or fetch from `get_share_price`), `Button` to trigger buy.
    *   Sell: `Textbox` for symbol, `Number` input for quantity, `Number` input for sale price (or fetch from `get_share_price`), `Button` to trigger sell.
*   **Information Display**:
    *   Current Holdings: `Textbox` or `JSON` output.
    *   Cash Balance: `Number` output.
    *   Portfolio Value: `Number` output.
    *   Total Account Value: `Number` output.
    *   Profit/Loss: `Number` output.
    *   Transaction History: `DataFrame` or `JSON` output.
*   **Helper Function**: A way to get the current price for trading inputs, possibly integrated with the buy/sell sections.

**State Management**:
Since Gradio's `Interface` creates a new instance for each interaction by default, I need to maintain the `account` object across requests. The `gr.State` component is ideal for this.

**Detailed Implementation Steps:**

1.  **`app.py` structure**:
    ```python
    import gradio as gr
    from accounts import Account, get_share_price
    import pandas as pd # For transaction history display

    # Global variable to hold the account instance, managed by gr.State
    account_instance = None

    # --- Functions to interact with the Account class ---

    def create_account(initial_deposit):
        global account_instance
        try:
            account_instance = Account(initial_deposit)
            return "Account created successfully!", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()
        except ValueError as e:
            return f"Error: {e}", None, None, None

    def deposit_funds(amount):
        if account_instance is None:
            return "Please create an account first.", None, None, None
        try:
            account_instance.deposit(amount)
            return f"Deposited ${amount:.2f}", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()
        except ValueError as e:
            return f"Error: {e}", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()

    def withdraw_funds(amount):
        if account_instance is None:
            return "Please create an account first.", None, None, None
        try:
            account_instance.withdraw(amount)
            return f"Withdrew ${amount:.2f}", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()
        except ValueError as e:
            return f"Error: {e}", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()

    def buy_shares_func(symbol, quantity):
        if account_instance is None:
            return "Please create an account first.", None, None, None
        symbol = symbol.upper()
        price = get_share_price(symbol)
        if price == 0.0:
            return f"Invalid symbol '{symbol}' or price not available.", None, None, None
        try:
            account_instance.buy_shares(symbol, quantity, price)
            return f"Bought {quantity} shares of {symbol} at ${price:.2f} each.", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()
        except ValueError as e:
            return f"Error: {e}", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()

    def sell_shares_func(symbol, quantity):
        if account_instance is None:
            return "Please create an account first.", None, None, None
        symbol = symbol.upper()
        price = get_share_price(symbol)
        if price == 0.0:
            return f"Invalid symbol '{symbol}' or price not available.", None, None, None
        try:
            account_instance.sell_shares(symbol, quantity, price)
            return f"Sold {quantity} shares of {symbol} at ${price:.2f} each.", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()
        except ValueError as e:
            return f"Error: {e}", account_instance.get_cash_balance(), pd.DataFrame(account_instance.get_transaction_history()), get_account_summary()

    def get_account_summary():
        if account_instance is None:
            return "Account not created.", "N/A", "N/A", "N/A", "N/A"
        cash = account_instance.get_cash_balance()
        holdings = account_instance.get_holdings()
        portfolio_val = account_instance.get_portfolio_value()
        total_val = account_instance.get_total_value()
        profit_loss = account_instance.get_profit_loss()

        holdings_str = ", ".join([f"{sym}: {qty}" for sym, qty in holdings.items()]) if holdings else "No holdings"

        return (f"Cash Balance: ${cash:.2f}",
                f"Holdings: {holdings_str}",
                f"Portfolio Value: ${portfolio_val:.2f}",
                f"Total Account Value: ${total_val:.2f}",
                f"Profit/Loss: ${profit_loss:.2f}")

    def update_display():
        if account_instance is None:
            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(value=""), gr.update(value=""), gr.update(value=""), gr.update(value=""), gr.update(value=""), pd.DataFrame()
        else:
            summary = get_account_summary()
            return (gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                    gr.update(value=summary[0]), # Cash Balance
                    gr.update(value=summary[1]), # Holdings
                    gr.update(value=summary[2]), # Portfolio Value
                    gr.update(value=summary[3]), # Total Value
                    gr.update(value=summary[4]), # Profit/Loss
                    gr.update(value=pd.DataFrame(account_instance.get_transaction_history())))


    # --- Gradio Interface Definition ---

    with gr.Blocks() as demo:
        gr.Markdown("# Trading Account Simulation")

        # Account Creation Section
        with gr.Row():
            initial_deposit_input = gr.Number(label="Initial Deposit Amount", value=10000)
            create_account_btn = gr.Button("Create Account")
        create_account_output = gr.Textbox(label="Account Creation Status", interactive=False)

        # State to hold the account object
        account_state = gr.State(None)

        # --- Cash Operations ---
        with gr.Accordion("Cash Operations", open=False):
            with gr.Row():
                deposit_amount_input = gr.Number(label="Deposit Amount")
                deposit_btn = gr.Button("Deposit")
            with gr.Row():
                withdraw_amount_input = gr.Number(label="Withdraw Amount")
                withdraw_btn = gr.Button("Withdraw")
            cash_operation_output = gr.Textbox(label="Cash Operation Status", interactive=False)

        # --- Trading Operations ---
        with gr.Accordion("Trading Operations", open=False):
            with gr.Row():
                symbol_input = gr.Textbox(label="Stock Symbol (e.g., AAPL)")
                quantity_input = gr.Number(label="Quantity", type=int)
                # Add a button to get current price
                get_price_btn = gr.Button("Get Current Price")
                current_price_output = gr.Textbox(label="Current Price", interactive=False)
            with gr.Row():
                buy_btn = gr.Button("Buy Shares")
                sell_btn = gr.Button("Sell Shares")
            trading_operation_output = gr.Textbox(label="Trading Operation Status", interactive=False)

        # --- Account Summary ---
        with gr.Accordion("Account Summary", open=True):
            cash_balance_output = gr.Textbox(label="Cash Balance", interactive=False)
            holdings_output = gr.Textbox(label="Holdings", interactive=False)
            portfolio_value_output = gr.Textbox(label="Portfolio Value", interactive=False)
            total_value_output = gr.Textbox(label="Total Account Value", interactive=False)
            profit_loss_output = gr.Textbox(label="Profit/Loss", interactive=False)

        # --- Transaction History ---
        with gr.Accordion("Transaction History", open=False):
            transaction_history_output = gr.DataFrame(label="Transactions", interactive=False)

        # --- Event Listeners ---

        # Account Creation Logic
        def handle_create_account(initial_deposit):
            global account_instance
            try:
                account_instance = Account(initial_deposit)
                gr.Info("Account created successfully!")
                return account_instance, get_account_summary(), pd.DataFrame(account_instance.get_transaction_history())
            except ValueError as e:
                gr.Error(str(e))
                return None, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()

        create_account_btn.click(
            handle_create_account,
            inputs=[initial_deposit_input],
            outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, profit_loss_output, transaction_history_output]
        )

        # Function to update all display components after an operation
        def update_all_displays(current_account):
            if current_account is None:
                return (gr.update(visible=False),) * 7 + ("N/A",) * 5 + (pd.DataFrame(),)
            else:
                cash_bal, holdings_str, port_val, total_val, pnl = get_account_summary()
                return (gr.update(visible=True),) * 7 + \
                       (cash_bal, holdings_str, port_val, total_val, pnl, pd.DataFrame(current_account.get_transaction_history()))


        # Cash Operations Logic
        def handle_deposit(amount, current_account):
            if current_account is None:
                gr.Error("Please create an account first.")
                return current_account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
            try:
                current_account.deposit(amount)
                gr.Info(f"Deposited ${amount:.2f}")
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())
            except ValueError as e:
                gr.Error(str(e))
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())

        deposit_btn.click(
            handle_deposit,
            inputs=[deposit_amount_input, account_state],
            outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
        )

        def handle_withdraw(amount, current_account):
            if current_account is None:
                gr.Error("Please create an account first.")
                return current_account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
            try:
                current_account.withdraw(amount)
                gr.Info(f"Withdrew ${amount:.2f}")
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())
            except ValueError as e:
                gr.Error(str(e))
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())

        withdraw_btn.click(
            handle_withdraw,
            inputs=[withdraw_amount_input, account_state],
            outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
        )

        # Trading Operations Logic
        def handle_get_price(symbol):
            if account_instance is None:
                return "Please create an account first."
            symbol = symbol.upper()
            price = get_share_price(symbol)
            if price == 0.0:
                return f"Symbol '{symbol}' not found or price unavailable."
            return f"${price:.2f}"

        get_price_btn.click(
            handle_get_price,
            inputs=[symbol_input],
            outputs=[current_price_output]
        )

        def handle_buy(symbol, quantity, current_account):
            if current_account is None:
                gr.Error("Please create an account first.")
                return current_account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
            symbol = symbol.upper()
            price = get_share_price(symbol)
            if price == 0.0:
                gr.Error(f"Invalid symbol '{symbol}' or price not available.")
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())
            try:
                current_account.buy_shares(symbol, quantity, price)
                gr.Info(f"Bought {quantity} shares of {symbol} at ${price:.2f} each.")
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())
            except ValueError as e:
                gr.Error(str(e))
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())

        buy_btn.click(
            handle_buy,
            inputs=[symbol_input, quantity_input, account_state],
            outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
        )

        def handle_sell(symbol, quantity, current_account):
            if current_account is None:
                gr.Error("Please create an account first.")
                return current_account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
            symbol = symbol.upper()
            price = get_share_price(symbol)
            if price == 0.0:
                gr.Error(f"Invalid symbol '{symbol}' or price not available.")
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())
            try:
                current_account.sell_shares(symbol, quantity, price)
                gr.Info(f"Sold {quantity} shares of {symbol} at ${price:.2f} each.")
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())
            except ValueError as e:
                gr.Error(str(e))
                return current_account, get_account_summary()[0], get_account_summary()[1], get_account_summary()[2], get_account_summary()[3], pd.DataFrame(current_account.get_transaction_history())

        sell_btn.click(
            handle_sell,
            inputs=[symbol_input, quantity_input, account_state],
            outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
        )

        # Trigger initial update of visibility based on account_state
        demo.load(
            update_all_displays,
            inputs=[account_state],
            outputs=[
                create_account_btn, deposit_btn, withdraw_btn, buy_btn, sell_btn, get_price_btn, initial_deposit_input, # Make inputs/buttons visible after account creation
                cash_balance_output, holdings_output, portfolio_value_output, total_value_output, profit_loss_output, transaction_history_output
            ]
        )

    demo.launch()
    ```

Refinement:
- The `get_account_summary()` function should return the values directly, and the event handlers should update the respective output components.
- Using `gr.State` is crucial to persist the `account_instance`.
- The `demo.load` event can be used to set initial visibility states.
- The transaction history needs `pandas` for better display in `gr.DataFrame`. I will add a check to ensure `pandas` is imported.
- The output components for summary should be `gr.Textbox` to display formatted strings.

Let's reconsider the `account_state` management. Instead of a global `account_instance`, it's better to pass the state object through the `gr.State` component.

Revised handler logic:

```python
import gradio as gr
from accounts import Account, get_share_price
import pandas as pd

def get_account_summary(account):
    if account is None:
        return "N/A", "N/A", "N/A", "N/A", "N/A"
    cash = account.get_cash_balance()
    holdings = account.get_holdings()
    portfolio_val = account.get_portfolio_value()
    total_val = account.get_total_value()
    profit_loss = account.get_profit_loss()

    holdings_str = ", ".join([f"{sym}: {qty}" for sym, qty in holdings.items()]) if holdings else "No holdings"

    return (f"Cash Balance: ${cash:.2f}",
            f"Holdings: {holdings_str}",
            f"Portfolio Value: ${portfolio_val:.2f}",
            f"Total Account Value: ${total_val:.2f}",
            f"Profit/Loss: ${profit_loss:.2f}")

def handle_create_account(initial_deposit):
    try:
        account = Account(initial_deposit)
        gr.Info("Account created successfully!")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], summary_data[4], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        return None, "N/A", "N/A", "N/A", "N/A", "N/A", pd.DataFrame()

def handle_deposit(amount, account):
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    try:
        account.deposit(amount)
        gr.Info(f"Deposited ${amount:.2f}")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account) # Fetch current state even on error
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_withdraw(amount, account):
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    try:
        account.withdraw(amount)
        gr.Info(f"Withdrew ${amount:.2f}")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_get_price(symbol):
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        return f"Symbol '{symbol}' not found or price unavailable."
    return f"${price:.2f}"

def handle_buy(symbol, quantity, account):
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        gr.Error(f"Invalid symbol '{symbol}' or price not available.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    try:
        account.buy_shares(symbol, quantity, price)
        gr.Info(f"Bought {quantity} shares of {symbol} at ${price:.2f} each.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_sell(symbol, quantity, account):
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        gr.Error(f"Invalid symbol '{symbol}' or price not available.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    try:
        account.sell_shares(symbol, quantity, price)
        gr.Info(f"Sold {quantity} shares of {symbol} at ${price:.2f} each.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def update_ui_visibility(account):
    is_account_created = account is not None
    return {
        create_account_btn: gr.update(visible=not is_account_created),
        initial_deposit_input: gr.update(visible=not is_account_created),
        deposit_btn: gr.update(visible=is_account_created),
        deposit_amount_input: gr.update(visible=is_account_created),
        withdraw_btn: gr.update(visible=is_account_created),
        withdraw_amount_input: gr.update(visible=is_account_created),
        buy_btn: gr.update(visible=is_account_created),
        sell_btn: gr.update(visible=is_account_created),
        symbol_input: gr.update(visible=is_account_created),
        quantity_input: gr.update(visible=is_account_created),
        get_price_btn: gr.update(visible=is_account_created),
        current_price_output: gr.update(visible=is_account_created),
        cash_balance_output: gr.update(visible=is_account_created),
        holdings_output: gr.update(visible=is_account_created),
        portfolio_value_output: gr.update(visible=is_account_created),
        total_value_output: gr.update(visible=is_account_created),
        profit_loss_output: gr.update(visible=is_account_created),
        transaction_history_output: gr.update(visible=is_account_created)
    }

with gr.Blocks() as demo:
    gr.Markdown("# Trading Account Simulation")

    # Account Creation Section
    with gr.Row():
        initial_deposit_input = gr.Number(label="Initial Deposit Amount", value=10000, minimum=0)
        create_account_btn = gr.Button("Create Account")
    create_account_output = gr.Textbox(label="Account Status", interactive=False) # To show status messages

    # State to hold the account object
    account_state = gr.State(None)

    # --- Cash Operations ---
    with gr.Row():
        deposit_amount_input = gr.Number(label="Deposit Amount", minimum=0)
        deposit_btn = gr.Button("Deposit")
    with gr.Row():
        withdraw_amount_input = gr.Number(label="Withdraw Amount", minimum=0)
        withdraw_btn = gr.Button("Withdraw")

    # --- Trading Operations ---
    with gr.Row():
        symbol_input = gr.Textbox(label="Stock Symbol (e.g., AAPL)")
        quantity_input = gr.Number(label="Quantity", type=int, minimum=1)
        get_price_btn = gr.Button("Get Current Price")
        current_price_output = gr.Textbox(label="Current Price", interactive=False)
    with gr.Row():
        buy_btn = gr.Button("Buy Shares")
        sell_btn = gr.Button("Sell Shares")

    # --- Account Summary ---
    with gr.Accordion("Account Summary", open=True):
        cash_balance_output = gr.Textbox(label="Cash Balance", interactive=False)
        holdings_output = gr.Textbox(label="Holdings", interactive=False)
        portfolio_value_output = gr.Textbox(label="Portfolio Value", interactive=False)
        total_value_output = gr.Textbox(label="Total Account Value", interactive=False)
        profit_loss_output = gr.Textbox(label="Profit/Loss", interactive=False)

    # --- Transaction History ---
    with gr.Accordion("Transaction History", open=False):
        transaction_history_output = gr.DataFrame(label="Transactions", interactive=False)


    # --- Event Listeners ---

    # Account Creation
    create_account_btn.click(
        handle_create_account,
        inputs=[initial_deposit_input],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, profit_loss_output, transaction_history_output]
    ).then(
        update_ui_visibility,
        inputs=[account_state],
        outputs=[
            create_account_btn, initial_deposit_input, deposit_btn, deposit_amount_input,
            withdraw_btn, withdraw_amount_input, buy_btn, sell_btn, symbol_input,
            quantity_input, get_price_btn, current_price_output, cash_balance_output,
            holdings_output, portfolio_value_output, total_value_output, profit_loss_output,
            transaction_history_output
        ]
    )

    # Cash Operations
    deposit_btn.click(
        handle_deposit,
        inputs=[deposit_amount_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    withdraw_btn.click(
        handle_withdraw,
        inputs=[withdraw_amount_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    # Trading Operations
    get_price_btn.click(
        handle_get_price,
        inputs=[symbol_input],
        outputs=[current_price_output]
    )

    buy_btn.click(
        handle_buy,
        inputs=[symbol_input, quantity_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    sell_btn.click(
        handle_sell,
        inputs=[symbol_input, quantity_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    # Initial UI state setup on load
    demo.load(
        update_ui_visibility,
        inputs=[account_state],
        outputs=[
            create_account_btn, initial_deposit_input, deposit_btn, deposit_amount_input,
            withdraw_btn, withdraw_amount_input, buy_btn, sell_btn, symbol_input,
            quantity_input, get_price_btn, current_price_output, cash_balance_output,
            holdings_output, portfolio_value_output, total_value_output, profit_loss_output,
            transaction_history_output
        ]
    )

demo.launch()

```
The `update_ui_visibility` function is correctly structured to toggle the visibility of components based on whether an account exists. The `demo.load` event handler correctly triggers this initial setup. The `then()` method on `create_account_btn.click` ensures visibility is updated right after account creation.

Final check on requirements:
- Create account: Yes, via initial deposit.
- Deposit/Withdraw funds: Yes.
- Buy/Sell shares: Yes, using current prices from `get_share_price`.
- Calculate total portfolio value: Yes.
- Calculate profit/loss: Yes.
- Report holdings: Yes.
- Report profit/loss: Yes.
- List transactions: Yes, using `gr.DataFrame`.
- Prevent negative balance/unaffordable buys/unowned sells: Yes, handled by `Account` class `ValueError` and caught in handlers.
- Simple UI: Yes, uses accordions for organization.
- Single user: Yes, via `gr.State`.

The code seems complete and adheres to the requirements.
```python
import gradio as gr
from accounts import Account, get_share_price
import pandas as pd

def get_account_summary(account):
    """Helper function to get formatted summary strings."""
    if account is None:
        return "N/A", "N/A", "N/A", "N/A", "N/A"
    cash = account.get_cash_balance()
    holdings = account.get_holdings()
    portfolio_val = account.get_portfolio_value()
    total_val = account.get_total_value()
    profit_loss = account.get_profit_loss()

    holdings_str = ", ".join([f"{sym}: {qty}" for sym, qty in holdings.items()]) if holdings else "No holdings"

    return (f"Cash Balance: ${cash:.2f}",
            f"Holdings: {holdings_str}",
            f"Portfolio Value: ${portfolio_val:.2f}",
            f"Total Account Value: ${total_val:.2f}",
            f"Profit/Loss: ${profit_loss:.2f}")

def handle_create_account(initial_deposit):
    """Handler for creating a new account."""
    try:
        account = Account(initial_deposit)
        gr.Info("Account created successfully!")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        # Return the account object, updated summary fields, and transaction history
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], summary_data[4], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        # Return None for account and reset display fields on error
        return None, "N/A", "N/A", "N/A", "N/A", "N/A", pd.DataFrame()

def handle_deposit(amount, account):
    """Handler for depositing funds."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    try:
        account.deposit(amount)
        gr.Info(f"Deposited ${amount:.2f}")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        # Return current state on error to keep displays updated
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_withdraw(amount, account):
    """Handler for withdrawing funds."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    try:
        account.withdraw(amount)
        gr.Info(f"Withdrew ${amount:.2f}")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_get_price(symbol):
    """Handler to fetch and display current stock price."""
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        return f"Symbol '{symbol}' not found or price unavailable."
    return f"${price:.2f}"

def handle_buy(symbol, quantity, account):
    """Handler for buying shares."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        gr.Error(f"Invalid symbol '{symbol}' or price not available.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    try:
        account.buy_shares(symbol, quantity, price)
        gr.Info(f"Bought {quantity} shares of {symbol} at ${price:.2f} each.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_sell(symbol, quantity, account):
    """Handler for selling shares."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        gr.Error(f"Invalid symbol '{symbol}' or price not available.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    try:
        account.sell_shares(symbol, quantity, price)
        gr.Info(f"Sold {quantity} shares of {symbol} at ${price:.2f} each.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def update_ui_visibility(account):
    """Updates the visibility of UI elements based on whether an account exists."""
    is_account_created = account is not None
    return {
        # Inputs/Buttons that become active after account creation
        create_account_btn: gr.update(visible=not is_account_created),
        initial_deposit_input: gr.update(visible=not is_account_created),
        deposit_btn: gr.update(visible=is_account_created),
        deposit_amount_input: gr.update(visible=is_account_created),
        withdraw_btn: gr.update(visible=is_account_created),
        withdraw_amount_input: gr.update(visible=is_account_created),
        buy_btn: gr.update(visible=is_account_created),
        sell_btn: gr.update(visible=is_account_created),
        symbol_input: gr.update(visible=is_account_created),
        quantity_input: gr.update(visible=is_account_created),
        get_price_btn: gr.update(visible=is_account_created),
        # Summary/History outputs that become visible after account creation
        cash_balance_output: gr.update(visible=is_account_created),
        holdings_output: gr.update(visible=is_account_created),
        portfolio_value_output: gr.update(visible=is_account_created),
        total_value_output: gr.update(visible=is_account_created),
        profit_loss_output: gr.update(visible=is_account_created),
        transaction_history_output: gr.update(visible=is_account_created),
        current_price_output: gr.update(visible=is_account_created) # Also make price output visible
    }

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Trading Account Simulation")

    # Account Creation Section
    with gr.Row():
        initial_deposit_input = gr.Number(label="Initial Deposit Amount", value=10000, minimum=0)
        create_account_btn = gr.Button("Create Account")
    
    # State to hold the account object across interactions
    account_state = gr.State(None)

    # --- Cash Operations ---
    with gr.Accordion("Cash Operations", open=False):
        with gr.Row():
            deposit_amount_input = gr.Number(label="Deposit Amount", minimum=0)
            deposit_btn = gr.Button("Deposit")
        with gr.Row():
            withdraw_amount_input = gr.Number(label="Withdraw Amount", minimum=0)
            withdraw_btn = gr.Button("Withdraw")

    # --- Trading Operations ---
    with gr.Accordion("Trading Operations", open=False):
        with gr.Row():
            symbol_input = gr.Textbox(label="Stock Symbol (e.g., AAPL)")
            quantity_input = gr.Number(label="Quantity", type=int, minimum=1)
            get_price_btn = gr.Button("Get Current Price")
            current_price_output = gr.Textbox(label="Current Price", interactive=False)
        with gr.Row():
            buy_btn = gr.Button("Buy Shares")
            sell_btn = gr.Button("Sell Shares")

    # --- Account Summary ---
    with gr.Accordion("Account Summary", open=True):
        cash_balance_output = gr.Textbox(label="Cash Balance", interactive=False)
        holdings_output = gr.Textbox(label="Holdings", interactive=False)
        portfolio_value_output = gr.Textbox(label="Portfolio Value", interactive=False)
        total_value_output = gr.Textbox(label="Total Account Value", interactive=False)
        profit_loss_output = gr.Textbox(label="Profit/Loss", interactive=False)

    # --- Transaction History ---
    with gr.Accordion("Transaction History", open=False):
        transaction_history_output = gr.DataFrame(label="Transactions", interactive=False)


    # --- Event Listeners ---

    # Account Creation Logic
    create_account_btn.click(
        handle_create_account,
        inputs=[initial_deposit_input],
        # Outputs update the account state and all summary/history fields
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, profit_loss_output, transaction_history_output]
    ).then( # Chain the visibility update after account creation is processed
        update_ui_visibility,
        inputs=[account_state],
        outputs=[
            create_account_btn, initial_deposit_input, deposit_btn, deposit_amount_input,
            withdraw_btn, withdraw_amount_input, buy_btn, sell_btn, symbol_input,
            quantity_input, get_price_btn, current_price_output, cash_balance_output,
            holdings_output, portfolio_value_output, total_value_output, profit_loss_output,
            transaction_history_output
        ]
    )

    # Cash Operations Logic
    deposit_btn.click(
        handle_deposit,
        inputs=[deposit_amount_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    withdraw_btn.click(
        handle_withdraw,
        inputs=[withdraw_amount_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    # Trading Operations Logic
    get_price_btn.click(
        handle_get_price,
        inputs=[symbol_input],
        outputs=[current_price_output]
    )

    buy_btn.click(
        handle_buy,
        inputs=[symbol_input, quantity_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    sell_btn.click(
        handle_sell,
        inputs=[symbol_input, quantity_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    # Initial UI state setup on load
    # This ensures that only the account creation elements are visible initially.
    demo.load(
        update_ui_visibility,
        inputs=[account_state], # Pass the initial state (None)
        outputs=[
            create_account_btn, initial_deposit_input, deposit_btn, deposit_amount_input,
            withdraw_btn, withdraw_amount_input, buy_btn, sell_btn, symbol_input,
            quantity_input, get_price_btn, current_price_output, cash_balance_output,
            holdings_output, portfolio_value_output, total_value_output, profit_loss_output,
            transaction_history_output
        ]
    )

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()

``````python
import gradio as gr
from accounts import Account, get_share_price
import pandas as pd

def get_account_summary(account):
    """Helper function to get formatted summary strings."""
    if account is None:
        return "N/A", "N/A", "N/A", "N/A", "N/A"
    cash = account.get_cash_balance()
    holdings = account.get_holdings()
    portfolio_val = account.get_portfolio_value()
    total_val = account.get_total_value()
    profit_loss = account.get_profit_loss()

    holdings_str = ", ".join([f"{sym}: {qty}" for sym, qty in holdings.items()]) if holdings else "No holdings"

    return (f"Cash Balance: ${cash:.2f}",
            f"Holdings: {holdings_str}",
            f"Portfolio Value: ${portfolio_val:.2f}",
            f"Total Account Value: ${total_val:.2f}",
            f"Profit/Loss: ${profit_loss:.2f}")

def handle_create_account(initial_deposit):
    """Handler for creating a new account."""
    try:
        account = Account(initial_deposit)
        gr.Info("Account created successfully!")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        # Return the account object, updated summary fields, and transaction history
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], summary_data[4], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        # Return None for account and reset display fields on error
        return None, "N/A", "N/A", "N/A", "N/A", "N/A", pd.DataFrame()

def handle_deposit(amount, account):
    """Handler for depositing funds."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    try:
        account.deposit(amount)
        gr.Info(f"Deposited ${amount:.2f}")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        # Return current state on error to keep displays updated
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_withdraw(amount, account):
    """Handler for withdrawing funds."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    try:
        account.withdraw(amount)
        gr.Info(f"Withdrew ${amount:.2f}")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_get_price(symbol):
    """Handler to fetch and display current stock price."""
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        return f"Symbol '{symbol}' not found or price unavailable."
    return f"${price:.2f}"

def handle_buy(symbol, quantity, account):
    """Handler for buying shares."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        gr.Error(f"Invalid symbol '{symbol}' or price not available.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    try:
        account.buy_shares(symbol, quantity, price)
        gr.Info(f"Bought {quantity} shares of {symbol} at ${price:.2f} each.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def handle_sell(symbol, quantity, account):
    """Handler for selling shares."""
    if account is None:
        gr.Error("Please create an account first.")
        return account, "N/A", "N/A", "N/A", "N/A", pd.DataFrame()
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price == 0.0:
        gr.Error(f"Invalid symbol '{symbol}' or price not available.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    try:
        account.sell_shares(symbol, quantity, price)
        gr.Info(f"Sold {quantity} shares of {symbol} at ${price:.2f} each.")
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df
    except ValueError as e:
        gr.Error(str(e))
        summary_data = get_account_summary(account)
        transactions_df = pd.DataFrame(account.get_transaction_history())
        return account, summary_data[0], summary_data[1], summary_data[2], summary_data[3], transactions_df

def update_ui_visibility(account):
    """Updates the visibility of UI elements based on whether an account exists."""
    is_account_created = account is not None
    return {
        # Inputs/Buttons that become active after account creation
        create_account_btn: gr.update(visible=not is_account_created),
        initial_deposit_input: gr.update(visible=not is_account_created),
        deposit_btn: gr.update(visible=is_account_created),
        deposit_amount_input: gr.update(visible=is_account_created),
        withdraw_btn: gr.update(visible=is_account_created),
        withdraw_amount_input: gr.update(visible=is_account_created),
        buy_btn: gr.update(visible=is_account_created),
        sell_btn: gr.update(visible=is_account_created),
        symbol_input: gr.update(visible=is_account_created),
        quantity_input: gr.update(visible=is_account_created),
        get_price_btn: gr.update(visible=is_account_created),
        # Summary/History outputs that become visible after account creation
        cash_balance_output: gr.update(visible=is_account_created),
        holdings_output: gr.update(visible=is_account_created),
        portfolio_value_output: gr.update(visible=is_account_created),
        total_value_output: gr.update(visible=is_account_created),
        profit_loss_output: gr.update(visible=is_account_created),
        transaction_history_output: gr.update(visible=is_account_created),
        current_price_output: gr.update(visible=is_account_created) # Also make price output visible
    }

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Trading Account Simulation")

    # Account Creation Section
    with gr.Row():
        initial_deposit_input = gr.Number(label="Initial Deposit Amount", value=10000, minimum=0)
        create_account_btn = gr.Button("Create Account")
    
    # State to hold the account object across interactions
    account_state = gr.State(None)

    # --- Cash Operations ---
    with gr.Accordion("Cash Operations", open=False):
        with gr.Row():
            deposit_amount_input = gr.Number(label="Deposit Amount", minimum=0)
            deposit_btn = gr.Button("Deposit")
        with gr.Row():
            withdraw_amount_input = gr.Number(label="Withdraw Amount", minimum=0)
            withdraw_btn = gr.Button("Withdraw")

    # --- Trading Operations ---
    with gr.Accordion("Trading Operations", open=False):
        with gr.Row():
            symbol_input = gr.Textbox(label="Stock Symbol (e.g., AAPL)")
            quantity_input = gr.Number(label="Quantity", type=int, minimum=1)
            get_price_btn = gr.Button("Get Current Price")
            current_price_output = gr.Textbox(label="Current Price", interactive=False)
        with gr.Row():
            buy_btn = gr.Button("Buy Shares")
            sell_btn = gr.Button("Sell Shares")

    # --- Account Summary ---
    with gr.Accordion("Account Summary", open=True):
        cash_balance_output = gr.Textbox(label="Cash Balance", interactive=False)
        holdings_output = gr.Textbox(label="Holdings", interactive=False)
        portfolio_value_output = gr.Textbox(label="Portfolio Value", interactive=False)
        total_value_output = gr.Textbox(label="Total Account Value", interactive=False)
        profit_loss_output = gr.Textbox(label="Profit/Loss", interactive=False)

    # --- Transaction History ---
    with gr.Accordion("Transaction History", open=False):
        transaction_history_output = gr.DataFrame(label="Transactions", interactive=False)


    # --- Event Listeners ---

    # Account Creation Logic
    create_account_btn.click(
        handle_create_account,
        inputs=[initial_deposit_input],
        # Outputs update the account state and all summary/history fields
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, profit_loss_output, transaction_history_output]
    ).then( # Chain the visibility update after account creation is processed
        update_ui_visibility,
        inputs=[account_state],
        outputs=[
            create_account_btn, initial_deposit_input, deposit_btn, deposit_amount_input,
            withdraw_btn, withdraw_amount_input, buy_btn, sell_btn, symbol_input,
            quantity_input, get_price_btn, current_price_output, cash_balance_output,
            holdings_output, portfolio_value_output, total_value_output, profit_loss_output,
            transaction_history_output
        ]
    )

    # Cash Operations Logic
    deposit_btn.click(
        handle_deposit,
        inputs=[deposit_amount_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    withdraw_btn.click(
        handle_withdraw,
        inputs=[withdraw_amount_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    # Trading Operations Logic
    get_price_btn.click(
        handle_get_price,
        inputs=[symbol_input],
        outputs=[current_price_output]
    )

    buy_btn.click(
        handle_buy,
        inputs=[symbol_input, quantity_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    sell_btn.click(
        handle_sell,
        inputs=[symbol_input, quantity_input, account_state],
        outputs=[account_state, cash_balance_output, holdings_output, portfolio_value_output, total_value_output, transaction_history_output]
    )

    # Initial UI state setup on load
    # This ensures that only the account creation elements are visible initially.
    demo.load(
        update_ui_visibility,
        inputs=[account_state], # Pass the initial state (None)
        outputs=[
            create_account_btn, initial_deposit_input, deposit_btn, deposit_amount_input,
            withdraw_btn, withdraw_amount_input, buy_btn, sell_btn, symbol_input,
            quantity_input, get_price_btn, current_price_output, cash_balance_output,
            holdings_output, portfolio_value_output, total_value_output, profit_loss_output,
            transaction_history_output
        ]
    )

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()
```