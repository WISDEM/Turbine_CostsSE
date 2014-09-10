"""
rotor_costsse.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from commonse.config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
from math import pi
import numpy as np

from fusedwind.plant_cost.fused_tcc import FullRotorCostModel, FullRotorCostAggregator, FullHubSystemCostAggregator, BaseComponentCostModel, configure_full_rcc
from fusedwind.interface import implement_base

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BladeCost(Component):

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine blade component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        ppi_labor  = ppi.compute('IPPI_BLL')

        if (self.advanced == True):
            ppi.ref_yr = 2003
            ppi_mat   = ppi.compute('IPPI_BLA')
            slope   = 13.0 #14.0 from model
            intercept     = 5813.9
        else:
            ppi_mat   = ppi.compute('IPPI_BLD')
            slope   = 8.0
            intercept     = 21465.0
        ppi.ref_yr = 2002

        laborCoeff    = 2.7445         # todo: ignoring labor impacts for now
        laborExp      = 2.5025

        self.cost = ((slope*self.blade_mass + intercept)*ppi_mat)

        # derivatives
        self.d_cost_d_blade_mass = slope * ppi_mat

    def list_deriv_vars(self):

        inputs = ['blade_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_blade_mass]])

        return self.J


# -----------------------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HubCost(Component):

    # variables
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine hub component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')

        laborCoeff    = 2.7445
        laborExp      = 2.5025

        hubCost2002      = (self.hub_mass * 4.25) # $/kg
        hubCostEscalator = ppi.compute('IPPI_HUB')
        self.cost = (hubCost2002 * hubCostEscalator )

        # derivatives
        self.d_cost_d_hub_mass = hubCostEscalator * 4.25

    def list_deriv_vars(self):

        inputs = ['hub_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_hub_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class PitchSystemCost(Component):

    # variables
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine pitch system.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')

        laborCoeff    = 2.7445
        laborExp      = 2.5025

        pitchSysCost2002     = 2.28 * (0.0808 * (self.pitch_system_mass ** 1.4985))            # new cost based on mass - x1.328 for housing proportion
        bearingCostEscalator = ppi.compute('IPPI_PMB')
        self.cost = (bearingCostEscalator * pitchSysCost2002)

        # derivatives
        self.d_cost_d_pitch_system_mass = bearingCostEscalator * 2.28 * (0.0808 * 1.4985 * (self.pitch_system_mass ** 0.4985))

    def list_deriv_vars(self):

        inputs = ['pitch_system_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_pitch_system_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class SpinnerCost(Component):

    # variables
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine spinner component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')

        laborCoeff    = 2.7445
        laborExp      = 2.5025

        spinnerCostEscalator = ppi.compute('IPPI_NAC')
        self.cost = (spinnerCostEscalator * (5.57*self.spinner_mass))

        # derivatives
        self.d_cost_d_spinner_mass = spinnerCostEscalator * 5.57

    def list_deriv_vars(self):

        inputs = ['spinner_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_spinner_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullHubSystemCostAggregator)
class HubSystemCostAdder(Component):

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def __init__(self):
        '''
        Computation of overall hub system cost.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.hub_cost + self.pitch_system_cost + self.spinner_cost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)
        overheadCostMultiplier = 0.0 # (24/72)
        profitMultiplier = 0.0
        transportMultiplier = 0.0

        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_hubCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_pitchSystemCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_spinnerCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

    def list_deriv_vars(self):

        inputs = ['hub_cost', 'pitch_system_cost', 'spinner_cost']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_hubCost, self.d_cost_d_pitchSystemCost, self.d_cost_d_spinnerCost]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullRotorCostAggregator)
class RotorCostAdder(Component):
    """
    RotorCostAdder adds up individual rotor system and component costs to get overall rotor cost.
    """

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def __init__(self):
        '''
        Computation of overall hub system cost.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.cost = self.blade_cost * self.blade_number + self.hub_system_cost

        # derivatives
        self.d_cost_d_bladeCost = self.blade_number
        self.d_cost_d_hubSystemCost = 1

    def list_deriv_vars(self):

        inputs = ['blade_cost', 'hub_system_cost']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_bladeCost, self.d_cost_d_hubSystemCost]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullRotorCostModel)
class Rotor_CostsSE(FullRotorCostModel):

    '''
       Rotor_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.
    '''

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def configure(self):

        configure_full_rcc(self)

        # select components
        self.replace('bladeCC', BladeCost())
        self.replace('hubCC', HubCost())
        self.replace('pitchSysCC', PitchSystemCost())
        self.replace('spinnerCC', SpinnerCost())
        self.replace('hubSysCC', HubSystemCostAdder())
        self.replace('rcc', RotorCostAdder())

        # connect inputs
        self.connect('blade_mass', 'bladeCC.blade_mass')
        self.connect('hub_mass', 'hubCC.hub_mass')
        self.connect('pitch_system_mass', 'pitchSysCC.pitch_system_mass')
        self.connect('spinner_mass', 'spinnerCC.spinner_mass')
        self.connect('year', ['hubCC.year', 'pitchSysCC.year', 'spinnerCC.year', 'bladeCC.year'])
        self.connect('month', ['hubCC.month', 'pitchSysCC.month', 'spinnerCC.month', 'bladeCC.month'])
        self.connect('advanced', 'bladeCC.advanced')

#-------------------------------------------------------------------------------

def example():

    # simple test of module
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    # NREL 5 MW turbine
    print "NREL 5 MW turbine test"
    rotor = Rotor_CostsSE()

    # Blade Test 1
    rotor.blade_number = 3
    rotor.advanced = True
    rotor.blade_mass = 17650.67  # inline with the windpact estimates
    rotor.hub_mass = 31644.5
    rotor.pitch_system_mass = 17004.0
    rotor.spinner_mass = 1810.5
    rotor.year = 2009
    rotor.month = 12

    rotor.run()

    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(rotor.cost)

if __name__ == "__main__":

    example()