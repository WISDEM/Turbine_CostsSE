"""
tcc_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_tcc_asym import BaseTurbineCapitalCostModel, BaseTCCAggregator
from fusedwind.vartrees.varTrees import Turbine

from NREL_CSM.csmTurbine import csmTurbine
from NREL_CSM.csmDriveEfficiency import DrivetrainEfficiencyModel, csmDriveEfficiency

# --------------------------------------------------------------------

class tcc_csm_assembly(BaseTurbineCapitalCostModel):

    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    machine_rating = Float(5000.0, units = 'kW', iotype='in', desc = 'rated power of wind turbine')
    hub_height = Float(90.0, units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')

    # Parameters
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')

    def __init__(self):

        super(tcc_csm_assembly, self).__init__()

    def configure(self):

        super(tcc_csm_assembly,self).configure()

        self.replace('tcc', tcc_csm_component())
        
        self.connect('rotor_diameter', 'tcc.rotor_diameter')
        self.connect('machine_rating', 'tcc.machine_rating')
        self.connect('hub_height', 'tcc.hub_height')
        self.connect('blade_number', 'tcc.blade_number')
        
        self.create_passthrough('tcc.advanced_blade')
        self.create_passthrough('tcc.max_tip_speed')
        self.create_passthrough('tcc.rated_wind_speed')
        self.create_passthrough('tcc.thrust_coefficient')
        self.create_passthrough('tcc.drivetrain_design')
        self.create_passthrough('tcc.crane')
        self.create_passthrough('tcc.advanced_bedplate')
        self.create_passthrough('tcc.max_efficiency')
        self.create_passthrough('tcc.advancedTower')
        self.create_passthrough('tcc.altitude')
        self.create_passthrough('tcc.sea_depth')
        self.create_passthrough('tcc.year')
        self.create_passthrough('tcc.month')
        
        self.create_passthrough('tcc.turbineVT')
        self.create_passthrough('tcc.turbine_mass')

    def execute(self):

        print "In {0}.execute()...".format(self.__class__)

        super(tcc_csm_assembly, self).execute()  # will actually run the workflow

#------------------------------------------------------------------

class tcc_csm_component(BaseTCCAggregator):

    # ---- Design Variables --------------
    
    # System Level Inputs
    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    machine_rating = Float(5000.0, units = 'kW', iotype='in', desc = 'rated power of wind turbine')
    hub_height = Float(90.0, units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')

    # Parameters
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')

    # Model Specific inputs
    # rotor
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')
    max_tip_speed = Float(80.0, units = 'm/s', iotype='in', desc= 'maximum allowable tip speed for the rotor')
    rated_wind_speed = Float(11.5064, units = 'm / s', iotype='in', desc='wind speed for rated power') 
    thrust_coefficient = Float(0.5, iotype = 'in', desc = 'thrust coefficient for rotor at rated power')
    # drivetrain
    drivetrain_design = Int(1, iotype='in', desc= 'drivetrain design type 1 = 3-stage geared, 2 = single-stage geared, 3 = multi-generator, 4 = direct drive')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of nacelle service crane')
    advanced_bedplate = Int(0, iotype='in', desc= 'type of bedplate design 0 = traditional, 1 = modular, 2 = advanced')
    max_efficiency = Float(0.902, iotype='in', desc = 'maximum efficiency of drivetrain')
    # tower/substructure
    advancedTower = Bool(False, iotype='in', desc='boolean for use of advanced tower configuration')
    
    # Plant Configuration
    altitude = Float(0.0, units = 'm', iotype='in', desc = 'altitude of onshore wind turbine')
    sea_depth = Float(20.0, units = 'm', iotype='in', desc = 'sea depth for offshore wind project')
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
    turbine_mass = Float(0.0, units='kg', iotype='out', desc='turbine mass')
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

    def execute(self):
        """
        Execute Turbine Capital _costs Model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)

        #initialize csmTurbine model
        self.turb = csmTurbine()

        self.turb.compute(self.hub_height, self.machine_rating, self.max_tip_speed, self.rotor_diameter, self.drivetrain_design, self.blade_number, self.max_efficiency, self.rated_wind_speed, self.altitude, \
            self.thrust_coefficient, self.sea_depth, self.crane, self.advanced_blade, self.advanced_bedplate, self.advancedTower, self.year, self.month)

        # high level output assignment
        self.turbine_mass = self.turb.getMass()
        self.turbine_cost = self.turb.getCost()
        
        # lower level output assignment
        # Turbine outputs (masses)
        self.turbineVT.mass = self.turbine_mass
        self.turbineVT.RNAmass = self.turb.blades.getMass() * self.blade_number + self.turb.hub.getMass() + self.turb.nac.getMass()
        # Rotor System
        self.turbineVT.rotor.mass = self.turb.blades.getMass() * self.blade_number + self.turb.hub.getMass()
        self.turbineVT.rotor.blades.mass = self.turb.blades.getMass() * self.blade_number
        self.turbineVT.rotor.hubsystem.mass = self.turb.hub.getMass()      
        [self.turbineVT.rotor.hubsystem.hub.mass,  self.turbineVT.rotor.hubsystem.pitchsys.mass, self.turbineVT.rotor.hubsystem.spinner.mass] = \
                  self.turb.hub.getHubComponentMasses()
        # Nacelle System
        self.turbineVT.nacelle.mass = self.turb.nac.getMass()
        [self.turbineVT.nacelle.lss.mass, self.turbineVT.nacelle.mainbearings.mass, self.turbineVT.nacelle.gearbox.mass, self.turbineVT.nacelle.mechbrakes.mass, \
         self.turbineVT.nacelle.generatorc.mass,  self.turbineVT.nacelle.vselectronics.mass, self.turbineVT.nacelle.elecconnections.mass, self.turbineVT.nacelle.hydraulics.mass, \
         self.turbineVT.nacelle.controls.mass, self.turbineVT.nacelle.yaw.mass, self.turbineVT.nacelle.mainframe.mass, self.turbineVT.nacelle.nacellecover.mass] = \
                  self.turb.nac.getNacelleComponentMasses()
        # Tower System
        self.turbineVT.tower.mass = self.turb.tower.getMass()

        # lower level output assignment
        # Turbine outputs (_costs)
        self.turbineVT.cost = self.turbine_cost
        self.turbineVT.RNAcost = self.turb.blades.getCost() * self.blade_number + self.turb.hub.getCost() + self.turb.nac.getCost()
        # Rotor System
        self.turbineVT.rotor.cost = self.turb.blades.getCost() * self.blade_number + self.turb.hub.getCost()
        self.turbineVT.rotor.blades.cost = self.turb.blades.getCost() * self.blade_number
        self.turbineVT.rotor.hubsystem.cost = self.turb.hub.getCost()      
        [self.turbineVT.rotor.hubsystem.hub.cost,  self.turbineVT.rotor.hubsystem.pitchsys.cost, self.turbineVT.rotor.hubsystem.spinner.cost] = \
                  self.turb.hub.getHubComponentCosts()
        # Nacelle System
        self.turbineVT.nacelle.cost = self.turb.nac.getCost()
        [self.turbineVT.nacelle.lss.cost, self.turbineVT.nacelle.mainbearings.cost, self.turbineVT.nacelle.gearbox.cost, self.turbineVT.nacelle.mechbrakes.cost, \
         self.turbineVT.nacelle.generatorc.cost,  self.turbineVT.nacelle.vselectronics.cost, self.turbineVT.nacelle.elecconnections.cost, self.turbineVT.nacelle.hydraulics.cost, \
         self.turbineVT.nacelle.controls.cost, self.turbineVT.nacelle.yaw.cost, self.turbineVT.nacelle.mainframe.cost, self.turbineVT.nacelle.nacellecover.cost] = \
                  self.turb.nac.getNacelleComponentCosts()
        # Tower System
        self.turbineVT.tower.cost = self.turb.tower.getCost()
        
        # Turbine outputs (dimensions - simplified for csm mass models where used)
        # Rotor System
        self.turbineVT.rotor.hubsystem.hub.diameter = self.rotor_diameter * 0.02381 # simple formula based on 5 MW ratio
        self.turbineVT.rotor.blades.length = (self.rotor_diameter - self.turbineVT.rotor.hubsystem.hub.diameter) / 2.0
        self.turbineVT.rotor.blades.width = self.turbineVT.rotor.blades.length * 0.037398 # simple formula based on 5 MW ratio
        # Drivetrain System
        self.turbineVT.nacelle.length = self.rotor_diameter * 0.1349 # simple formula based on 5 MW ratio
        self.turbineVT.nacelle.height = self.turbineVT.nacelle.length * 0.3235 # simple formula based on 5 MW ratio
        self.turbineVT.nacelle.width = self.turbineVT.nacelle.length * 0.3235 # simple formula based on 5 MW ratio
        # Tower System
        if self.sea_depth > 0:
          self.turbineVT.tower.height = self.hub_height - (self.sea_depth + 10.0) # simplified formula
        else:
          self.turbineVT.tower.height = self.hub_height # simplified formula
        self.turbineVT.tower.maxDiameter = self.turbineVT.tower.height * 0.072289 # simple formula based on 5 MW ratio
           
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
    trb.blade_number = 3
    trb.hub_height = 90.0    
    trb.machine_rating = 5000.0
    trb.execute()
    
    print "Offshore turbine in 20 m of water"
    print "Turbine mass: {0}".format(trb.turbine_mass)
    print "Turbine cost: {0}".format(trb.turbine_cost)
    print "Turbine variable tree:"
    trb.tcc.turbineVT.printVT()
    print

    # Onshore turbine    
    trb.sea_depth = 0.0
    trb.execute()

    print "Onshore turbine"
    print "Turbine mass: {0}".format(trb.turbine_mass)
    print "Turbine cost: {0}".format(trb.turbine_cost)    
    print "Turbine variable tree:"
    trb.tcc.turbineVT.printVT()

if __name__ == "__main__":

    example()