import random
import math
from queue import Queue
from absl import app

import pysc2.agents.myAgent.macro_operation as macro_operation

from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions
from pysc2.lib import features

_NO_OP = actions.FUNCTIONS.no_op.id
_NOT_QUEUED = [0]
_QUEUED = [1]


class myAgent(base_agent.BaseAgent):

    def __init__(self):
        super(myAgent, self).__init__()

        # 宏操作的大队列
        self.macroOpQueue = Queue()

        # 宏操作中原子的小队列
        self.tempMarcoOp = Queue()

    def inQueue(self, actionQueue):

        # 空操作跳过
        if not actionQueue:
            return -1

        self.macroOpQueue.put(actionQueue)

        return 0

    def opperation(self, obs):

        # 宏操作队列判空
        if self.macroOpQueue.empty() and self.tempMarcoOp.empty():
            return actions.FunctionCall(_NO_OP, [])

        if self.tempMarcoOp.empty():
            self.tempMarcoOp = self.macroOpQueue.get()

        atomicOp = self.tempMarcoOp.get()

        if int(atomicOp[0]) in obs.observation['available_actions']:

            return atomicOp

        else:

            self.tempMarcoOp.queue.clear()

            return actions.FunctionCall(_NO_OP, [])

    def step(self, obs):
        super(myAgent, self).step(obs)

        self.inQueue(macro_operation.chooseARandomScv(obs))

        self.inQueue(macro_operation.buildSupplydepot(obs))
        #
        self.inQueue(macro_operation.buildBarracks(obs))
        #
        self.inQueue(macro_operation.trainMarines(obs))
        self.inQueue(macro_operation.svcBackToWork(obs))
        self.inQueue(macro_operation.trainSCVs(obs))
        # self.inQueue(macro_operation.attackRandom(obs))
        f = self.opperation(obs)
        print(f)

        return f


def main(unused_argv):
    agent1 = myAgent()
    agent2 = myAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="Simple96",

                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Agent(sc2_env.Race.terran)],
                             # sc2_env.Bot(sc2_env.Race.random,
                             #             sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=84, minimap=64),
                        use_feature_units=True),

                    step_mul=8,
                    game_steps_per_episode=0,
                    realtime=False,
                    visualize=True) as env:

                agent1.setup(env.observation_spec(), env.action_spec())
                agent2.setup(env.observation_spec(), env.action_spec())

                timesteps = env.reset()
                agent1.reset()
                agent2.reset()

                while True:
                    step_actions = [agent1.step(timesteps[0]),
                                    agent2.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)
