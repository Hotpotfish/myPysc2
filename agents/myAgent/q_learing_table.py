import pandas as pd
import numpy as np
import pysc2.lib.units as units

KILL_UNIT_REWARD = 0.2
KILL_BUILDING_REWARD = 0.5


def unitCount(obs, unitId):
    unit_counts = np.array(obs.observation['unit_counts'])

    unitCount = [uc for uc in unit_counts if uc[0] == int(unitId)]

    if not len(unitCount):
        return 0
    else:
        return unitCount[0][1]


class currentState:
    def __init__(self, obs):
        self.data = [obs.observation['player'].minerals,
                     obs.observation['player'].vespene,
                     obs.observation['player'].food_cap,
                     obs.observation['player'].food_used,
                     obs.observation['player'].food_workers,
                     obs.observation['player'].idle_worker_count,
                     obs.observation['player'].army_count,
                     unitCount(obs, units.Terran.SupplyDepot),
                     unitCount(obs, units.Terran.Barracks)
                     ]

    def getData(self):
        return self.data


class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=np.arange(0, len(actions)), dtype=np.float64)

    def choose_action(self, state):

        self.check_state_exist(state)

        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.ix[state, :]

            # some actions have the same value
            state_action = state_action.reindex(np.random.permutation(state_action.index))

            action = state_action.idxmax()
        else:
            # choose random action
            action = np.random.choice(self.actions)

        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        self.check_state_exist(s)

        q_predict = self.q_table.ix[s, a]
        q_target = r + self.gamma * self.q_table.ix[s_, :].max()

        # update
        self.q_table.ix[s, a] += self.lr * (q_target - q_predict)

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series([0] * len(self.actions), index=self.q_table.columns, name=state))
