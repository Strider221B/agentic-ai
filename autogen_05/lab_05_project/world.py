import asyncio
from dotenv import load_dotenv

from autogen_core import AgentId
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime

load_dotenv(override=True)

import autogen_05.lab_05_project.messages as messages
from autogen_05.lab_05_project.agent import Agent
from autogen_05.lab_05_project.creator import Creator
from autogen_05.lab_05_project.lab_constants import LabConstants

class World:

    _HOW_MANY_AGENTS = 5

    @classmethod
    async def main(cls):
        host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
        host.start()
        worker = GrpcWorkerAgentRuntime(host_address="localhost:50051")
        await worker.start()
        result = await Creator.register(worker, "Creator", lambda: Creator("Creator"))
        creator_id = AgentId("Creator", "default")
        coroutines = [cls._create_and_message(worker, creator_id, i) for i in range(1, cls._HOW_MANY_AGENTS+1)]
        await asyncio.gather(*coroutines)
        try:
            await worker.stop()
            await host.stop()
        except Exception as e:
            print(e)

    @staticmethod
    async def _create_and_message(worker, creator_id, i: int):
        try:
            result = await worker.send_message(messages.Message(content=f"agent{i}.py"), creator_id)
            with open(f"{LabConstants.PATH}/idea{i}.md", "w") as f:
                f.write(result.content)
        except Exception as e:
            print(f"Failed to run worker {i} due to exception: {e}")

if __name__ == "__main__":
    asyncio.run(World.main())

# Output:
# ** Creator has created python code for agent agent3 - about to register with Runtime
# ** Agent agent3 is live
# INFO:autogen_core.trace:** Agent agent3 is live
# agent3: Received message
# ** Creator has created python code for agent agent4 - about to register with Runtime
# ** Creator has created python code for agent agent1 - about to register with Runtime
# Failed to run worker 1 due to exception: No module named 'agent1'
# ** Agent agent4 is live
# INFO:autogen_core.trace:** Agent agent4 is live
# agent4: Received message
# ** Creator has created python code for agent agent5 - about to register with Runtime
# ** Agent agent5 is live
# INFO:autogen_core.trace:** Agent agent5 is live
# agent5: Received message
# ** Creator has created python code for agent agent2 - about to register with Runtime
# ** Agent agent2 is live
# INFO:autogen_core.trace:** Agent agent2 is live
# agent2: Received message
# Selecting agent for refinement: agent5
# agent5: Received message
# Selecting agent for refinement: agent3
# agent3: Received message
# Selecting agent for refinement: agent4
# agent4: Received message
# Selecting agent for refinement: agent5
# agent5: Received message
# Selecting agent for refinement: agent4
# agent4: Received message
