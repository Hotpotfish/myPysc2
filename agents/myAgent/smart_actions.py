import pysc2.agents.myAgent.macro_operation as mc

smart_actions = {
    0: [mc.svcBackToWork, 2],
    1: [mc.chooseARandomScv, 1],
    2: [mc.buildBarracks, 2],
    3: [mc.buildSupplydepot, 2],
    4: [mc.trainMarines, 2],
    5: [mc.attack, 2],
    6: [mc.trainSCVs, 2],
}
