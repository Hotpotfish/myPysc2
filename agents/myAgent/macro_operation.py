import random
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib import units
from queue import Queue
import numpy as np

_NOT_QUEUED = [0]
_QUEUED = [1]

screenSize = 256
minimapSize = 64


def ownMineralFields(MineralFields, CommandCenter):
    # if len(CommandCenter) and len(MineralFields):
    #     MineralFields = np.array(MineralFields)[:, 12:14]
    #     CommandCenter = np.array(CommandCenter)[:, 12:14]
    #     for i in range(0, len(CommandCenter)):
    #         Command = CommandCenter[i]
    #         for j in range(0, len(MineralFields[0])):
    #             Mineral = MineralFields[j]
    #
    #             if np.sqrt(np.sum(np.square(Command - Mineral))) <= 20:
    #                 return Mineral
    #
    # else:
    #
    #     return None
    if len(CommandCenter) and len(MineralFields):
        MineralFields = np.array(MineralFields)
        CommandCenter = np.array(CommandCenter)
        for i in range(0, len(CommandCenter)):
            Command = np.array([CommandCenter[i].x, CommandCenter[i].y])
            for j in range(0, len(MineralFields)):
                Mineral = np.array([MineralFields[j].x, MineralFields[j].y])

                if np.sqrt(np.sum(np.square(Command - Mineral))) <= 20:
                    return Mineral

    else:

        return None


def findAnyEnemies(obs):
    enemy_y, enemy_x = (obs.observation['feature_screen'][
                            features.SCREEN_FEATURES.player_relative.index] == features.PlayerRelative.ENEMY).nonzero()
    enemies = list(zip(enemy_x, enemy_y))

    if enemies:
        target = enemies[np.argmax(np.array(enemies)[:, 1])]
        return target

    else:

        return None
    # feature_units = obs.observation['feature_units']
    # enemies = []
    #
    # for i in range(0, len(feature_units)):
    #     if feature_units[i][1] == features.PlayerRelative.ENEMY:
    #         enemies.append(feature_units[i])
    #
    # if enemies:
    #     ran = random.randint(0, len(enemies) - 1)
    #
    #     enemy = enemies[ran]
    #
    #     return [enemy.x, enemy.y]
    #
    # else:
    #     return None


def needFood(obs):
    if obs.observation['player'][4] != 200 and obs.observation['player'][4] - obs.observation['player'][3] <= 0:
        return buildSupplydepot(obs)
    else:
        return None


def chooseARandomPlace(input_x, input_y):
    add_y = random.randint(-10, 10)
    add_x = random.randint(-10, 10)

    if input_x + add_x >= screenSize:

        outx = screenSize

    elif input_x + add_x < 0:
        outx = 0

    else:
        outx = input_x + add_x

    if input_y + add_y >= screenSize:

        outy = screenSize

    elif input_y + add_y < 0:
        outy = 0

    else:
        outy = input_y + add_y

    return [outx, outy]


def searchUnitScreen(obs, unitType, alliance):
    # feature_units = obs.observation['feature_units']
    # examples = []
    #
    # for i in range(0, len(feature_units)):
    #     if feature_units[i][0] == int(unitType) and feature_units[i][1] == alliance:
    #         examples.append(feature_units[i])
    #
    # return examples
    class point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    feature_screen = obs.observation['feature_screen']
    examples = []

    units_y, units_x = (feature_screen[features.SCREEN_FEATURES.unit_type.index] == int(unitType)).nonzero()

    if units_y is not None:
        for i in range(0, len(units_y)):
            if feature_screen[features.SCREEN_FEATURES.player_relative.index][units_y[i]][units_x[i]] == alliance:
                examples.append(point(units_x[i], units_y[i]))

    if examples is not None:
        return examples
    else:
        return None


def noOP():
    actionQueue = Queue()
    actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.no_op.id, []))
    return actionQueue


def svcBackToWork(obs, step):
    # print('svcBackToWork')

    MineralFields = searchUnitScreen(obs, units.Neutral.MineralField, 3)
    MineralField750s = searchUnitScreen(obs, units.Neutral.MineralField750, 3)
    CommandCenter = searchUnitScreen(obs, units.Terran.CommandCenter, 1)

    if obs.observation['player'][7] != 0 and (len(MineralFields) or len(MineralField750s)):
        # 2代表选择所有空闲工人
        if step == 0:
            return actions.FunctionCall(actions.FUNCTIONS.select_idle_worker.id, [[2]])

        if step == 1:

            if MineralFields is not None:
                target = ownMineralFields(MineralFields, CommandCenter)
                if target is not None:
                    # ran = random.randint(0, len(MineralFields) - 1)
                    # target = [MineralFields[ran].x, MineralFields[ran].y]
                    return actions.FunctionCall(actions.FUNCTIONS.Harvest_Gather_screen.id, [_QUEUED, target])

            if MineralField750s is not None:
                target = ownMineralFields(MineralField750s, CommandCenter)
                if target is not None:
                    # ran = random.randint(0, len(MineralField750s) - 1)
                    # target = [MineralField750s[ran].x, MineralField750s[ran].y]
                    return actions.FunctionCall(actions.FUNCTIONS.Harvest_Gather_screen.id, [_QUEUED, target])

        else:
            return None




    else:

        return None


