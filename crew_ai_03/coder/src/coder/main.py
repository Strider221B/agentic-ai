#!/usr/bin/env python
import dotenv
import sys
import warnings
from datetime import datetime

dotenv.load_dotenv(override=True)

from crew import Coder

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

_ASSIGNMENT = ('Write a python program to calculate the first 10,000 terms of this series, '
               'multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ...')

def run():
    inputs = {'assignment': _ASSIGNMENT}

    try:
        result = Coder().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == '__main__':
    run()

## Output:
# Ensure current user is added to docker group for this to run using: sudo usermod -aG docker $USER
# (P3.12_LLM) ~/Git/agentic-ai/crew_ai_03/coder/src/coder$ python main.py
# ╭─────────────────────────────────────────────────────────────────────────────────────────── Crew Execution Started ────────────────────────────────────────────────────────────────────────────────────────────╮
# │                                                                                                                                                                                                               │
# │  Crew Execution Started                                                                                                                                                                                       │
# │  Name: crew                                                                                                                                                                                                   │
# │  ID: 3dfdad79-b5e1-40fc-a5aa-9364e8aa916e                                                                                                                                                                     │
# │                                                                                                                                                                                                               │
# │                                                                                                                                                                                                               │
# ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

# /home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:623: UserWarning: <built-in function callable> is not a Python type (it may be an instance of an object), Pydantic will allow any object with no validation since we cannot even enforce that the input is an instance of the given type. To get rid of this error wrap the type with `pydantic.SkipValidation`.
#   warn(
# 🚀 Crew: crew
# └── 📋 Task: 3620e008-d22e-4e92-901a-a40c177a47c3
#        Status: Executing Task...

# 🚀 Crew: crew
# └── 📋 Task: 3620e008-d22e-4e92-901a-a40c177a47c3
#        Status: Executing Task...
#     └── 🤖 Agent: Python Developer

#             Status: In Progress

# # Agent: Python Developer
# ## Task: Write python code to achieve this: Write a python program to calculate the first 10,000 terms of this series, multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ...

# 🤖 Agent: Python Developer

#     Status: In Progress
# └── 🧠 Thinking...

# 🤖 Agent: Python Developer

#     Status: In Progress

# 🤖 Agent: Python Developer

#     Status: In Progress

#  Running code in Docker environment


# # Agent: Python Developer
# ## Thought: The user wants to calculate the first 10,000 terms of the series 1 - 1/3 + 1/5 - 1/7 + ... and then multiply the sum by 4. I need to write a Python program to do this.
# Here's the plan:
# 1. Initialize a variable `total_sum` to 0.
# 2. Initialize a variable `denominator` to 1.
# 3. Initialize a variable `sign` to 1 (for the first term).
# 4. Loop 10,000 times. In each iteration:
#     a. Calculate the current term: `sign / denominator`.
#     b. Add the current term to `total_sum`.
#     c. Update the `denominator` by adding 2.
#     d. Update the `sign` by multiplying it by -1.
# 5. After the loop, multiply `total_sum` by 4.
# 6. Print the final result.
# I will use the Code Interpreter tool for this.
# python
# total_sum = 0
# denominator = 1
# sign = 1
# for _ in range(10000):
#     term = sign / denominator
#     total_sum += term
#     denominator += 2
#     sign *= -1
# final_result = total_sum * 4
# print(f"The result of the series is: {final_result}")
# Now I need to execute this code using the Code Interpreter.
# ## Using tool: Code Interpreter
# ## Tool Input:
# "{\"code\": \"total_sum = 0\\ndenominator = 1\\nsign = 1\\n\\nfor _ in range(10000):\\n    term = sign / denominator\\n    total_sum += term\\n    denominator += 2\\n    sign *= -1\\n\\nfinal_result = total_sum * 4\\nprint(f\\\"The result of the series is: {final_result}\\\")\", \"libraries_used\": []}"
# ## Tool Output:
# The result of the series is: 3.1414926535900345

# 🤖 Agent: Python Developer

#     Status: In Progress
# └── 🧠 Thinking...

# 🤖 Agent: Python Developer

#     Status: In Progress



# # Agent: Python Developer
# ## Final Answer:
# The result of the series is: 3.1414926535900345


# 🚀 Crew: crew
# └── 📋 Task: 3620e008-d22e-4e92-901a-a40c177a47c3
#        Status: Executing Task...
#     └── 🤖 Agent: Python Developer

#             Status: ✅ Completed

# 🚀 Crew: crew
# └── 📋 Task: 3620e008-d22e-4e92-901a-a40c177a47c3
#        Assigned to: Python Developer

#        Status: ✅ Completed
#     └── 🤖 Agent: Python Developer

#             Status: ✅ Completed
# ╭─────────────────────────────────────────────────────────────────────────────────────────────── Task Completion ───────────────────────────────────────────────────────────────────────────────────────────────╮
# │                                                                                                                                                                                                               │
# │  Task Completed                                                                                                                                                                                               │
# │  Name: 3620e008-d22e-4e92-901a-a40c177a47c3                                                                                                                                                                   │
# │  Agent: Python Developer                                                                                                                                                                                      │
# │                                                                                                                                                                                                               │
# │                                                                                                                                                                                                               │
# │                                                                                                                                                                                                               │
# ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

# ╭─────────────────────────────────────────────────────────────────────────────────────────────── Crew Completion ───────────────────────────────────────────────────────────────────────────────────────────────╮
# │                                                                                                                                                                                                               │
# │  Crew Execution Completed                                                                                                                                                                                     │
# │  Name: crew                                                                                                                                                                                                   │
# │  ID: 3dfdad79-b5e1-40fc-a5aa-9364e8aa916e                                                                                                                                                                     │
# │                                                                                                                                                                                                               │
# │                                                                                                                                                                                                               │
# ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

# The result of the series is: 3.1414926535900345
