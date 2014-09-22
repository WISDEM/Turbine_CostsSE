"""
turbine_costsse.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int, Enum
import numpy as np

from fusedwind.plant_cost.fused_tcc import FullTurbineCostModel, FullTCCAggregator, configure_full_tcc
from fusedwind.interface import implement_base

from rotor_costsse import Rotor_CostsSE
from nacelle_costsse import Nacelle_CostsSE
from tower_costsse import Tower_CostsSE

#-------------------------------------------------------------------------------
@implement_base(FullTurbineCostModel)
class Turbine_CostsSE(Assembly):

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
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore site')
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def configure(self):

        configure_full_tcc(self)

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
        
        self.create_passthrough('tcc.assemblyCostMultiplier')
        self.create_passthrough('tcc.overheadCostMultiplier')
        self.create_passthrough('tcc.profitMultiplier')
        self.create_passthrough('tcc.transportMultiplier')


#-------------------------------------------------------------------------------
@implement_base(FullTCCAggregator)
class TurbineCostAdder(Component):

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # parameters
    offshore = Bool(iotype='in', desc='flag for offshore site')
    assemblyCostMultiplier = Float(0.0, iotype='in', desc='multiplier for assembly cost in manufacturing')
    overheadCostMultiplier = Float(0.0, iotype='in', desc='multiplier for overhead')
    profitMultiplier = Float(0.0, iotype='in', desc='multiplier for profit markup')
    transportMultiplier = Float(0.0, iotype='in', desc='multiplier for transport costs')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def __init__(self):

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        self.turbine_cost = (1 + self.transportMultiplier + self.profitMultiplier) * ((1+self.overheadCostMultiplier+self.assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_rotor_cost = (1 + self.transportMultiplier + self.profitMultiplier) * (1+self.overheadCostMultiplier+self.assemblyCostMultiplier)
        self.d_cost_d_nacelle_cost = (1 + self.transportMultiplier + self.profitMultiplier) * (1+self.overheadCostMultiplier+self.assemblyCostMultiplier)
        self.d_cost_d_tower_cost = (1 + self.transportMultiplier + self.profitMultiplier) * (1+self.overheadCostMultiplier+self.assemblyCostMultiplier)

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
    turbine.drivetrain_design = 'geared'
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