def moveCarmeraToPlayerSelf_atomicOp(obs):
    playerRelative = obs.observation['feature_minimap'][features.MINIMAP_FEATURES.player_relative.index]
    pr_y, pr_x = (playerRelative == features.PlayerRelative.SELF).nonzero()

    ran = random.randint(0, len(pr_y) - 1)

    target = [pr_x[ran], pr_y[ran]]

    return actions.FunctionCall(actions.FUNCTIONS.move_camera.id, [target])


def chooseARandomScv_atomicOp(obs):
    # 找寻空闲工人
    # print('chooseARandomScv_atomicOp')
    if obs.observation['player'][7] != 0:
        return actions.FunctionCall(actions.FUNCTIONS.select_idle_worker.id, [[0]])

    SCVs = searchUnitScreen(obs, units.Terran.SCV, 1)

    if SCVs is not None:
        ran = random.randint(0, len(SCVs) - 1)
        target = [SCVs[ran].x, SCVs[ran].y]

        return actions.FunctionCall(actions.FUNCTIONS.select_point.id, [[0], target])

    return None


def chooseARandomScv(obs, step):
    # actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    SCVs = searchUnitScreen(obs, units.Terran.SCV, 1)

    if len(SCVs):
        i = random.randint(0, len(SCVs) - 1)
        target = [SCVs[i].x, SCVs[i].y]
        if step == 0:
            # 这里的0代表选择一个的意思
            return actions.FunctionCall(actions.FUNCTIONS.select_point.id, [[0], target])
    return None


def buildBarracks(obs, step):
    # print('buildBarracks')

    # actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    if not chooseARandomScv_atomicOp(obs):
        return None

    if step == 0:
        return chooseARandomScv_atomicOp(obs)

    supplyDepots = searchUnitScreen(obs, units.Terran.SupplyDepot, 1)
    #Barracks = searchUnitScreen(obs, units.Terran.Barracks, 1)

    if step == 1:

        if len(supplyDepots) :
            seed = random.randint(0, len(supplyDepots) - 1)
            target = chooseARandomPlace(supplyDepots[seed].x, supplyDepots[seed].y)
            return actions.FunctionCall(actions.FUNCTIONS.Build_Barracks_screen.id, [_QUEUED, target])

    return None


def buildSupplydepot(obs, step):
    # print('buildSupplydepot')

    # actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    if not chooseARandomScv_atomicOp(obs):
        return None
    if step == 0:
        return chooseARandomScv_atomicOp(obs)

    if step == 1:

        commandCenters = searchUnitScreen(obs, units.Terran.CommandCenter, 1)

        if len(commandCenters):
            seed = random.randint(0, len(commandCenters) - 1)
            target = chooseARandomPlace(commandCenters[seed].x, commandCenters[seed].y)
            return actions.FunctionCall(actions.FUNCTIONS.Build_SupplyDepot_screen.id, [_QUEUED, target])

    return None


def trainMarines(obs, step):
    # print('trainMarines')

    # 将摄像机随机移动到有己方单位的地方
    # actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    Barracks = searchUnitScreen(obs, units.Terran.Barracks, 1)
    # 找寻是否当前选择的地方有己方兵营
    if len(Barracks):
        ran = random.randint(0, len(Barracks) - 1)
        target = [Barracks[ran].x, Barracks[ran].y]

        if step == 0:
            return actions.FunctionCall(actions.FUNCTIONS.select_point.id, [[2], target])

        if step == 1:
            return actions.FunctionCall(actions.FUNCTIONS.Train_Marine_quick.id, [_NOT_QUEUED])

    else:

        return None


def trainSCVs(obs, step):
    # print('trainSCVs')

    # 将摄像机随机移动到有己方单位的地方
    # actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    CommandCenter = searchUnitScreen(obs, units.Terran.CommandCenter, 1)
    SCVs = searchUnitScreen(obs, units.Terran.SCV, 1)

    if len(CommandCenter) and len(SCVs) < 16:
        ran = random.randint(0, len(CommandCenter) - 1)
        target = [CommandCenter[ran].x, CommandCenter[ran].y]
        if step == 0:
            return actions.FunctionCall(actions.FUNCTIONS.select_point.id, [[2], target])

        if step == 1:
            return actions.FunctionCall(actions.FUNCTIONS.Train_SCV_quick.id, [_NOT_QUEUED])


    else:
        return None


def attack(obs, step):
    # 将摄像机随机移动到有己方单位的地方
    # actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    if obs.observation['player'][8] > 0:
        if findAnyEnemies(obs):
            target = findAnyEnemies(obs)
            if step == 0:
                return actions.FunctionCall(actions.FUNCTIONS.select_army.id, [[0]])
            if step == 1:
                return actions.FunctionCall(actions.FUNCTIONS.Attack_screen.id, [_NOT_QUEUED, target])
            # actionQueue.put(actions.FUNCTIONS.Attack_screen("now", target))
        else:
            # print('attackRandom')
            random_x = random.randint(0, screenSize - 1)
            random_y = random.randint(0, screenSize - 1)
            target = [random_x, random_y]
            if step == 0:
                return actions.FunctionCall(actions.FUNCTIONS.select_army.id, [[0]])
            if step == 1:
                return actions.FunctionCall(actions.FUNCTIONS.Move_screen.id, [_QUEUED, target])

    return None
