"""
rotorcosts.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
from math import pi
import numpy as np

from fusedwind.plant_cost.fused_tcc_asym import FullRotorCostModel, FullRotorCostAggregator, FullHubSystemCostAggregator, BaseComponentCostModel

#-------------------------------------------------------------------------------

class BladeCost(BaseComponentCostModel):

    # variables
    bladeMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine blade component.       
        
        Parameters
        ----------
        bladeMass : float
          blade mass [kg]
        advanced : bool
          boolean for advanced (using carbon) or basline (all fiberglass) blade 
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
        
        Returns
        -------
        cost : float
          component cost [USD]       
        '''

        super(BladeCost, self).__init__()

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon
         
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
        
        self.cost = ((slope*self.bladeMass + intercept)*ppi_mat)

        # derivatives
        self.d_cost_d_bladeMass = slope * ppi_mat

    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_bladeMass]])

    def provideJ(self):

        inputs = ['bladeMass']
        outputs = ['cost']

        return inputs, outputs, self.J


# -----------------------------------------------------------------------------------------------

class HubCost(BaseComponentCostModel):

    # variables
    hubMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine hub component.       
        
        Parameters
        ----------
        hubMass : float
          hub mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
        
        Returns
        -------
        cost : float
          component cost [USD]           
        '''

        super(HubCost, self).__init__()
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')
            
        laborCoeff    = 2.7445
        laborExp      = 2.5025    

        hubCost2002      = (self.hubMass * 4.25) # $/kg
        hubCostEscalator = ppi.compute('IPPI_HUB')
        self.cost = (hubCost2002 * hubCostEscalator )

        # derivatives
        self.d_cost_d_hubMass = hubCostEscalator * 4.25
    
    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_hubMass]])

    def provideJ(self):

        inputs = ['hubMass']
        outputs = ['cost']

        return inputs, outputs, self.J
        
#-------------------------------------------------------------------------------

class PitchSystemCost(BaseComponentCostModel):

    # variables
    pitchSystemMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine pitch system.       
        
        Parameters
        ----------
        pitchSystemMass : float
          pitch system mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month

        Returns
        -------
        cost : float
          component cost [USD]           
        '''
        
        super(PitchSystemCost, self).__init__()
        
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')
            
        laborCoeff    = 2.7445
        laborExp      = 2.5025    

        pitchSysCost2002     = 2.28 * (0.0808 * (self.pitchSystemMass ** 1.4985))            # new cost based on mass - x1.328 for housing proportion
        bearingCostEscalator = ppi.compute('IPPI_PMB')
        self.cost = (bearingCostEscalator * pitchSysCost2002)

        # derivatives
        self.d_cost_d_pitchSystemMass = bearingCostEscalator * 2.28 * (0.0808 * 1.4985 * (self.pitchSystemMass ** 0.4985))

    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_pitchSystemMass]])

    def provideJ(self):

        inputs = ['pitchSystemMass']
        outputs = ['cost']

        return inputs, outputs, self.J
        
#-------------------------------------------------------------------------------

class SpinnerCost(BaseComponentCostModel):

    # variables
    spinnerMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine spinner component.       
        
        Parameters
        ----------
        spinnerMass : float
          spinner mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month

        Returns
        -------
        cost : float          
        '''
        
        super(SpinnerCost, self).__init__()
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')
            
        laborCoeff    = 2.7445
        laborExp      = 2.5025    

        spinnerCostEscalator = ppi.compute('IPPI_NAC')
        self.cost = (spinnerCostEscalator * (5.57*self.spinnerMass))

        # derivatives
        self.d_cost_d_spinnerMass = spinnerCostEscalator * 5.57

    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_spinnerMass]])

    def provideJ(self):

        inputs = ['spinnerMass']
        outputs = ['cost']

        return inputs, outputs, self.J

#-------------------------------------------------------------------------------

class HubSystemCostAdder(FullHubSystemCostAggregator):

    def __init__(self):
        '''
        Computation of overall hub system cost.       
        
        Parameters
        ----------
        hubCost : float
          hub component cost [USD]
        pitchSystemCost : float
          pitch system cost [USD]
        spinnerCost : float [USD]
          spinner component cost [USD]

        Returns
        -------
        cost : float
          overall hub system cost [USD]   
        '''
        
        super(HubSystemCostAdder,self).__init__()

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

    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_hubCost, self.d_cost_d_pitchSystemCost, self.d_cost_d_spinnerCost]])

    def provideJ(self):

        inputs = ['hub_cost', 'pitch_system_cost', 'spinner_cost']
        outputs = ['cost']

        return inputs, outputs, self.J

#-------------------------------------------------------------------------------

class RotorCostAdder(FullRotorCostAggregator):
    """
    RotorCostAdder adds up individual rotor system and component costs to get overall rotor cost.
    """

    def __init__(self):
        '''
        Computation of overall hub system cost.       
        
        Parameters
        ----------
        bladeCost : float
          individual blade cost [USD]
        hubSystemCost : float
          hub system cost [USD]
        bladeNumber : int
          number of rotor blades

        Returns
        -------
        cost : float
          overall rotor cost [USD]   
        '''            

        super(RotorCostAdder, self).__init__()
    
    def execute(self):

        self.cost = self.blade_cost * self.blade_number + self.hub_system_cost

        # derivatives
        self.d_cost_d_bladeCost = self.blade_number
        self.d_cost_d_hubSystemCost = 1

    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_bladeCost, self.d_cost_d_hubSystemCost]])

    def provideJ(self):

        inputs = ['blade_cost', 'hub_system_cost']
        outputs = ['cost']

        return inputs, outputs, self.J

#-------------------------------------------------------------------------------

class Rotor_CostsSE(FullRotorCostModel):

    ''' 
       Rotor_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.             
    '''

    # variables
    bladeMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hubMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitchSystemMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinnerMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design') 

    def __init__(self):

        super(Rotor_CostsSE, self).__init__()

    def configure(self):

        super(Rotor_CostsSE,self).configure()

        # select components
        self.replace('bladeCC', BladeCost())
        self.replace('hubCC', HubCost())
        self.replace('pitchSysCC', PitchSystemCost())
        self.replace('spinnerCC', SpinnerCost())
        self.replace('hubSysCC', HubSystemCostAdder())
        self.replace('rcc', RotorCostAdder())
        
        # connect inputs
        self.connect('bladeMass', 'bladeCC.bladeMass')
        self.connect('hubMass', 'hubCC.hubMass')
        self.connect('pitchSystemMass', 'pitchSysCC.pitchSystemMass')
        self.connect('spinnerMass', 'spinnerCC.spinnerMass')
        self.connect('curr_yr', ['hubCC.curr_yr', 'pitchSysCC.curr_yr', 'spinnerCC.curr_yr', 'bladeCC.curr_yr'])
        self.connect('curr_mon', ['hubCC.curr_mon', 'pitchSysCC.curr_mon', 'spinnerCC.curr_mon', 'bladeCC.curr_mon'])
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
    rotor.bladeMass = 17650.67  # inline with the windpact estimates
    rotor.hubMass = 31644.5
    rotor.pitchSystemMass = 17004.0
    rotor.spinnerMass = 1810.5
    rotor.curr_yr = 2009
    rotor.curr_mon = 12
    
    rotor.execute()
    
    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(rotor.cost)

if __name__ == "__main__":

    example()