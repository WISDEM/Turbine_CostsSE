"""
nacelle_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from NREL_CSM.csmNacelle import csmNacelle

class nacelle_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # Rotor
    rotor_diameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotor_mass = Float(123193.3010, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    max_rotor_speed = Float(12.1260909, iotype='in', units='rpm', desc='rotor speed at rated power')
    max_rotor_thrust = Float(500930.0837, iotype='in', units='N', desc='maximum thurst from rotor')    
    max_rotor_torque = Float(4365248.7375, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    # Drivetrain
    drivetrain_design = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advanced_bedplate = Int(0, iotype='in', desc= 'indicator for drivetrain bedplate design 0 - conventional')   
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')
    offshore = Bool(False, iotype='in', desc = 'boolean for land or offshore wind project')

    # ------------- Outputs -------------- 
   
    # system masses
    nacelle_mass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    lowSpeedShaft_mass = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft mass')
    bearings_mass = Float(0.0, units='kg', iotype='out', desc= 'bearings system mass')
    gearbox_mass = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing mass')
    mechanicalBrake_mass = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generator_mass = Float(0.0, units='kg', iotype='out', desc= 'generator and housing mass')
    VSElectronics_mass = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics mass')
    yawSystem_mass = Float(0.0, units='kg', iotype='out', desc= 'yaw system mass')
    mainframeTotal_mass = Float(0.0, units='kg', iotype='out', desc= 'mainframe total mass including bedplate')
    electronicCabling_mass = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling mass')
    HVAC_mass = Float(0.0, units='kg', iotype='out', desc= 'HVAC system mass')
    nacelleCover_mass = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover mass')
    controls_mass = Float(0.0, units='kg', iotype='out', desc= 'control system mass')

    # system costs
    nacelle_cost = Float(0.0, units='USD', iotype='out', desc='nacelle cost')
    lowSpeedShaft_cost = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft _cost')
    bearings_cost = Float(0.0, units='kg', iotype='out', desc= 'bearings system _cost')
    gearbox_cost = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing _cost')
    mechanicalBrake_cost = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes _cost')
    generator_cost = Float(0.0, units='kg', iotype='out', desc= 'generator and housing _cost')
    VSElectronics_cost = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics _cost')
    yawSystem_cost = Float(0.0, units='kg', iotype='out', desc= 'yaw system _cost')
    mainframeTotal_cost = Float(0.0, units='kg', iotype='out', desc= 'mainframe total _cost including bedplate')
    electronicCabling_cost = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling _cost')
    HVAC_cost = Float(0.0, units='kg', iotype='out', desc= 'HVAC system _cost')
    nacelleCover_cost = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover _cost')
    controls_cost = Float(0.0, units='kg', iotype='out', desc= 'control system _cost')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL _cost and Scaling model data (csmNacelle.py).

        Parameters
        ----------
        rotor_diameter : float
          diameter of the rotor [m]
        rotor_mass : float
          mass of rotor including blades and hub [kg]
        max_rotor_speed : float
          rotor speed at rated power [kW]
        max_rotor_thrust : float
          maximum thrust from rotor [N]
        max_rotor_torque : float
          torque from rotor at rated power [Nm]
        drivetrain_design : int
          drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive
        machine_rating : float
          Machine rated power [kW]
        crane : bool
          boolean for presence of a service crane up tower
        advanced_bedplate : int
          indicator for drivetrain bedplate design: 0 - conventional
        year : int
          year of project start
        month : int
          month of project start
        offshore : bool
          boolean for land or offshore wind project
        
        Returns
        -------
        nacelle_mass : float
          nacelle mass [kg]
        lowSpeedShaft_mass : float
          low speed shaft _mass [kg]
        mainBearings_mass : float
          bearings system _mass [kg]
        gearbox_mass : float
          gearbox and housing _mass [kg]
        mechanicalBrake_mass : float
          high speed shaft, coupling, and mechanical brakes _mass [kg]
        generator_mass : float
          generator and housing _mass [kg]
        VSElectronics_mass : float
          variable speed electronics _mass [kg]
        yawSystem_mass : float
          yaw system _mass [kg]
        mainframeTotal_mass : float
          mainframe total _mass including bedplate [kg]
        electronicCabling_mass : float
          electronic cabling _mass [kg]
        HVAC_mass : float
          HVAC system _mass [kg]
        nacelleCover_mass : float
          nacelle cover _mass [kg]
        controls_mass : float
          control system _mass [kg]  
        nacelle_cost : float
          nacelle cost [USD]
        lowSpeedShaft_cost : float
          low speed shaft _cost [USD]
        mainBearings_cost : float
          bearings system _cost [USD]
        gearbox_cost : float
          gearbox and housing _cost [USD]
        mechanicalBrake_cost : float
          high speed shaft, coupling, and mechanical brakes _cost [USD]
        generator_cost : float
          generator and housing _cost [USD]
        VSElectronics_cost : float
          variable speed electronics _cost [USD]
        yawSystem_cost : float
          yaw system _cost [USD]
        mainframeTotal_cost : float
          mainframe total _cost including bedplate [USD]
        electronicCabling_cost : float
          electronic cabling _cost [USD]
        HVAC_cost : float
          HVAC system _cost [USD]
        nacelleCover_cost : float
          nacelle cover _cost [USD]
        controls_cost : float
          control system _cost [USD]               
        """

        super(nacelle_csm_component, self).__init__()
        
        self.nac = csmNacelle()

    def execute(self):
        """
        Execute nacelle model of the NREL _cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1
           
        self.nac.compute(self.rotor_diameter, self.machine_rating, self.rotor_mass, self.max_rotor_speed, \
                    self.max_rotor_thrust, self.max_rotor_torque, self.drivetrain_design, offshore, \
                    self.crane, self.advanced_bedplate, self.year, self.month)

        self.nacelle_cost = self.nac.getCost()
        self.nacelle_mass = self.nac.getMass()

        [self.lowSpeedShaft_mass, self.bearings_mass, self.gearbox_mass, self.mechanicalBrake_mass, self.generator_mass, \
         self.VSElectronics_mass, self.electronicCabling_mass, self.HVAC_mass, \
         self.controls_mass, self.yawSystem_mass, self.mainframeTotal_mass, self.nacelleCover_mass] = \
                self.nac.getNacelleComponentMasses()

        [self.lowSpeedShaft_cost, self.bearings_cost, self.gearbox_cost, self.mechanicalBrake_cost, self.generator_cost, \
         self.VSElectronics_cost, self.electronicCabling_cost, self.HVAC_cost, \
         self.controls_cost, self.yawSystem_cost, self.mainframeTotal_cost, self.nacelleCover_cost] = \
                self.nac.getNacelleComponentCosts() 
           
#-----------------------------------------------------------------

class nacelle_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # Rotor
    rotor_diameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotor_mass = Float(123193.30, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    max_rotor_speed = Float(12.12609, iotype='in', units='rpm', desc='rotor speed at rated power')
    max_rotor_thrust = Float(500930.1, iotype='in', units='N', desc='maximum thurst from rotor')    
    max_rotor_torque = Float(4365249, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    # Drivetrain
    drivetrain_design = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advanced_bedplate = Int(1, iotype='in', desc= 'indicator for drivetrain bedplate design 1 - conventional')   
    
    # Plant Configuration
    offshore = Bool(False, iotype='in', desc = 'boolean for land or offshore wind project')

    # ------------- Outputs -------------- 
  
    # system masses
    nacelle_mass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    lowSpeedShaft_mass = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft mass')
    bearings_mass = Float(0.0, units='kg', iotype='out', desc= 'bearings system mass')
    gearbox_mass = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing mass')
    mechanicalBrake_mass = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generator_mass = Float(0.0, units='kg', iotype='out', desc= 'generator and housing mass')
    VSElectronics_mass = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics mass')
    yawSystem_mass = Float(0.0, units='kg', iotype='out', desc= 'yaw system mass')
    mainframeTotal_mass = Float(0.0, units='kg', iotype='out', desc= 'mainframe total mass including bedplate')
    electronicCabling_mass = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling mass')
    HVAC_mass = Float(0.0, units='kg', iotype='out', desc= 'HVAC system mass')
    nacelleCover_mass = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover mass')
    controls_mass = Float(0.0, units='kg', iotype='out', desc= 'control system mass')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL _cost and Scaling model data (csmNacelle.py).

        Parameters
        ----------
        rotor_diameter : float
          diameter of the rotor [m]
        rotor_mass : float
          mass of rotor including blades and hub [kg]
        max_rotor_speed : float
          rotor speed at rated power [kW]
        max_rotor_thrust : float
          maximum thrust from rotor [N]
        max_rotor_torque : float
          torque from rotor at rated power [Nm]
        drivetrain_design : int
          drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive
        machine_rating : float
          Machine rated power [kW]
        crane : bool
          boolean for presence of a service crane up tower
        advanced_bedplate : int
          indicator for drivetrain bedplate design: 0 - conventional
        offshore : bool
          boolean for land or offshore wind project
        
        Returns
        -------
        nacelle_mass : float
          nacelle mass [kg]
        lowSpeedShaft_mass : float
          low speed shaft _mass [kg]
        mainBearings_mass : float
          bearings system _mass [kg]
        gearbox_mass : float
          gearbox and housing _mass [kg]
        mechanicalBrake_mass : float
          high speed shaft, coupling, and mechanical brakes _mass [kg]
        generator_mass : float
          generator and housing _mass [kg]
        VSElectronics_mass : float
          variable speed electronics _mass [kg]
        yawSystem_mass : float
          yaw system _mass [kg]
        mainframeTotal_mass : float
          mainframe total _mass including bedplate [kg]
        electronicCabling_mass : float
          electronic cabling _mass [kg]
        HVAC_mass : float
          HVAC system _mass [kg]
        nacelleCover_mass : float
          nacelle cover _mass [kg]
        controls_mass : float
          control system _mass [kg]              
        """
        super(nacelle_mass_csm_component, self).__init__()
        
        self.nac = csmNacelle()

    def execute(self):
        """
        Execute nacelle model of the NREL _cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1
           
        self.nac.compute_mass(self.rotor_diameter, self.machine_rating, self.rotor_mass, self.max_rotor_speed, \
                    self.max_rotor_thrust, self.max_rotor_torque, self.drivetrain_design, offshore, \
                    self.crane, self.advanced_bedplate)

        self.nacelle_mass = self.nac.getMass()

        [self.lowSpeedShaft_mass, self.bearings_mass, self.gearbox_mass, self.mechanicalBrake_mass, self.generator_mass, \
         self.VSElectronics_mass, self.electronicCabling_mass, self.HVAC_mass, \
         self.controls_mass, self.yawSystem_mass, self.mainframeTotal_mass, self.nacelleCover_mass] = \
                self.nac.getNacelleComponentMasses() 
           
#-----------------------------------------------------------------

class nacelle_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # Rotor
    rotor_diameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotor_mass = Float(123193.30, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    max_rotor_speed = Float(12.12609, iotype='in', units='rpm', desc='rotor speed at rated power')
    max_rotor_thrust = Float(500930.1, iotype='in', units='N', desc='maximum thurst from rotor')    
    max_rotor_torque = Float(4365249, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    # Drivetrain
    drivetrain_design = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower') 
    mainframe_mass = Float(93090.15, iotype='in', desc= 'mainframe mass') 
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')
    offshore = Bool(False, iotype='in', desc = 'boolean for land or offshore wind project')

    # ------------- Outputs -------------- 

    # system costs
    nacelle_cost = Float(0.0, units='USD', iotype='out', desc='nacelle cost')
    lowSpeedShaft_cost = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft _cost')
    bearings_cost = Float(0.0, units='kg', iotype='out', desc= 'bearings system _cost')
    gearbox_cost = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing _cost')
    mechanicalBrake_cost = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes _cost')
    generator_cost = Float(0.0, units='kg', iotype='out', desc= 'generator and housing _cost')
    VSElectronics_cost = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics _cost')
    yawSystem_cost = Float(0.0, units='kg', iotype='out', desc= 'yaw system _cost')
    mainframeTotal_cost = Float(0.0, units='kg', iotype='out', desc= 'mainframe total _cost including bedplate')
    electronicCabling_cost = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling _cost')
    HVAC_cost = Float(0.0, units='kg', iotype='out', desc= 'HVAC system _cost')
    nacelleCover_cost = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover _cost')
    controls_cost = Float(0.0, units='kg', iotype='out', desc= 'control system _cost')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL _cost and Scaling model data (csmNacelle.py).

        Parameters
        ----------
        rotor_diameter : float
          diameter of the rotor [m]
        rotor_mass : float
          mass of rotor including blades and hub [kg]
        max_rotor_speed : float
          rotor speed at rated power [kW]
        max_rotor_thrust : float
          maximum thrust from rotor [N]
        max_rotor_torque : float
          torque from rotor at rated power [Nm]
        drivetrain_design : int
          drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive
        machine_rating : float
          Machine rated power [kW]
        crane : bool
          boolean for presence of a service crane up tower
        mainframe_mass : float
          total mass of mainframe [kg]
        year : int
          year of project start
        month : int
          month of project start
        offshore : bool
          boolean for land or offshore wind project
        
        Returns
        -------
        nacelle_cost : float
          nacelle cost [USD]
        lowSpeedShaft_cost : float
          low speed shaft _cost [USD]
        mainBearings_cost : float
          bearings system _cost [USD]
        gearbox_cost : float
          gearbox and housing _cost [USD]
        mechanicalBrake_cost : float
          high speed shaft, coupling, and mechanical brakes _cost [USD]
        generator_cost : float
          generator and housing _cost [USD]
        VSElectronics_cost : float
          variable speed electronics _cost [USD]
        yawSystem_cost : float
          yaw system _cost [USD]
        mainframeTotal_cost : float
          mainframe total _cost including bedplate [USD]
        electronicCabling_cost : float
          electronic cabling _cost [USD]
        HVAC_cost : float
          HVAC system _cost [USD]
        nacelleCover_cost : float
          nacelle cover _cost [USD]
        controls_cost : float
          control system _cost [USD]               
        """
        super(nacelle_cost_csm_component, self).__init__()
        
        self.nac = csmNacelle()

    def execute(self):
        """
        Execute nacelle model of the NREL _cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1
           
        self.nac.compute_cost(self.rotor_diameter, self.machine_rating, self.rotor_mass, self.max_rotor_speed, \
                    self.max_rotor_thrust, self.max_rotor_torque, self.drivetrain_design, offshore, self.mainframe_mass, \
                    self.crane, self.year, self.month)

        self.nacelle_cost = self.nac.getCost()

        [self.lowSpeedShaft_cost, self.bearings_cost, self.gearbox_cost, self.mechanicalBrake_cost, self.generator_cost, \
         self.VSElectronics_cost, self.electronicCabling_cost, self.HVAC_cost, \
         self.controls_cost, self.yawSystem_cost, self.mainframeTotal_cost, self.nacelleCover_cost] = \
                self.nac.getNacelleComponentCosts() 
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    nac = nacelle_csm_component()
        
    # First test
    nac.rotor_diameter = 126.0
    nac.machine_rating = 5000.0
    nac.rotor_mass = 123193.30
    nac.max_rotor_speed = 12.12609
    nac.max_rotor_thrust = 500930.1
    nac.max_rotor_torque = 4365249
    nac.drivetrain_design = 1
    nac.offshore = False
    nac.crane=True
    nac.advanced_bedplate=0
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    
    print "Nacelle csm component"
    print "Nacelle mass: {0}".format(nac.nacelle_mass)
    print "Nacelle cost: {0}".format(nac.nacelle_cost)
    print   
    print "lss mass: {0}".format(nac.lowSpeedShaft_mass)
    print "bearings mass: {0}".format(nac.bearings_mass)
    print "gearbox mass: {0}".format(nac.gearbox_mass)
    print "mechanical brake mass: {0}".format(nac.mechanicalBrake_mass)
    print "generator mass: {0}".format(nac.generator_mass)
    print "yaw system mass: {0}".format(nac.yawSystem_mass)
    print "mainframe total mass: {0}".format(nac.mainframeTotal_mass)
    print   
    print "lss _cost: {0}".format(nac.lowSpeedShaft_cost)
    print "bearings _cost: {0}".format(nac.bearings_cost)
    print "gearbox _cost: {0}".format(nac.gearbox_cost)
    print "mechanical brake _cost: {0}".format(nac.mechanicalBrake_cost)
    print "generator _cost: {0}".format(nac.generator_cost)
    print "yaw system _cost: {0}".format(nac.yawSystem_cost)
    print "mainframe total _cost: {0}".format(nac.mainframeTotal_cost)

    # simple test of module

    nac = nacelle_mass_csm_component()
        
    # First test
    nac.rotor_diameter = 126.0
    nac.machine_rating = 5000.0
    nac.rotor_mass = 123193.30
    nac.max_rotor_speed = 12.12609
    nac.max_rotor_thrust = 500930.1
    nac.max_rotor_torque = 4365249
    nac.drivetrain_design = 1
    nac.offshore = False
    nac.crane=True
    nac.advanced_bedplate=0
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    print
    print
    print "Nacelle mass csm component"
    print "Nacelle mass: {0}".format(nac.nacelle_mass)
    print   
    print "lss mass: {0}".format(nac.lowSpeedShaft_mass)
    print "bearings mass: {0}".format(nac.bearings_mass)
    print "gearbox mass: {0}".format(nac.gearbox_mass)
    print "mechanical brake mass: {0}".format(nac.mechanicalBrake_mass)
    print "generator mass: {0}".format(nac.generator_mass)
    print "yaw system mass: {0}".format(nac.yawSystem_mass)
    print "mainframe total mass: {0}".format(nac.mainframeTotal_mass)
   
    # simple test of module

    nac = nacelle_cost_csm_component()
        
    # First test
    nac.rotor_diameter = 126.0
    nac.machine_rating = 5000.0
    nac.rotor_mass = 123193.30
    nac.max_rotor_speed = 12.12609
    nac.max_rotor_thrust = 500930.1
    nac.max_rotor_torque = 4365249
    nac.drivetrain_design = 1
    nac.offshore = False
    nac.crane=True
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    print
    print
    print "Nacelle csm cost component"
    print "Nacelle cost: {0}".format(nac.nacelle_cost)
    print   
    print "lss _cost: {0}".format(nac.lowSpeedShaft_cost)
    print "bearings _cost: {0}".format(nac.bearings_cost)
    print "gearbox _cost: {0}".format(nac.gearbox_cost)
    print "mechanical brake _cost: {0}".format(nac.mechanicalBrake_cost)
    print "generator _cost: {0}".format(nac.generator_cost)
    print "yaw system _cost: {0}".format(nac.yawSystem_cost)
    print "mainframe total _cost: {0}".format(nac.mainframeTotal_cost) 


if __name__ == "__main__":

    example()