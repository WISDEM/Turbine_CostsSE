"""
turbinecost.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
import numpy as np

from fusedwind.plant_cost.fused_tcc_asym import FullTurbineCapitalCostModel, FullTCCAggregator

from Rotor_CostsSE import Rotor_CostsSE
from Nacelle_CostsSE import Nacelle_CostsSE
from Tower_CostsSE import Tower_CostsSE

#-------------------------------------------------------------------------------        

class Turbine_CostsSE(FullTurbineCapitalCostModel):

    '''
    Initial computation of the costs for the wind turbine.

    Parameters
    ----------
    bladeMass : float
      blade mass [kg]
    hubMass : float
      hub mass [kg]
    pitchSystemMass : float
      pitch system mass [kg]
    spinnerMass : float
      spinner mass [kg]
    lowSpeedShaftMass : float
      Low speed shaft mass [kg]
    mainBearingsMass : float
      bearing mass [kg]
    secondBearingsMass : float
      bearing mass [kg]
    gearboxMass : float
      Gearbox mass [kg]
    highSpeedSideMass : float
      High speed side mass [kg]
    bedplateMass : float
      Bedplate mass [kg]
    yawSystemMass : float
      Yaw system mass [kg]
    towerMass : float
      mass [kg] of the wind turbine tower
    machineRating : float
      Machine rating for turbine [kW]
    bladeNumber : int
      Number of blades on rotor
    advanced : bool
      boolean for advanced (using carbon) or basline (all fiberglass) blade
    drivetrainDesign : int
      machine configuration 1 conventional, 2 medium speed, 3 multi-gen, 4 direct-drive
    offshore : bool
      boolean true if it is offshore
    crane : bool
        boolean for crane present on-board
    curr_yr : int
      Project start year
    curr_mon : int
      Project start month
      
    Returns
    -------
    cost : float
      overall turbine cost [USD]        
    '''

    # variables
    bladeMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hubMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitchSystemMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinnerMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    lowSpeedShaftMass = Float(iotype='in', units='kg', desc='component mass')
    mainBearingMass = Float(iotype='in', units='kg', desc='component mass')
    secondBearingMass = Float(iotype='in', units='kg', desc='component mass')
    gearboxMass = Float(iotype='in', units='kg', desc='component mass')
    highSpeedSideMass = Float(iotype='in', units='kg', desc='component mass')
    generatorMass = Float(iotype='in', units='kg', desc='component mass')
    bedplateMass = Float(iotype='in', units='kg', desc='component mass')
    yawSystemMass = Float(iotype='in', units='kg', desc='component mass')
    towerMass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    machineRating = Float(iotype='in', units='kW', desc='machine rating')
    
    # parameters
    bladeNumber = Int(iotype='in', desc='number of rotor blades')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design') 
    drivetrainDesign = Int(iotype='in', desc='type of gearbox based on drivetrain type: 1 = standard 3-stage gearbox, 2 = single-stage, 3 = multi-gen, 4 = direct drive')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore site')
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):

        super(Turbine_CostsSE, self).__init__()

    def configure(self):

        super(Turbine_CostsSE, self).configure()

        # select components
        self.replace('rotorCC', Rotor_CostsSE())
        self.replace('nacelleCC', Nacelle_CostsSE())
        self.replace('towerCC', Tower_CostsSE())
        self.replace('tcc', TurbineCostAdder())
        
        # connect inputs
        self.connect('bladeMass', 'rotorCC.bladeMass')
        self.connect('hubMass', 'rotorCC.hubMass')
        self.connect('pitchSystemMass', 'rotorCC.pitchSystemMass')
        self.connect('spinnerMass', 'rotorCC.spinnerMass')
        self.connect('advanced', 'rotorCC.advanced')
        self.connect('lowSpeedShaftMass', 'nacelleCC.lowSpeedShaftMass')
        self.connect('mainBearingMass', 'nacelleCC.mainBearingMass')
        self.connect('secondBearingMass', 'nacelleCC.secondBearingMass')
        self.connect('gearboxMass', 'nacelleCC.gearboxMass')
        self.connect('highSpeedSideMass', 'nacelleCC.highSpeedSideMass')
        self.connect('generatorMass', 'nacelleCC.generatorMass')
        self.connect('bedplateMass', ['nacelleCC.bedplateMass'])
        self.connect('yawSystemMass', 'nacelleCC.yawSystemMass')
        self.connect('machineRating', ['nacelleCC.machineRating'])
        self.connect('drivetrainDesign', ['nacelleCC.drivetrainDesign'])
        self.connect('crane', 'nacelleCC.crane')
        self.connect('offshore', ['nacelleCC.offshore', 'tcc.offshore'])
        self.connect('towerMass', 'towerCC.towerMass')
        self.connect('curr_yr', ['rotorCC.curr_yr', 'nacelleCC.curr_yr', 'towerCC.curr_yr'])
        self.connect('curr_mon', ['rotorCC.curr_mon', 'nacelleCC.curr_mon', 'towerCC.curr_mon'])


#-------------------------------------------------------------------------------

class TurbineCostAdder(FullTCCAggregator):
    
    # parameters
    offshore = Bool(iotype='in', desc='flag for offshore site')

    def __init__(self):
      
        '''
        Turbine cost adder
        
        rotor_cost : float
          rotor cost [USD]
        nacelle_cost : float
          nacelle cost [USD]
        towerCost : float
          tower cost [USD]

        Returns
        -------
        cost : float
          overall rotor cost [USD]   
        '''   
        
        super(TurbineCostAdder, self).__init__()
    
    def execute(self):
      
        partsCost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)       
        overheadCostMultiplier = 0.0 # (24/72)       
        profitMultiplier = 0.0       
        transportMultiplier = 0.0
        
        self.turbine_cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)
        
        # derivatives
        d_cost_d_rotor_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        d_cost_d_nacelle_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        d_cost_d_tower_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

        if self.offshore:
            self.turbine_cost *= 1.1

            # derivatives
            d_cost_d_rotor_cost *= 1.1
            d_cost_d_nacelle_cost *= 1.1
            d_cost_d_tower_cost *= 1.1
        
        # Jacobian
        self.J = np.array([[d_cost_d_rotor_cost, d_cost_d_nacelle_cost, d_cost_d_tower_cost]])

    def provideJ(self):

        input_keys = ['rotor_cost', 'nacelle_cost', 'tower_cost']
        output_keys = ['turbine_cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)
        
#-------------------------------------------------------------------------------       

def example():

    # simple test of module
    
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    turbine = Turbine_CostsSE()

    turbine.bladeMass = 17650.67  # inline with the windpact estimates
    turbine.hubMass = 31644.5
    turbine.pitchSystemMass = 17004.0
    turbine.spinnerMass = 1810.5
    turbine.lowSpeedShaftMass = 31257.3
    #bearingsMass = 9731.41
    turbine.mainBearingMass = 9731.41 / 2
    turbine.secondBearingMass = 9731.41 / 2
    turbine.gearboxMass = 30237.60
    turbine.highSpeedSideMass = 1492.45
    turbine.generatorMass = 16699.85
    turbine.bedplateMass = 93090.6
    turbine.yawSystemMass = 11878.24
    turbine.towerMass = 434559.0
    turbine.machineRating = 5000.0
    turbine.advanced = True
    turbine.bladeNumber = 3
    turbine.drivetrainDesign = 1
    turbine.crane = True
    turbine.offshore = True
    turbine.curr_yr = 2009
    turbine.curr_mon =  12

    turbine.run()
    
    print "Turbine cost is ${0:.2f} USD".format(turbine.turbine_cost) # $5350414.10
    print
    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(turbine.rotorCC.cost)
    print "Hub cost is ${0:.2f} USD".format(turbine.rotorCC.hubCC.cost)   # $175513.50
    print "Pitch cost is ${0:.2f} USD".format(turbine.rotorCC.pitchSysCC.cost)  # $535075.0
    print "Spinner cost is ${0:.2f} USD".format(turbine.rotorCC.spinnerCC.cost)  # $10509.00
    print
    print "Overall nacelle cost is ${0:.2f} USD".format(turbine.nacelleCC.cost) # $2884227.08
    print "LSS cost is ${0:.2f} USD".format(turbine.nacelleCC.lssCC.cost) # $183363.52
    print "Main bearings cost is ${0:.2f} USD".format(turbine.nacelleCC.bearingsCC.cost) # $56660.71
    print "Gearbox cost is ${0:.2f} USD".format(turbine.nacelleCC.gearboxCC.cost) # $648030.18
    print "HSS cost is ${0:.2f} USD".format(turbine.nacelleCC.hssCC.cost) # $15218.20
    print "Generator cost is ${0:.2f} USD".format(turbine.nacelleCC.generatorCC.cost) # $435157.75
    print "Bedplate cost is ${0:.2f} USD".format(turbine.nacelleCC.bedplateCC.cost)
    print "Yaw system cost is ${0:.2f} USD".format(turbine.nacelleCC.yawSysCC.cost) # $137609.38
    print
    print "Tower cost is ${0:.2f} USD".format(turbine.towerCC.cost) # $987180.30 

if __name__ == "__main__":  

    example()