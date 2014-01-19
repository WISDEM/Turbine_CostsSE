"""
tcc_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_tcc_asym import BaseTurbineCapitalCostModel, BaseTCCAggregator
from fusedwind.vartrees.varTrees import Turbine

from Turbine_CostsSE.NREL_CSM_TCC.blades_csm_component import blades_csm_component
from Turbine_CostsSE.NREL_CSM_TCC.hub_csm_component import hub_csm_component
from Turbine_CostsSE.NREL_CSM_TCC.nacelle_csm_component import nacelle_csm_component
from Turbine_CostsSE.NREL_CSM_TCC.tower_csm_component import tower_csm_component

# -------------------------------------------------------
# Rotor mass adder
class rotor_mass_adder(Component):

    # Variables
    blade_mass = Float(0.0, units='kg', iotype='in', desc='mass for a single wind turbine blade')
    hub_system_mass = Float(0.0, units='kg', iotype='in', desc='hub system mass')  
    
    # Parameters
    blade_number = Int(3, iotype='in', desc='blade numebr')
    
    # Outputs
    rotor_mass = Float(units='kg', iotype='out', desc= 'overall rotor mass')

    def __init__(self):
      
        super(rotor_mass_adder,self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
       
        self.rotor_mass = self.blade_mass * self.blade_number + self.hub_system_mass
         
        self.d_mass_d_blade_mass = self.blade_number
        self.d_mass_d_hub_mass = 1.0
         
    def list_deriv_vars(self):

        inputs = ('blade_mass', 'hub_system_mass')
        outputs = ('rotor_mass')
        
        return inputs, outputs
    
    def provideJ(self):
      
        self.J = np.array([[self.d_mass_d_blade_mass, self.d_mass_d_hub_mass]])        
        
        return self.J

# --------------------------------------------------------------------

class tcc_csm_assembly(BaseTurbineCapitalCostModel):

    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    machine_rating = Float(5000.0, units = 'kW', iotype='in', desc = 'rated power of wind turbine')
    hub_height = Float(90.0, units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')

    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')
    offshore = Bool(True, iotype='in', desc = 'boolean for offshore')

    def __init__(self):

        super(tcc_csm_assembly, self).__init__()

    def configure(self):

        super(tcc_csm_assembly,self).configure()

        self.replace('tcc', tcc_csm_component())
        self.add('blades', blades_csm_component())
        self.add('hub', hub_csm_component())
        self.add('nacelle', nacelle_csm_component())
        self.add('tower', tower_csm_component())
        self.add('rotor', rotor_mass_adder())
        
        self.connect('rotor_diameter', ['blades.rotor_diameter', 'hub.rotor_diameter', 'nacelle.rotor_diameter', 'tower.rotor_diameter'])
        self.connect('machine_rating', 'nacelle.machine_rating')
        self.connect('hub_height', ['tower.hub_height'])
        self.connect('blade_number', ['rotor.blade_number', 'hub.blade_number', 'tcc.blade_number'])
        self.connect('offshore', ['nacelle.offshore', 'tcc.offshore'])
        self.connect('year', ['blades.year', 'hub.year', 'nacelle.year', 'tower.year'])
        self.connect('month', ['blades.month', 'hub.month', 'nacelle.month', 'tower.month'])
        
        self.connect('blades.blade_mass', ['hub.blade_mass', 'rotor.blade_mass'])
        self.connect('hub.hub_system_mass', 'rotor.hub_system_mass')
        self.connect('rotor.rotor_mass', 'nacelle.rotor_mass')
        
        self.create_passthrough('blades.advanced_blade')
        self.create_passthrough('nacelle.rotor_thrust')
        self.create_passthrough('nacelle.rotor_torque')
        self.create_passthrough('nacelle.crane')
        self.create_passthrough('nacelle.advanced_bedplate')
        self.create_passthrough('nacelle.drivetrain_design')
        self.create_passthrough('tower.advanced_tower')
        
        self.create_passthrough('tcc.turbineVT')
        self.create_passthrough('tcc.turbine_mass')
        
        # connect mass and cost outputs to tcc
        self.connect('blades.blade_mass', ['tcc.blade_mass'])
        self.connect('blades.blade_cost', 'tcc.blade_cost')

        self.connect('hub.hub_system_cost', 'tcc.hub_system_cost')
        self.connect('hub.hub_system_mass', 'tcc.hub_system_mass')
        self.connect('hub.hub_cost', 'tcc.hub_cost')
        self.connect('hub.hub_mass', 'tcc.hub_mass')
        self.connect('hub.pitch_system_cost', 'tcc.pitch_system_cost')
        self.connect('hub.pitch_system_mass', 'tcc.pitch_system_mass')
        self.connect('hub.spinner_cost', 'tcc.spinner_cost')
        self.connect('hub.spinner_mass', 'tcc.spinner_mass')

        self.connect('nacelle.nacelle_mass', 'tcc.nacelle_mass')
        self.connect('nacelle.lowSpeedShaft_mass', 'tcc.lowSpeedShaft_mass')
        self.connect('nacelle.bearings_mass', 'tcc.bearings_mass')
        self.connect('nacelle.gearbox_mass', 'tcc.gearbox_mass')
        self.connect('nacelle.mechanicalBrakes_mass', 'tcc.mechanicalBrakes_mass')
        self.connect('nacelle.generator_mass', 'tcc.generator_mass')
        self.connect('nacelle.VSElectronics_mass', 'tcc.VSElectronics_mass')
        self.connect('nacelle.yawSystem_mass', 'tcc.yawSystem_mass')
        self.connect('nacelle.mainframeTotal_mass', 'tcc.mainframeTotal_mass')
        self.connect('nacelle.electronicCabling_mass', 'tcc.electronicCabling_mass')
        self.connect('nacelle.HVAC_mass', 'tcc.HVAC_mass')
        self.connect('nacelle.nacelleCover_mass', 'tcc.nacelleCover_mass')
        self.connect('nacelle.controls_mass', 'tcc.controls_mass')

        self.connect('nacelle.nacelle_cost', 'tcc.nacelle_cost')
        self.connect('nacelle.lowSpeedShaft_cost', 'tcc.lowSpeedShaft_cost')
        self.connect('nacelle.bearings_cost', 'tcc.bearings_cost')
        self.connect('nacelle.gearbox_cost', 'tcc.gearbox_cost')
        self.connect('nacelle.mechanicalBrakes_cost', 'tcc.mechanicalBrakes_cost')
        self.connect('nacelle.generator_cost', 'tcc.generator_cost')
        self.connect('nacelle.VSElectronics_cost', 'tcc.VSElectronics_cost')
        self.connect('nacelle.yawSystem_cost', 'tcc.yawSystem_cost')
        self.connect('nacelle.mainframeTotal_cost', 'tcc.mainframeTotal_cost')
        self.connect('nacelle.electronicCabling_cost', 'tcc.electronicCabling_cost')
        self.connect('nacelle.HVAC_cost', 'tcc.HVAC_cost')
        self.connect('nacelle.nacelleCover_cost', 'tcc.nacelleCover_cost')
        self.connect('nacelle.controls_cost', 'tcc.controls_cost')
        
        self.connect('tower.tower_mass', 'tcc.tower_mass')
        self.connect('tower.tower_cost', 'tcc.tower_cost')

    def execute(self):

        print "In {0}.execute()...".format(self.__class__)

        super(tcc_csm_assembly, self).execute()  # will actually run the workflow

#------------------------------------------------------------------

class tcc_csm_component(BaseTCCAggregator):

    # Variables    
    blade_cost = Float(0.0, units='USD', iotype='in', desc='cost for a single wind turbine blade')
    blade_mass = Float(0.0, units='kg', iotype='in', desc='mass for a single wind turbine blade')
    hub_system_cost = Float(0.0, units='USD', iotype='in', desc='hub system cost')
    hub_system_mass = Float(0.0, units='kg', iotype='in', desc='hub system mass')
    nacelle_mass = Float(0.0, units='kg', iotype='in', desc='nacelle mass')
    nacelle_cost = Float(0.0, units='USD', iotype='in', desc='nacelle cost')
    tower_cost = Float(0.0, units='USD', iotype='in', desc='cost for a tower')
    tower_mass = Float(0.0, units='kg', iotype='in', desc='mass for a turbine tower')

    # Parameters (and ignored inputs)
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')
    offshore = Bool(False, iotype='in', desc= 'boolean for offshore')

    hub_cost = Float(0.0, units='USD', iotype='in', desc='hub cost')
    hub_mass = Float(0.0, units='kg', iotype='in', desc='hub mass')
    pitch_system_cost = Float(0.0, units='USD', iotype='in', desc='pitch system cost')
    pitch_system_mass = Float(0.0, units='kg', iotype='in', desc='pitch system mass')
    spinner_cost = Float(0.0, units='USD', iotype='in', desc='spinner / nose cone cost')
    spinner_mass = Float(0.0, units='kg', iotype='in', desc='spinner / nose cone mass')

    lowSpeedShaft_mass = Float(0.0, units='kg', iotype='in', desc= 'low speed shaft mass')
    bearings_mass = Float(0.0, units='kg', iotype='in', desc= 'bearings system mass')
    gearbox_mass = Float(0.0, units='kg', iotype='in', desc= 'gearbox and housing mass')
    mechanicalBrakes_mass = Float(0.0, units='kg', iotype='in', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generator_mass = Float(0.0, units='kg', iotype='in', desc= 'generator and housing mass')
    VSElectronics_mass = Float(0.0, units='kg', iotype='in', desc= 'variable speed electronics mass')
    yawSystem_mass = Float(0.0, units='kg', iotype='in', desc= 'yaw system mass')
    mainframeTotal_mass = Float(0.0, units='kg', iotype='in', desc= 'mainframe total mass including bedplate')
    electronicCabling_mass = Float(0.0, units='kg', iotype='in', desc= 'electronic cabling mass')
    HVAC_mass = Float(0.0, units='kg', iotype='in', desc= 'HVAC system mass')
    nacelleCover_mass = Float(0.0, units='kg', iotype='in', desc= 'nacelle cover mass')
    controls_mass = Float(0.0, units='kg', iotype='in', desc= 'control system mass')

    lowSpeedShaft_cost = Float(0.0, units='kg', iotype='in', desc= 'low speed shaft _cost')
    bearings_cost = Float(0.0, units='kg', iotype='in', desc= 'bearings system _cost')
    gearbox_cost = Float(0.0, units='kg', iotype='in', desc= 'gearbox and housing _cost')
    mechanicalBrakes_cost = Float(0.0, units='kg', iotype='in', desc= 'high speed shaft, coupling, and mechanical brakes _cost')
    generator_cost = Float(0.0, units='kg', iotype='in', desc= 'generator and housing _cost')
    VSElectronics_cost = Float(0.0, units='kg', iotype='in', desc= 'variable speed electronics _cost')
    yawSystem_cost = Float(0.0, units='kg', iotype='in', desc= 'yaw system _cost')
    mainframeTotal_cost = Float(0.0, units='kg', iotype='in', desc= 'mainframe total _cost including bedplate')
    electronicCabling_cost = Float(0.0, units='kg', iotype='in', desc= 'electronic cabling _cost')
    HVAC_cost = Float(0.0, units='kg', iotype='in', desc= 'HVAC system _cost')
    nacelleCover_cost = Float(0.0, units='kg', iotype='in', desc= 'nacelle cover _cost')
    controls_cost = Float(0.0, units='kg', iotype='in', desc= 'control system _cost')

    # Outputs
    turbine_mass = Float(0.0, units='kg', iotype='out', desc='turbine mass')
    
    # Outputs without derivatives
    turbineVT = VarTree(Turbine(), iotype='out')

    def __init__(self):
        """
        OpenMDAO component to wrap turbine model of the NREL _cost and Scaling Model (csmTurbine.py).

        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m] 
        blade_number : int
          number of rotor blades
        advanced_blade : bool
          boolean for use of advanced blade curve
        max_tip_speed : float
          maximum allowable tip speed for the rotor [m/s]
        rated_wind_speed : float
          wind speed for rated power [m/s]
        thrust_coefficient : float
          thrust coefficient for rotor at rated power [N]
        blade_cost : float
          blade cost for turbine [USD]
        machine_rating : float
          rated machine power in kW
        drivetrain_design : int
          drivetrain design type 1 = 3-stage geared, 2 = single-stage geared, 3 = multi-generator, 4 = direct drive
        crane : bool
          boolean for presence of nacelle service crane
        advanced_bedplate : bool
          type of bedplate design 1 = traditional
        max_efficiency : float
          maximum efficiency of drivetrain
        hub_height : float
          hub height of wind turbine above ground / sea level
        altitude : float
          altitude of onshore wind turbine [m]
        sea_depth : float
          sea depth for offshore wind project [m]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        turbine_cost : float
          turbine cost per turbine [USD]
        turbine_mass : float
          turbine mass [kg]
        turbine : Turbine
          Variable tree for detailed turbine masses and costs
        """       

        super(tcc_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Execute Turbine Capital _costs Model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)

        # high level output assignment
        self.turbine_mass = self.blade_mass * self.blade_number + self.hub_system_mass + self.nacelle_mass + self.tower_mass
        self.turbine_cost = self.blade_cost * self.blade_number + self.hub_system_cost + self.nacelle_cost + self.tower_cost

        if self.offshore:
            self.turbine_cost *= 1.1
   
        # derivatives     
        self.d_mass_d_blade_mass = self.blade_number
        self.d_mass_d_hub_mass = 1.0
        self.d_mass_d_nacelle_mass = 1.0
        self.d_mass_d_tower_mass = 1.0
        
        if self.offshore:
            self.d_cost_d_blade_cost = 1.1 * self.blade_number
            self.d_cost_d_hub_cost = 1.1
            self.d_cost_d_nacelle_cost = 1.1
            self.d_cost_d_tower_cost = 1.1
        else:
            self.d_cost_d_blade_cost = self.blade_number
            self.d_cost_d_hub_cost = 1.0
            self.d_cost_d_nacelle_cost = 1.0
            self.d_cost_d_tower_cost = 1.0
        
        
        # lower level output assignment
        # Turbine outputs (masses)
        self.turbineVT.mass = self.turbine_mass
        self.turbineVT.RNAmass = self.blade_mass * self.blade_number + self.hub_system_mass + self.nacelle_mass
        # Rotor System
        self.turbineVT.rotor.mass = self.blade_mass * self.blade_number + self.hub_system_mass
        self.turbineVT.rotor.blades.mass = self.blade_mass * self.blade_number
        self.turbineVT.rotor.hubsystem.mass = self.hub_system_mass      
        self.turbineVT.rotor.hubsystem.hub.mass = self.hub_mass
        self.turbineVT.rotor.hubsystem.pitchsys.mass = self.pitch_system_mass
        self.turbineVT.rotor.hubsystem.spinner.mass = self.spinner_mass
        # Nacelle System
        self.turbineVT.nacelle.mass = self.nacelle_mass
        self.turbineVT.nacelle.lss.mass = self.lowSpeedShaft_mass
        self.turbineVT.nacelle.mainbearings.mass = self.bearings_mass
        self.turbineVT.nacelle.gearbox.mass = self.gearbox_mass
        self.turbineVT.nacelle.mechbrakes.mass = self.mechanicalBrakes_mass
        self.turbineVT.nacelle.generatorc.mass = self.generator_mass
        self.turbineVT.nacelle.vselectronics.mass = self.VSElectronics_mass
        self.turbineVT.nacelle.elecconnections.mass = self.electronicCabling_mass
        self.turbineVT.nacelle.hydraulics.mass = self.HVAC_mass
        self.turbineVT.nacelle.controls.mass = self.controls_mass
        self.turbineVT.nacelle.yaw.mass = self.yawSystem_mass
        self.turbineVT.nacelle.mainframe.mass = self.mainframeTotal_mass
        self.turbineVT.nacelle.nacellecover.mass = self.nacelleCover_mass
        # Tower System
        self.turbineVT.tower.mass = self.tower_mass

        # Turbine dimensions - TODO: proper sizing
        self.turbineVT.rotor.blades.length = 61.5
        self.turbineVT.rotor.blades.width = 5.0
        self.turbineVT.rotor.hubsystem.hub.diameter = 3.0
        self.turbineVT.nacelle.length = 6.0
        self.turbineVT.nacelle.height = 3.0
        self.turbineVT.nacelle.width = 3.0
        self.turbineVT.tower.height = 80.0
        self.turbineVT.tower.maxDiameter = 6.0

        # lower level output assignment
        # Turbine outputs (_costs)
        self.turbineVT.cost = self.turbine_cost
        self.turbineVT.RNAcost = self.blade_cost * self.blade_number + self.hub_system_cost + self.nacelle_cost
        # Rotor System
        self.turbineVT.rotor.cost = self.blade_cost * self.blade_number + self.hub_system_cost
        self.turbineVT.rotor.blades.cost = self.blade_cost * self.blade_number
        self.turbineVT.rotor.hubsystem.cost = self.hub_system_cost      
        self.turbineVT.rotor.hubsystem.hub.cost = self.hub_cost
        self.turbineVT.rotor.hubsystem.pitchsys.cost = self.pitch_system_cost
        self.turbineVT.rotor.hubsystem.spinner.cost = self.spinner_cost
        # Nacelle System
        self.turbineVT.nacelle.cost = self.nacelle_cost
        self.turbineVT.nacelle.lss.cost = self.lowSpeedShaft_cost
        self.turbineVT.nacelle.mainbearings.cost = self.bearings_cost
        self.turbineVT.nacelle.gearbox.cost = self.gearbox_cost
        self.turbineVT.nacelle.mechbrakes.cost = self.mechanicalBrakes_cost
        self.turbineVT.nacelle.generatorc.cost = self.generator_cost
        self.turbineVT.nacelle.vselectronics.cost = self.VSElectronics_cost
        self.turbineVT.nacelle.elecconnections.cost = self.electronicCabling_cost
        self.turbineVT.nacelle.hydraulics.cost = self.HVAC_cost
        self.turbineVT.nacelle.controls.cost = self.controls_cost
        self.turbineVT.nacelle.yaw.cost = self.yawSystem_cost
        self.turbineVT.nacelle.mainframe.cost = self.mainframeTotal_cost
        self.turbineVT.nacelle.nacellecover.cost = self.nacelleCover_cost
        # Tower System
        self.turbineVT.tower.cost = self.tower_cost

    def list_deriv_vars(self):

        inputs=('blade_mass', 'hub_system_mass', 'nacelle_mass', 'tower_mass', \
                'blade_cost', 'hub_system_cost', 'nacelle_cost', 'tower_cost')
        
        outputs = ('turbine_mass', 'turbine_cost')
        
        return inputs, outputs
        
    def provideJ(self):
        
        self.J = np.array([[self.d_mass_d_blade_mass, self.d_mass_d_hub_mass, self.d_mass_d_nacelle_mass, self.d_mass_d_tower_mass, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_cost_d_blade_cost, self.d_cost_d_hub_cost, self.d_cost_d_nacelle_cost, self.d_cost_d_tower_cost]])
        
        return self.J
  
#-----------------------------------------------------------------

def example():

    # simple test of module
    '''trb = tcc_csm_component()
    trb.rotor_diameter = 126.0
    trb.blade_number = 3
    trb.hub_height = 90.0    
    trb.machine_rating = 5000.0
    trb.execute()'''

    # simple test of module
    trb = tcc_csm_assembly()
    trb.rotor_diameter = 126.0
    trb.advanced_blade = True
    trb.blade_number = 3
    trb.hub_height = 90.0    
    trb.machine_rating = 5000.0
    trb.offshore = True
    trb.year = 2009
    trb.month = 12

    # Rotor force calculations for nacelle inputs
    # Compute air density (todo: this is redundant from csm AEP, calculation of environmental variables of interest should probably be its own model)        
    ssl_pa     = 101300  # std sea-level pressure in Pa
    gas_const  = 287.15  # gas constant for air in J/kg/K
    gravity    = 9.80665 # standard gravity in m/sec/sec
    lapse_rate = 0.0065  # temp lapse rate in K/m
    ssl_temp   = 288.15  # std sea-level temp in K

    maxTipSpd = 80.0
    maxEfficiency = 0.90201
    ratedWindSpd = 11.5064
    altitude = 0.0
    thrustCoeff = 0.50
    hubHeight = trb.hub_height
    rotorDiam = trb.rotor_diameter
    machineRating = trb.machine_rating
    
    airDensity = (ssl_pa * (1-((lapse_rate*(altitude + hubHeight))/ssl_temp))**(gravity/(lapse_rate*gas_const))) / \
        (gas_const*(ssl_temp-lapse_rate*(altitude + hubHeight)))
    ratedHubPower  = machineRating / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*rotorDiam)) * (60.0 / (2*np.pi))
    trb.rotor_thrust  = airDensity * thrustCoeff * np.pi * rotorDiam**2 * (ratedWindSpd**2) / 8
    trb.rotor_torque = ratedHubPower/(rotorSpeed*(np.pi/30))*1000   # NREL internal version

    trb.execute()
    
    print "Offshore turbine in 20 m of water"
    print "Turbine mass: {0}".format(trb.turbine_mass)
    print "Turbine cost: {0}".format(trb.turbine_cost)
    print "Turbine variable tree:"
    trb.tcc.turbineVT.printVT()
    print

if __name__ == "__main__":

    example()