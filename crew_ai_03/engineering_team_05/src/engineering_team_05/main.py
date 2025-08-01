#!/usr/bin/env python
import dotenv
import warnings

dotenv.load_dotenv(override=True)

from crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

_REQUIREMENTS = ('A simple account management system for a trading simulation platform. '
                 'The system should allow users to create an account, deposit funds, and withdraw funds. '
                 'The system should allow users to record that they have bought or sold shares, providing a quantity. '
                 "The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit. "
                 'The system should be able to report the holdings of the user at any point in time. '
                 'The system should be able to report the profit or loss of the user at any point in time. '
                 'The system should be able to list the transactions that the user has made over time. '
                 'The system should prevent the user from withdrawing funds that would leave them with a negative balance, or '
                 "from buying more shares than they can afford, or selling shares that they don't have. "
                 "The system has access to a function get_share_price(symbol) which returns the current price of a share, "
                 "and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL.")
_MODULE_NAME = "accounts.py"
_CLASS_NAME = "Account"

def run():
    """
    Run the crew.
    """
    inputs = {
        'requirements': _REQUIREMENTS,
        'module_name': _MODULE_NAME,
        'class_name': _CLASS_NAME
    }

    try:
        result = EngineeringTeam().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == '__main__':
    run()
