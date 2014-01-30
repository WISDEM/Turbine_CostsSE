"""
turbinecost.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
import numpy as np

from fusedwind.plant_cost.fused_tcc_asym import FullTurbineCapitalCostModel, FullTCCAggregator

from rotor_costsSE import Rotor_CostsSE
from nacelle_costsSE import Nacelle_CostsSE
from tower_costsSE import Tower_CostsSE

#-------------------------------------------------------------------------------

class Turbine_CostsSE(FullTurbineCapitalCostModel):

    '''
    Initial computation of the costs for the wind turbine.

    Parameters
    ----------
    blade_mass : float
      blade mass [kg]
    hub_mass : float
      hub mass [kg]
    pitch_system_mass : float
      pitch system mass [kg]
    spinner_mass : float
      spinner mass [kg]
    low_speed_shaft_mass : float
      Low speed shaft mass [kg]
    mainBearingsMass : float
      bearing mass [kg]
    secondBearingsMass : float
      bearing mass [kg]
    gearbox_mass : float
      Gearbox mass [kg]
    high_speed_side_mass : float
      High speed side mass [kg]
    bedplate_mass : float
      Bedplate mass [kg]
    yaw_system_mass : float
      Yaw system mass [kg]
    tower_mass : float
      mass [kg] of the wind turbine tower
    machine_rating : float
      Machine rating for turbine [kW]
    blade_number : int
      Number of blades on rotor
    advanced : bool
      boolean for advanced (using carbon) or basline (all fiberglass) blade
    drivetrain_design : int
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
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass')
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    second_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass')
    generator_mass = Float(iotype='in', units='kg', desc='component mass')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass')
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass')
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    advanced_blade = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')
    drivetrain_design = Int(iotype='in', desc='type of gearbox based on drivetrain type: 1 = standard 3-stage gearbox, 2 = single-stage, 3 = multi-gen, 4 = direct drive')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore site')
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

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
        self.connect('blade_mass', 'rotorCC.blade_mass')
        self.connect('blade_number', 'rotorCC.blade_number')
        self.connect('hub_mass', 'rotorCC.hub_mass')
        self.connect('pitch_system_mass', 'rotorCC.pitch_system_mass')
        self.connect('spinner_mass', 'rotorCC.spinner_mass')
        self.connect('advanced_blade', 'rotorCC.advanced')
        self.connect('low_speed_shaft_mass', 'nacelleCC.low_speed_shaft_mass')
        self.connect('main_bearing_mass', 'nacelleCC.main_bearing_mass')
        self.connect('second_bearing_mass', 'nacelleCC.second_bearing_mass')
        self.connect('gearbox_mass', 'nacelleCC.gearbox_mass')
        self.connect('high_speed_side_mass', 'nacelleCC.high_speed_side_mass')
        self.connect('generator_mass', 'nacelleCC.generator_mass')
        self.connect('bedplate_mass', ['nacelleCC.bedplate_mass'])
        self.connect('yaw_system_mass', 'nacelleCC.yaw_system_mass')
        self.connect('machine_rating', ['nacelleCC.machine_rating'])
        self.connect('drivetrain_design', ['nacelleCC.drivetrain_design'])
        self.connect('crane', 'nacelleCC.crane')
        self.connect('offshore', ['nacelleCC.offshore', 'tcc.offshore'])
        self.connect('tower_mass', 'towerCC.tower_mass')
        self.connect('year', ['rotorCC.year', 'nacelleCC.year', 'towerCC.year'])
        self.connect('month', ['rotorCC.month', 'nacelleCC.month', 'towerCC.month'])


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

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)
        overheadCostMultiplier = 0.0 # (24/72)
        profitMultiplier = 0.0
        transportMultiplier = 0.0

        self.turbine_cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_rotor_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_nacelle_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_tower_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

        if self.offshore:
            self.turbine_cost *= 1.1

            # derivatives
            self.d_cost_d_rotor_cost *= 1.1
            self.d_cost_d_nacelle_cost *= 1.1
            self.d_cost_d_tower_cost *= 1.1

    def list_deriv_vars(self):

        inputs = ['rotor_cost', 'nacelle_cost', 'tower_cost']
        outputs = ['turbine_cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_rotor_cost, self.d_cost_d_nacelle_cost, self.d_cost_d_tower_cost]])

        return self.J

#-------------------------------------------------------------------------------

def example():

    # simple test of module

    turbine = Turbine_CostsSE()

    turbine.blade_mass = 17650.67  # inline with the windpact estimates
    turbine.hub_mass = 31644.5
    turbine.pitch_system_mass = 17004.0
    turbine.spinner_mass = 1810.5
    turbine.low_speed_shaft_mass = 31257.3
    #bearingsMass = 9731.41
    turbine.main_bearing_mass = 9731.41 / 2
    turbine.second_bearing_mass = 9731.41 / 2
    turbine.gearbox_mass = 30237.60
    turbine.high_speed_side_mass = 1492.45
    turbine.generator_mass = 16699.85
    turbine.bedplate_mass = 93090.6
    turbine.yaw_system_mass = 11878.24
    turbine.tower_mass = 434559.0
    turbine.machine_rating = 5000.0
    turbine.advanced = True
    turbine.blade_number = 3
    turbine.drivetrain_design = 1
    turbine.crane = True
    turbine.offshore = True
    turbine.year = 2010
    turbine.month =  12

    turbine.run()

    print "Turbine cost is ${0:.2f} USD".format(turbine.turbine_cost) # $5350414.10
    print
    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(turbine.rotorCC.cost)
    print "Blade cost is ${0:.2f} USD".format(turbine.rotorCC.bladeCC.cost)
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