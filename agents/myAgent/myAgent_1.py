from queue import Queue
from absl import app

import pysc2.agents.myAgent.macro_operation as macro_operation

from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions
from pysc2.lib import features
import pysc2.agents.myAgent.smart_actions as sa

_NO_OP = actions.FUNCTIONS.no_op.id
_NOT_QUEUED = [0]
_QUEUED = [1]


class myAgent(base_agent.BaseAgent):

    def __init__(self):
        super(myAgent, self).__init__()

        # 宏操作的大队列
        self.macroOpQueue = Queue()

        # 宏操作中原子的小队列
        self.tempMarcoOp = None

        self.tempMarcoOp_step = 0

    def inQueue(self, funtionNumber):

        self.macroOpQueue.put(funtionNumber)

        return 0

    def opperation(self, obs):

        # 宏操作队列判空
        if self.macroOpQueue.empty() and self.tempMarcoOp is None:
            return actions.FunctionCall(_NO_OP, [])

        if self.tempMarcoOp is None:
            self.tempMarcoOp = self.macroOpQueue.get()

        if self.tempMarcoOp_step < sa.smart_actions[self.tempMarcoOp][1]:

            atomicOp = sa.smart_actions[self.tempMarcoOp][0](obs, self.tempMarcoOp_step)

            if atomicOp is not None and int(atomicOp[0]) in obs.observation['available_actions']:

                self.tempMarcoOp_step += 1

                return atomicOp


        self.tempMarcoOp = None

        self.tempMarcoOp_step = 0

        return actions.FunctionCall(_NO_OP, [])

    def step(self, obs):
        super(myAgent, self).step(obs)

        # self.inQueue(macro_operation.chooseARandomScv(obs))

        # self.inQueue(macro_operation.buildSupplydepot(obs))

        # self.inQueue(macro_operation.buildBarracks(obs))

        # self.inQueue(macro_operation.trainMarines(obs))
        self.inQueue(6)
        # self.inQueue(macro_operation.trainSCVs(obs))
        # self.inQueue(macro_operation.attackRandom(obs))
        f = self.opperation(obs)
        # print(f)

        return f


def main(unused_argv):
    agent = myAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="FindAndDefeatZerglings",
                    players=[sc2_env.Agent(race=sc2_env.Race.terran, name='agent'),],
                    # sc2_env.Bot(sc2_env.Race.random,
                    #             sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=macro_operation.screenSize,
                                                               minimap=macro_operation.minimapSize),
                        camera_width_world_units=macro_operation.screenSize,

                    ),
                    step_mul=4,
                    game_steps_per_episode=0,
                    realtime=True,
                    visualize=False,

            ) as env:

                agent.setup(env.observation_spec(), env.action_spec())
                timesteps = env.reset()
                agent.reset()

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    # if timesteps[0].last():
                    #     break
                    timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)
