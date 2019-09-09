import pysc2.agents.myAgent.macro_operation as mc

smart_actions = {
    1: [mc.svcBackToWork, 2],
    2: [mc.chooseARandomScv, 1],
    3: [mc.buildBarracks, 2],
    4: [mc.buildSupplydepot, 2],
    5: [mc.trainMarines, 2],
    6: [mc.attack, 2],
}
