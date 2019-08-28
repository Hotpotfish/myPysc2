import random
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib import units
from queue import Queue

_NOT_QUEUED = [0]
_QUEUED = [1]


def chooseARandomPlace(input_x, input_y):
    add_y = random.randint(-20, 20)
    add_x = random.randint(-20, 20)

    if input_x + add_x >= 64:

        outx = 64

    elif input_x + add_x < 0:
        outx = 0

    else:
        outx = input_x + add_x

    if input_y + add_y >= 64:

        outy = 64

    elif input_y + add_y < 0:
        outy = 0

    else:
        outy = input_y + add_y

    return [outx, outy]


def noOP():
    actionQueue = Queue()
    actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.no_op.id, []))
    return actionQueue


def svcBackToWork(obs):
    actionQueue = Queue()
    if obs.observation['player'][7] != 0:
        # 3代表选择所有空闲工人
        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.select_idle_worker.id, [[3]]))

        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.Harvest_Return_quick.id, [_NOT_QUEUED]))

        return actionQueue
    else:
        return None


def moveCarmeraToPlayerSelf_atomicOp(obs):
    playerRelative = obs.observation['feature_minimap'][features.MINIMAP_FEATURES.player_relative.index]
    pr_y, pr_x = (playerRelative == features.PlayerRelative.SELF).nonzero()

    ran = random.randint(0, len(pr_y) - 1)

    target = [pr_x[ran], pr_y[ran]]

    return actions.FunctionCall(actions.FUNCTIONS.move_camera.id, [target])


def chooseARandomScv_atomicOp(obs):
    # 辅助镜头移动
    # unit_type = obs.observation['feature_minimap'][features.MINIMAP_FEATURES.player_relative.index]

    unit_type = obs.observation['feature_screen'][features.SCREEN_FEATURES.unit_type.index]
    unit_y, unit_x = (unit_type == units.Terran.SCV).nonzero()

    if unit_y.any():
        i = random.randint(0, len(unit_y) - 1)
        target = [unit_x[i], unit_y[i]]

        return actions.FunctionCall(actions.FUNCTIONS.select_point.id, [_NOT_QUEUED, target])

    return None


def chooseARandomScv(obs):
    actionQueue = Queue()

    actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    unit_type = obs.observation['feature_screen'][features.SCREEN_FEATURES.unit_type.index]

    unit_y, unit_x = (unit_type == units.Terran.SCV).nonzero()

    if unit_y.any():
        i = random.randint(0, len(unit_y) - 1)
        target = [unit_x[i], unit_y[i]]
        # 这里的0代表选择一个的意思
        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.select_point.id, [[0], target]))

        return actionQueue

    return None


def buildBarracks(obs):
    actionQueue = Queue()

    actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    if not chooseARandomScv_atomicOp(obs):
        return None

    actionQueue.put(chooseARandomScv_atomicOp(obs))

    unit_type = obs.observation['feature_screen'][features.SCREEN_FEATURES.unit_type.index]
    unit_y, unit_x = (unit_type == units.Terran.SupplyDepot).nonzero()

    if unit_y.any():
        target = chooseARandomPlace(unit_x[0], unit_y[0])
        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.Build_Barracks_screen.id,
                                             [_NOT_QUEUED, target]))

        return actionQueue

    return None


def buildSupplydepot(obs):
    actionQueue = Queue()
    actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    if not chooseARandomScv_atomicOp(obs):
        return None
    actionQueue.put(chooseARandomScv_atomicOp(obs))

    unit_type = obs.observation['feature_screen'][features.SCREEN_FEATURES.unit_type.index]
    unit_y, unit_x = (unit_type == units.Terran.CommandCenter).nonzero()

    if unit_y.any():
        target = chooseARandomPlace(int(unit_x.mean()), int(unit_y.mean()))
        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.Build_SupplyDepot_screen.id,
                                             [_NOT_QUEUED, target]))
        return actionQueue

    return None


def trainMarines(obs):
    actionQueue = Queue()
    # 将摄像机随机移动到有己方单位的地方
    actionQueue.put(moveCarmeraToPlayerSelf_atomicOp(obs))

    # # 3代表选择所有该类型
    # actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.select_unit.id, [[0], [int(units.Terran.Barracks)]]))
    # actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.Train_Marine_quick.id, [_NOT_QUEUED]))
    # return actionQueue

    unit_type = obs.observation['feature_screen'][features.SCREEN_FEATURES.unit_type.index]
    unit_y, unit_x = (unit_type == units.Terran.Barracks).nonzero()
    # 找寻是否当前选择的地方有己方兵营
    if unit_y.any():
        ran = random.randint(0, len(unit_y) - 1)
        target = [unit_x[ran], unit_y[ran]]

        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.select_point.id, [[0], target]))

        actionQueue.put(actions.FunctionCall(actions.FUNCTIONS.Train_Marine_quick.id, [_NOT_QUEUED]))
        return actionQueue

    else:
        return buildBarracks(obs)
