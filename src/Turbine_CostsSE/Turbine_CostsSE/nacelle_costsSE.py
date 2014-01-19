"""
nacellecosts.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
from math import pi
import numpy as np

from fusedwind.plant_cost.fused_tcc_asym import FullNacelleCostModel, BaseComponentCostModel, FullNacelleCostAggregator

# -------------------------------------------------

class LowSpeedShaftCost(BaseComponentCostModel):

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine low speed shaft component.       
        
        Parameters
        ----------
        low_speed_shaft_mass : float
          lss mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD]       
        '''
        
        super(LowSpeedShaftCost, self).__init__()
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon
        
        # calculate component cost        
        LowSpeedShaftCost2002 = 3.3602 * self.low_speed_shaft_mass + 13587      # equation adjusted to be based on mass rather than rotor diameter using data from CSM
        lowSpeedShaftCostEsc            = ppi.compute('IPPI_LSS')
        self.cost = (LowSpeedShaftCost2002 * lowSpeedShaftCostEsc )

        # derivatives
        self.d_cost_d_low_speed_shaft_mass = lowSpeedShaftCostEsc * 3.3602

    def linearize(self):
        
        # Jacobian
        self.J = np.array([[self.d_cost_d_low_speed_shaft_mass]])

    def provideJ(self):

        inputs = ['low_speed_shaft_mass']
        outputs = ['cost']

        return inputs, outputs, self.J

#-------------------------------------------------------------------------------

class BearingsCost(BaseComponentCostModel):

    # variables
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    second_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine maing bearings.       
        
        Parameters
        ----------
        main_bearing_mass : float
          bearing mass [kg]
        second_bearing_mass : float
          bearing mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD]       
        '''
        
        super(BearingsCost, self).__init__()

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon
        bearingsMass = self.main_bearing_mass + self.second_bearing_mass

        # calculate component cost
        bearingCostEsc       = ppi.compute('IPPI_BRN')

        brngSysCostFactor = 17.6 # $/kg                  # cost / unit mass from CSM
        Bearings2002 = (bearingsMass) * brngSysCostFactor
        self.cost    = (( Bearings2002 ) * bearingCostEsc ) / 4   # div 4 to account for bearing cost mass differences CSM to Sunderland  

        # derivatives
        self.d_cost_d_main_bearing_mass = bearingCostEsc * brngSysCostFactor / 4
        self.d_cost_d_second_bearing_mass = bearingCostEsc * brngSysCostFactor / 4

    def linearize(self):
 
        # Jacobian
        self.J = np.array([[self.d_cost_d_main_bearing_mass, self.d_cost_d_second_bearing_mass]])

    def provideJ(self):

        inputs = ['main_bearing_mass', 'second_bearing_mass']
        outputs = ['cost']

        return inputs, outputs, self.J             

#-------------------------------------------------------------------------------

class GearboxCost(BaseComponentCostModel):

    # variables
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    
    # parameters
    drivetrain_design = Int(iotype='in', desc='type of gearbox based on drivetrain type: 1 = standard 3-stage gearbox, 2 = single-stage, 3 = multi-gen, 4 = direct drive')
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine gearbox component.       
        
        Parameters
        ----------
        gearbox_mass : float
          gearbox mass [kg]
        machine_rating : float
          machine rating [kW]
        drivetrain_design : int
          machine configuration 1 conventional, 2 medium speed, 3 multi-gen, 4 direct-drive
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD]           
        '''
        
        super(GearboxCost, self).__init__()
     
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        # calculate component cost                                              
        GearboxCostEsc     = ppi.compute('IPPI_GRB')

        costCoeff = [None, 16.45  , 74.101     ,   15.25697015,  0 ]
        costExp   = [None,  1.2491,  1.002     ,    1.2491    ,  0 ]

        if self.drivetrain_design == 1:                                 
          Gearbox2002 = 16.9 * self.gearbox_mass - 25066          # for traditional 3-stage gearbox, use mass based cost equation from NREL CSM
        else:
          Gearbox2002 = costCoeff[self.drivetrain_design] * (self.machine_rating ** costCoeff[self.drivetrain_design])        # for other drivetrain configurations, use NREL CSM equation based on machine rating

        self.cost   = Gearbox2002 * GearboxCostEsc

        # derivatives
        if self.drivetrain_design == 1:                                 
          self.d_cost_d_gearbox_mass = GearboxCostEsc * 16.9
          self.d_cost_d_machine_rating = 0.0
        else:
          self.d_cost_d_gearbox_mass = 0.0
          self.d_cost_d_machine_rating =  GearboxCostEsc * costCoeff[self.drivetrain_design] * (costCoeff[self.drivetrain_design] * (self.machine_rating ** (costCoeff[self.drivetrain_design]-1))) 

    def linearize(self):
    
        self.J = np.array([[self.d_cost_d_gearbox_mass, self.d_cost_d_machine_rating]])

    def provideJ(self):

        inputs= ['gearbox_mass', 'machine_rating']
        outputs = ['cost']

        return inputs, outputs, self.J 

#-------------------------------------------------------------------------------
              
class HighSpeedSideCost(BaseComponentCostModel):

    # variables
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine mechanical brake and HSS component.       
        
        Parameters
        ----------
        high_speed_side_mass : float
          mechBrake mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD]       
        '''
        
        super(HighSpeedSideCost, self).__init__()
     
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon 
        # calculate component cost
        mechBrakeCostEsc     = ppi.compute('IPPI_BRK')
        mechBrakeCost2002    = 10 * self.high_speed_side_mass                  # mechanical brake system cost based on $10 / kg multiplier from CSM model (inverse relationship)
        self.cost            = mechBrakeCostEsc * mechBrakeCost2002                                

        # derivatives
        self.d_cost_d_high_speed_side_mass = mechBrakeCostEsc * 10      

    def linearize(self):
 
        # Jacobian
        self.J = np.array([[self.d_cost_d_high_speed_side_mass]])

    def provideJ(self):

        inputs = ['high_speed_side_mass']
        outputs = ['cost']

        return inputs, outputs, self.J  

#-------------------------------------------------------------------------------

class GeneratorCost(BaseComponentCostModel):

    # variables
    generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    
    # parameters
    drivetrain_design = Int(iotype='in', desc='type of gearbox based on drivetrain type: 1 = standard 3-stage gearbox, 2 = single-stage, 3 = multi-gen, 4 = direct drive')
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine generator component.       
        
        Parameters
        ----------
        generator_mass : float
          generator mass [kg]
        drivetrain_design : int
          machine configuration 1 conventional, 2 medium speed, 3 multi-gen, 4 direct-drive
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD]       
        '''
        
        super(GeneratorCost, self).__init__()
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon
                                                        
        # calculate component cost                                      #TODO: only handles traditional drivetrain configuration at present
        generatorCostEsc     = ppi.compute('IPPI_GEN')
        costCoeff = [None, 65    , 54.73 ,  48.03 , 219.33 ] # $/kW - from 'Generators' worksheet


        if self.drivetrain_design == 1:
            GeneratorCost2002 = 19.697 * self.generator_mass + 9277.3
        else:
        	  GeneratorCost2002 = costCoeff[self.drivetrain_design] * self.machine_rating
        	  
        self.cost         = GeneratorCost2002 * generatorCostEsc 

        # derivatives
        if self.drivetrain_design == 1:
            self.d_cost_d_generator_mass = generatorCostEsc * 19.697   
            self.d_cost_d_machine_rating = 0.0  
        else:
        	  self.d_cost_d_generator_mass = 0.0
        	  self.d_cost_d_machine_rating = costCoeff[self.drivetrain_design] * generatorCostEsc

    def linearize(self):
 
        # Jacobian
        self.J = np.array([[self.d_cost_d_generator_mass, self.d_cost_d_machine_rating]])

    def provideJ(self):

        inputs = ['generator_mass', 'machine_rating']
        outputs = ['cost']

        return inputs, outputs, self.J                         

#-------------------------------------------------------------------------------

class BedplateCost(BaseComponentCostModel):

    # variables
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    drivetrain_design = Int(iotype='in', desc='type of drivetrain')
    
    # returns
    cost2002 = Float(iotype='out', units='USD', desc='component cost in 2002 USD')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine bedplate component.       
        
        Parameters
        ----------
        bedplate_mass : float
          bedplate mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD] 
        cost2002 : float
          componet 2002 cost [USD]      
        '''
        
        super(BedplateCost, self).__init__()
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        #calculate component cost                                    # TODO: cost needs to be adjusted based on look-up table or a materials, mass and manufacturing equation            
        BedplateCostEsc     = ppi.compute('IPPI_MFM')

        #TODO: handle different drivetrain types
        costCoeff = [None, 9.48850 , 303.96000, 17.92300 , 627.280000 ]
        costExp   = [None, 1.9525, 1.0669, 1.6716, 0.85]

        self.cost2002 = 0.9461 * self.bedplate_mass + 17799                   # equation adjusted based on mass / cost relationships for components documented in NREL CSM
        self.cost     = self.cost2002 * BedplateCostEsc

        # derivatives
        self.d_cost_d_bedplate_mass = BedplateCostEsc * 0.9461  
        self.d_cost2002_d_bedplate_mass = 0.9461

    def linearize(self):
 
        # Jacobian
        self.J = np.array([[self.d_cost_d_bedplate_mass], [self.d_cost2002_d_bedplate_mass]])

    def provideJ(self):

        inputs = ['bedplate_mass']
        outputs = ['cost', 'cost2002']

        return inputs, outputs, self.J       

#--------------------------------------------------------------------------------- 
   
class YawSystemCost(BaseComponentCostModel):

    # variables
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.       
        
        Parameters
        ----------
        yaw_system_mass : float
          yawSystem mass [kg]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
          
        Returns
        -------
        cost : float
          component cost [USD]       
        '''
        
        super(YawSystemCost, self).__init__()
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        # calculate component cost
        yawDrvBearingCostEsc = ppi.compute('IPPI_YAW')

        YawDrvBearing2002 = 8.3221 * self.yaw_system_mass + 2708.5          # cost / mass relationship derived from NREL CSM data
        self.cost         = YawDrvBearing2002 * yawDrvBearingCostEsc 

        # derivatives
        self.d_cost_d_yaw_system_mass = yawDrvBearingCostEsc * 8.3221      

    def linearize(self):
 
        # Jacobian
        self.J = np.array([[self.d_cost_d_yaw_system_mass]])

    def provideJ(self):

        inputs = ['yaw_system_mass']
        outputs = ['cost']

        return inputs, outputs, self.J                 

#-------------------------------------------------------------------------------

class NacelleSystemCostAdder(FullNacelleCostAggregator):

    # variables
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')   
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost [USD]')
    bedplateCost2002 = Float(iotype='in', units='USD', desc='component cost in 2002 USD')
    
    # parameters
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore project')
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine gearbox component.       
        
        Parameters
        ----------
        lowSpeedShaftCost : float
          component cost [USD]
        bearingsCost : float
          component cost [USD]
        gearboxCost : float
          component cost [USD]
        highSpeedSideCost : float
          component cost [USD]
        generatorCost : float
          component cost [USD]
        mainframeCost : float
          component cost [USD]
        yawSystemCost : float
          component cost [USD]
        machine_rating : float
          machine rating [kW]
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month
        offshore : bool
          flag for offshore project

        Returns
        -------
        cost : float
          component cost [USD]       
        '''

        super(NacelleSystemCostAdder, self).__init__()    
    
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        BedplateCostEsc      = ppi.compute('IPPI_MFM')

        # mainframe system including bedplate, platforms, crane and miscellaneous hardware
        nacellePlatformsMass = 0.125 * self.bedplate_mass
        NacellePlatforms2002 = 8.7 * nacellePlatformsMass

        if (self.crane):
            craneCost2002  = 12000.0
        else:
            craneCost2002  = 0.0

        # aggregation of mainframe components: bedplate, crane and platforms into single mass and cost
        BaseHardwareCost2002  = self.bedplateCost2002 * 0.7
        MainFrameCost2002   = (NacellePlatforms2002 + craneCost2002  + \
                          BaseHardwareCost2002 )
        self.mainframe_cost  = MainFrameCost2002 * BedplateCostEsc + self.bedplate_cost

        # calculations of mass and cost for other systems not included above as main drivetrain load-bearing components
        # Cost Escalators - should be obtained from PPI tables
        VspdEtronicsCostEsc  = ppi.compute('IPPI_VSE')
        nacelleCovCostEsc    = ppi.compute('IPPI_NAC')
        hydrCoolingCostEsc   = ppi.compute('IPPI_HYD')
        econnectionsCostEsc  = ppi.compute('IPPI_ELC')
        controlsCostEsc      = ppi.compute('IPPI_CTL')

        # electronic systems, hydraulics and controls
        econnectionsCost2002  = 40.0 * self.machine_rating  # 2002
        self.econnectionsCost = econnectionsCost2002 * econnectionsCostEsc
               
        VspdEtronics2002      = 79.32 * self.machine_rating
        self.vspdEtronicsCost = VspdEtronics2002 * VspdEtronicsCostEsc        

        hydrCoolingCost2002  = 12.0 * self.machine_rating # 2002
        self.hydrCoolingCost = hydrCoolingCost2002 * hydrCoolingCostEsc  

        if (not self.offshore):
            ControlsCost2002  = 35000.0 # initial approximation 2002
            self.controlsCost = ControlsCost2002 * controlsCostEsc 
        else:
            ControlsCost2002  = 55900.0 # initial approximation 2002
            self.controlsCost = ControlsCost2002 * controlsCostEsc   
        
        nacelleCovCost2002  = 11.537 * self.machine_rating + (3849.7)
        self.nacelleCovCost = nacelleCovCost2002 * nacelleCovCostEsc
        
        # aggregation of nacelle costs
        partsCost = self.lss_cost + \
                    self.bearings_cost + \
                    self.gearbox_cost + \
                    self.hss_cost + \
                    self.generator_cost + \
                    self.mainframe_cost + \
                    self.yaw_system_cost + \
                    self.econnectionsCost + \
                    self.vspdEtronicsCost + \
                    self.hydrCoolingCost + \
                    self.controlsCost + \
                    self.nacelleCovCost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)       
        overheadCostMultiplier = 0.0 # (24/72)       
        profitMultiplier = 0.0       
        transportMultiplier = 0.0
        
        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        # derivatives
        self.d_cost_d_bedplate_mass = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier) * BedplateCostEsc * 8.7 * 0.125
        self.d_cost_d_bedplateCost2002 = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier) * BedplateCostEsc * 0.7
        self.d_cost_d_bedplateCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_lowSpeedShaftCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_bearingsCost= (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_gearboxCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_highSpeedSideCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_generatorCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_yawSystemCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_machine_rating = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier) * \
                                 (econnectionsCostEsc * 40.0 + VspdEtronicsCostEsc * 79.32 + hydrCoolingCostEsc * 12.0 + nacelleCovCostEsc * 11.537))

    def linearize(self):
 
        # Jacobian
        self.J = np.array([[self.d_cost_d_bedplate_mass, self.d_cost_d_bedplateCost2002, self.d_cost_d_bedplateCost, \
                            self.d_cost_d_lowSpeedShaftCost, self.d_cost_d_bearingsCost, self.d_cost_d_gearboxCost, \
                            self.d_cost_d_highSpeedSideCost, self.d_cost_d_generatorCost, \
                            self.d_cost_d_yawSystemCost, self.d_cost_d_machine_rating]])

    def provideJ(self):

        inputs = ['bedplate_mass', 'bedplateCost2002', 'bedplate_cost', 'lss_cost', 'bearings_cost', \
                      'gearbox_cost', 'hss_cost', 'generator_cost', 'yaw_system_cost', 'machine_rating']
        outputs = ['cost']

        return inputs, outputs, self.J 

#------------------------------------------------------------------

class Nacelle_CostsSE(FullNacelleCostModel):

    ''' 
       Nacelle_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.             
    '''

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass')
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    second_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass')
    generator_mass = Float(iotype='in', units='kg', desc='component mass')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass')
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    
    # parameters
    drivetrain_design = Int(iotype='in', desc='type of gearbox based on drivetrain type: 1 = standard 3-stage gearbox, 2 = single-stage, 3 = multi-gen, 4 = direct drive')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flat for offshore site')
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def __init__(self):

        super(Nacelle_CostsSE, self).__init__()

    def configure(self):

        super(Nacelle_CostsSE, self).configure()

        # select components
        self.replace('lssCC', LowSpeedShaftCost())
        self.replace('bearingsCC', BearingsCost())
        self.replace('gearboxCC', GearboxCost())
        self.replace('hssCC', HighSpeedSideCost())
        self.replace('generatorCC', GeneratorCost())
        self.replace('bedplateCC', BedplateCost())
        self.replace('yawSysCC', YawSystemCost())
        self.replace('ncc', NacelleSystemCostAdder())
        
        # connect inputs
        self.connect('low_speed_shaft_mass', 'lssCC.low_speed_shaft_mass')
        self.connect('main_bearing_mass', 'bearingsCC.main_bearing_mass')
        self.connect('second_bearing_mass', 'bearingsCC.second_bearing_mass')
        self.connect('gearbox_mass', 'gearboxCC.gearbox_mass')
        self.connect('high_speed_side_mass', 'hssCC.high_speed_side_mass')
        self.connect('generator_mass', 'generatorCC.generator_mass')
        self.connect('bedplate_mass', ['bedplateCC.bedplate_mass', 'ncc.bedplate_mass'])
        self.connect('yaw_system_mass', 'yawSysCC.yaw_system_mass')
        self.connect('machine_rating', ['gearboxCC.machine_rating', 'ncc.machine_rating'])
        self.connect('drivetrain_design', ['gearboxCC.drivetrain_design', 'generatorCC.drivetrain_design'])
        self.connect('crane', 'ncc.crane')
        self.connect('offshore', 'ncc.offshore')
        self.connect('curr_yr', ['lssCC.curr_yr', 'bearingsCC.curr_yr', 'gearboxCC.curr_yr', 'hssCC.curr_yr', 'generatorCC.curr_yr', 'bedplateCC.curr_yr', 'yawSysCC.curr_yr', 'ncc.curr_yr'])
        self.connect('curr_mon', ['lssCC.curr_mon', 'bearingsCC.curr_mon', 'gearboxCC.curr_mon', 'hssCC.curr_mon', 'generatorCC.curr_mon', 'bedplateCC.curr_mon', 'yawSysCC.curr_mon', 'ncc.curr_mon'])


#==================================================================

def example():

    # test of module for turbine data set

    nacelle = Nacelle_CostsSE()
    
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    nacelle.low_speed_shaft_mass = 31257.3
    #nacelle.bearingsMass = 9731.41
    nacelle.main_bearing_mass = 9731.41 / 2.0
    nacelle.second_bearing_mass = 9731.41 / 2.0
    nacelle.gearbox_mass = 30237.60
    nacelle.high_speed_side_mass = 1492.45
    nacelle.generator_mass = 16699.85
    nacelle.bedplate_mass = 93090.6
    nacelle.yaw_system_mass = 11878.24
    nacelle.machine_rating = 5000.0
    nacelle.drivetrain_design = 1
    nacelle.crane = True
    nacelle.offshore = True
    nacelle.curr_yr = 2009
    nacelle.curr_mon = 12
    
    nacelle.run()

    print "LSS cost is ${0:.2f} USD".format(nacelle.lssCC.cost) # $183363.52
    print "Main bearings cost is ${0:.2f} USD".format(nacelle.bearingsCC.cost) # $56660.71
    print "Gearbox cost is ${0:.2f} USD".format(nacelle.gearboxCC.cost) # $648030.18
    print "HSS cost is ${0:.2f} USD".format(nacelle.hssCC.cost) # $15218.20
    print "Generator cost is ${0:.2f} USD".format(nacelle.generatorCC.cost) # $435157.75
    print "Bedplate cost is ${0:.2f} USD".format(nacelle.bedplateCC.cost)
    print "Yaw system cost is ${0:.2f} USD".format(nacelle.yawSysCC.cost) # $137609.38
    
    print "Overall nacelle cost is ${0:.2f} USD".format(nacelle.cost) # $2884227.08

if __name__ == '__main__':

    example()