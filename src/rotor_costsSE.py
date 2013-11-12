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

#-------------------------------------------------------------------------------

class BladeCost(Component):

    # variables
    bladeMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='Blade cost for an individual blade')

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
        d_cost_d_bladeMass = slope * ppi_mat
        
        # Jacobian
        self.J = np.array([[d_cost_d_bladeMass]])

    def provideJ(self):

        input_keys = ['bladeMass']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)


# -----------------------------------------------------------------------------------------------

class HubCost(Component):

    # variables
    hubMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='Blade cost for an individual blade')

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
        d_cost_d_hubMass = hubCostEscalator * 4.25
        
        # Jacobian
        self.J = np.array([[d_cost_d_hubMass]])

    def provideJ(self):

        input_keys = ['hubMass']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)
        
#-------------------------------------------------------------------------------

class PitchSystemCost(Component):

    # variables
    pitchSystemMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='Blade cost for an individual blade')

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
        d_cost_d_pitchSystemMass = bearingCostEscalator * 2.28 * (0.0808 * 1.4985 * (self.pitchSystemMass ** 0.4985))
        
        # Jacobian
        self.J = np.array([[d_cost_d_pitchSystemMass]])

    def provideJ(self):

        input_keys = ['pitchSystemMass']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)
        
#-------------------------------------------------------------------------------

class SpinnerCost(Component):

    # variables
    spinnerMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='Blade cost for an individual blade')

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
        d_cost_d_spinnerMass = spinnerCostEscalator * 5.57
        
        # Jacobian
        self.J = np.array([[d_cost_d_spinnerMass]])

    def provideJ(self):

        input_keys = ['spinnerMass']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)

#-------------------------------------------------------------------------------

class HubSystemCostAdder(Component):

    # variables
    hubCost = Float(iotype='in', units='USD', desc='hub component cost')
    pitchSystemCost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinnerCost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall hub system cost')

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
    
        partsCost = self.hubCost + self.pitchSystemCost + self.spinnerCost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)       
        overheadCostMultiplier = 0.0 # (24/72)       
        profitMultiplier = 0.0       
        transportMultiplier = 0.0
        
        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)
        
        # derivatives
        d_cost_d_hubCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        d_cost_d_pitchSystemCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        d_cost_d_spinnerCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        
        # Jacobian
        self.J = np.array([[d_cost_d_hubCost, d_cost_d_pitchSystemCost, d_cost_d_spinnerCost]])

    def provideJ(self):

        input_keys = ['hubCost', 'pitchSystemCost', 'spinnerCost']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)   

#-------------------------------------------------------------------------------

class HubSystemCost(Assembly):

    ''' 
       HubSystemCost class
          The HubSystemCost class is used to represent the hub system costs of a wind turbine.             
    '''

    # variables
    hubMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitchSystemMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinnerMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def configure(self):

        # select components
        self.add('hubSystemCostAdder', HubSystemCostAdder())
        self.add('hubCost', HubCost())
        self.add('pitchSystemCost', PitchSystemCost())
        self.add('spinnerCost', SpinnerCost())
        
        # workflow
        self.driver.workflow.add(['hubSystemCostAdder','hubCost', 'pitchSystemCost', 'spinnerCost'])
        
        # connect inputs
        self.connect('hubMass', 'hubCost.hubMass')
        self.connect('pitchSystemMass', 'pitchSystemCost.pitchSystemMass')
        self.connect('spinnerMass', 'spinnerCost.spinnerMass')
        self.connect('curr_yr', ['hubCost.curr_yr', 'pitchSystemCost.curr_yr', 'spinnerCost.curr_yr'])
        self.connect('curr_mon', ['hubCost.curr_mon', 'pitchSystemCost.curr_mon', 'spinnerCost.curr_mon'])
        
        # connect components
        self.connect('hubCost.cost', 'hubSystemCostAdder.hubCost')
        self.connect('pitchSystemCost.cost', 'hubSystemCostAdder.pitchSystemCost')
        self.connect('spinnerCost.cost', 'hubSystemCostAdder.spinnerCost')
        
        # create passthroughs
        self.create_passthrough('hubSystemCostAdder.cost')

#-------------------------------------------------------------------------------

class RotorCostAdder(Component):
    """
    RotorCostAdder adds up individual rotor system and component costs to get overall rotor cost.
    """

    # variables
    bladeCost = Float(iotype='in', units='USD', desc='individual blade cost')
    hubSystemCost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    bladeNumber = Int(iotype='in', desc='number of rotor blades')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall rotor cost')

    def __init__(self):
        '''
        Computation of overall hub system cost.       
        
        Parameters
        ----------
        bladeCost : float
          individual blade cost [USD]
        hubSystemCost : float
          hub system cost [USD]
        bladeNumber : float
          number of rotor blades

        Returns
        -------
        cost : float
          overall rotor cost [USD]   
        '''            

        super(RotorCostAdder, self).__init__()
    
    def execute(self):

        self.cost = self.bladeCost * self.bladeNumber + self.hubSystemCost

        # derivatives
        d_cost_d_bladeCost = self.bladeNumber
        d_cost_d_hubSystemCost = 1
        
        # Jacobian
        self.J = np.array([[d_cost_d_bladeCost, d_cost_d_hubSystemCost]])

    def provideJ(self):

        input_keys = ['bladeCost', 'hubSystemCost']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)

#-------------------------------------------------------------------------------

class Rotor_CostsSE(Assembly):

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
    bladeNumber = Int(iotype='in', desc='number of rotor blades')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design') 

    def configure(self):

        # select components
        self.add('hubSystemCost', HubSystemCost())
        self.add('bladeCost', BladeCost())
        self.add('rotorCostAdder', RotorCostAdder())
        
        # workflow
        self.driver.workflow.add(['hubSystemCost', 'bladeCost', 'rotorCostAdder'])
        
        # connect inputs
        self.connect('bladeMass', 'bladeCost.bladeMass')
        self.connect('hubMass', 'hubSystemCost.hubMass')
        self.connect('pitchSystemMass', 'hubSystemCost.pitchSystemMass')
        self.connect('spinnerMass', 'hubSystemCost.spinnerMass')
        self.connect('curr_yr', ['hubSystemCost.curr_yr', 'bladeCost.curr_yr'])
        self.connect('curr_mon', ['hubSystemCost.curr_mon', 'bladeCost.curr_mon'])
        self.connect('bladeNumber', 'rotorCostAdder.bladeNumber')
        self.connect('advanced', 'bladeCost.advanced')
        
        # connect components
        self.connect('hubSystemCost.cost', 'rotorCostAdder.hubSystemCost')
        self.connect('bladeCost.cost', 'rotorCostAdder.bladeCost')
        
        # create passthroughs
        self.create_passthrough('rotorCostAdder.cost')

#-------------------------------------------------------------------------------     

def example():
  
    # simple test of module
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    # NREL 5 MW turbine
    print "NREL 5 MW turbine test"
    rotor = Rotor_CostsSE()

    # Blade Test 1
    rotor.bladeMass = 17650.67  # inline with the windpact estimates
    rotor.advanced = True
    rotor.bladeNumber = 3
    rotor.hubMass = 31644.5
    rotor.pitchSystemMass = 17004.0
    rotor.spinnerMass = 1810.5
    rotor.curr_yr = 2009
    rotor.curr_mon = 12
    
    rotor.run()
    
    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(rotor.cost)

if __name__ == "__main__":

    example()