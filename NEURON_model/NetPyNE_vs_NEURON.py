from Na12HMMModel_TF import Na12Model_TF
import matplotlib.pyplot as plt
import json
from netpyne import specs, sim

netParams = specs.NetParams()   # object of class NetParams to store the network parameters
cfg = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

###############################################################################
# NETWORK PARAMETERS
###############################################################################

stim_amp = [0, 0.1, 0.2, 0.3, 0.4, 0.5]

# Cell parameters
## PT cell properties
fptr = open("Na1216TF.json", "r")
PTcell = json.load(fptr)
fptr.close()

PTcell['conds'] = {'cellType': 'PT'}

netParams.cellParams['PT5B_full'] = PTcell
# Population parameters
netParams.popParams['PT5B_full'] = {'cellType': 'PT', 'numCells': 1} # add dict with params for this pop
netParams.renameCellParamsSec(label='PT5B_full', oldSec ='soma_0', newSec ='soma')
netParams.defaultThreshold = 0.

###############################################################################
# SIMULATION PARAMETERS
###############################################################################

cfg.duration = 800
cfg.dt = 0.025
cfg.verbose = False
cfg.hParams = {'celsius': 34, 'v_init': -72} #changed from -65
cfg.recordTraces = {'v': {'sec':'soma', 'loc':0.5, 'var':'v'}} # Dict with traces to record
cfg.recordStep = 0.05  # Step size in ms to save data
cfg.saveJson = True
cfg.printPopAvgRates = True
cfg.analysis['plotTraces'] = {'include': [0], 'saveFig': False}  # Plot recorded traces for this list of cells

cfg.saveDataInclude = ['simData'] #['simData', 'simConfig', 'netParams', 'net']

for i in range(len(stim_amp)):
    # add stim source
    netParams.stimSourceParams['ic'] = {'type': 'IClamp', 'delay': 100, 'dur': 500, 'amp': stim_amp[i]}
    # connect stim source to target
    netParams.stimTargetParams['ic->PT'] = {'source': 'ic', 'conds': {'pop': 'PT5B_full'}, 'sec': 'soma', 'loc': 0.5}

    cfg.filename = 'SingleCellSims/PT_'+ str(stim_amp[i])

    # Create network and run simulation
    sim.initialize( simConfig = cfg, netParams = netParams)

    # Create network and run simulation
    sim.createSimulateAnalyze(netParams=netParams, simConfig=cfg)



  
fig, axs = plt.subplots(2, len(stim_amp))
for i in range(len(stim_amp)):
    newClass = Na12Model_TF()
    newClass.plot_stim(stim_amp = stim_amp[i], axs=axs[0,i])
    with open("SingleCellSims/PT_" + str(stim_amp[i]) + "_data.json", "r") as fptr:
        SimData = json.load(fptr)
        v = SimData["simData"]["v"]["cell_0"]
        t = SimData["simData"]["t"]
    axs[1,i].plot(t,v,'k', linewidth=0.5)
    #axs[0,i].set_ylim([-80, 10])    
    #axs[1,i].set_ylim([-80, 10])
 
[axs[i,j].axis('off') for i in range(2) for j in range(len(stim_amp))]
plt.tight_layout()
plt.savefig("Comparison.png")
