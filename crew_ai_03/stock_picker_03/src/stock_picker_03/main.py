#!/usr/bin/env python
import warnings
from dotenv import load_dotenv

load_dotenv(override=True)

from crew import StockPicker03

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'sector': 'Energy'
    }

    try:
        result = StockPicker03().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == '__main__':
    run()
