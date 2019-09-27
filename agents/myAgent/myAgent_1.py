from queue import Queue
from absl import app

import pysc2.agents.myAgent.macro_operation as macro_operation

from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions
from pysc2.lib import features
import pysc2.agents.myAgent.smart_actions as sa
import pysc2.agents.myAgent.q_learing_table as q_learing_table
import matplotlib.pyplot as plt
import numpy as np

_NO_OP = actions.FUNCTIONS.no_op.id
_NOT_QUEUED = [0]
_QUEUED = [1]

KILL_UNIT_REWARD = 0.2
KILL_BUILDING_REWARD = 0.5


class myAgent(base_agent.BaseAgent):

    def __init__(self):
        super(myAgent, self).__init__()

        # 宏操作的大队列
        self.macroOpQueue = Queue()

        # 宏操作中原子的小队列
        self.tempMarcoOp = None

        self.tempMarcoOp_step = 0

        self.qlearn = q_learing_table.QLearningTable(actions=list(range(len(sa.smart_actions))))

        self.previous_killed_unit_score = 0
        self.previous_killed_building_score = 0

        self.previous_action = None
        self.previous_state = None

        self.figureData = []

    def inQueue(self, functionNumber):

        self.macroOpQueue.put(functionNumber)

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
        current_state = q_learing_table.currentState(obs).getData()

        killed_unit_score = obs.observation['score_cumulative'][5]
        killed_building_score = obs.observation['score_cumulative'][6]

        self.figureData.append([self.steps, killed_unit_score, killed_building_score])
        # plt.plot(self.steps, killed_unit_score, label='killed_unit_score', linewidth=1, color='g')
        # plt.plot(self.steps, killed_building_score, label='killed_building_score', linewidth=1, color='r')

        if self.previous_action is not None:
            reward = 0

            if killed_unit_score > self.previous_killed_unit_score:
                reward += KILL_UNIT_REWARD

            if killed_building_score > self.previous_killed_building_score:
                reward += KILL_BUILDING_REWARD

            self.qlearn.learn(str(self.previous_state), self.previous_action, reward, str(current_state))
        rl_action = self.qlearn.choose_action(str(current_state))
        self.inQueue(rl_action)

        self.previous_killed_unit_score = killed_unit_score
        self.previous_killed_building_score = killed_building_score
        self.previous_state = current_state
        self.previous_action = rl_action

        f = self.opperation(obs)

        return f


def main(unused_argv):
    agent = myAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="Flat96",
                    players=[sc2_env.Agent(race=sc2_env.Race.terran, name='agent'),
                             sc2_env.Bot(sc2_env.Race.random,
                                         sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=macro_operation.screenSize,
                                                               minimap=macro_operation.minimapSize),
                        camera_width_world_units=macro_operation.screenSize,
                        use_unit_counts=True,

                    ),

                    step_mul=0.000000001,
                    game_steps_per_episode=0,
                    realtime=True,
                    visualize=False,

            ) as env:

                agent.setup(env.observation_spec(), env.action_spec())
                timesteps = env.reset()
                agent.reset()

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        agent.figureData = np.array(agent.figureData)
                        plt.plot(agent.figureData[:, 0], agent.figureData[:, 1])
                        plt.plot(agent.figureData[:, 0], agent.figureData[:, 2])

                        plt.show()

                        break
                    timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)

# def main(unused_argv):
#     agent1 = myAgent()
#     agent2 = myAgent()
#     try:
#         while True:
#             with sc2_env.SC2Env(
#                     map_name="Flat96",
#                     players=[sc2_env.Agent(race=sc2_env.Race.terran, name='agent1'),
#                              sc2_env.Agent(race=sc2_env.Race.terran, name='agent2')],
#                     agent_interface_format=features.AgentInterfaceFormat(
#                         feature_dimensions=features.Dimensions(screen=macro_operation.screenSize,
#                                                                minimap=macro_operation.minimapSize),
#                         camera_width_world_units=macro_operation.screenSize,
#                         use_unit_counts=True,
#
#                     ),
#
#                     step_mul=8,
#                     game_steps_per_episode=0,
#                     realtime=False,
#                     visualize=False,
#
#             ) as env:
#
#                 agent1.setup(env.observation_spec(), env.action_spec())
#                 agent2.setup(env.observation_spec(), env.action_spec())
#                 timesteps = env.reset()
#                 agent1.reset()
#                 agent2.reset()
#
#                 while True:
#                     step_actions = [agent1.step(timesteps[0]),
#                                     agent2.step(timesteps[1])]
#                     # if timesteps[0].last():
#                     #     agent1.figureData = np.array(agent1.figureData)
#                     #     plt.plot(agent1.figureData[:, 0], agent1.figureData[:, 1])
#                     #     plt.plot(agent1.figureData[:, 0], agent1.figureData[:, 2])
#                     #
#                     #     agent2.figureData = np.array(agent2.figureData)
#                     #     plt.plot(agent2.figureData[:, 0], agent2.figureData[:, 1])
#                     #     plt.plot(agent2.figureData[:, 0], agent2.figureData[:, 2])
#                     #
#                     #     plt.show()
#                     #
#                     #     break
#                     timesteps = env.step(step_actions)
#
#     except KeyboardInterrupt:
#         pass
#
#
# if __name__ == "__main__":
#     app.run(main)
