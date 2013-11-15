"""
nacelle_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.models.csm.csmNacelle import csmNacelle

class nacelle_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # Rotor
    rotorDiameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotorMass = Float(123193.3010, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    maxRotorSpeed = Float(12.1260909, iotype='in', units='rpm', desc='rotor speed at rated power')
    maxRotorThrust = Float(500930.0837, iotype='in', units='N', desc='maximum thurst from rotor')    
    maxRotorTorque = Float(4365248.7375, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    # Drivetrain
    drivetrainDesign = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    ratedPower = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advancedBedplate = Int(0, iotype='in', desc= 'indicator for drivetrain bedplate design 0 - conventional')   
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')
    offshore = Bool(False, iotype='in', desc = 'boolean for land or offshore wind project')

    # ------------- Outputs -------------- 
   
    # system masses
    nacelleMass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    lowSpeedShaftMass = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft mass')
    bearingsMass = Float(0.0, units='kg', iotype='out', desc= 'bearings system mass')
    gearboxMass = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing mass')
    mechanicalBrakeMass = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generatorMass = Float(0.0, units='kg', iotype='out', desc= 'generator and housing mass')
    VSElectronicsMass = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics mass')
    yawSystemMass = Float(0.0, units='kg', iotype='out', desc= 'yaw system mass')
    mainframeTotalMass = Float(0.0, units='kg', iotype='out', desc= 'mainframe total mass including bedplate')
    electronicCablingMass = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling mass')
    HVACMass = Float(0.0, units='kg', iotype='out', desc= 'HVAC system mass')
    nacelleCoverMass = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover mass')
    controlsMass = Float(0.0, units='kg', iotype='out', desc= 'control system mass')

    # system costs
    nacelleCost = Float(0.0, units='USD', iotype='out', desc='nacelle cost')
    lowSpeedShaftCost = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft Cost')
    bearingsCost = Float(0.0, units='kg', iotype='out', desc= 'bearings system Cost')
    gearboxCost = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing Cost')
    mechanicalBrakeCost = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes Cost')
    generatorCost = Float(0.0, units='kg', iotype='out', desc= 'generator and housing Cost')
    VSElectronicsCost = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics Cost')
    yawSystemCost = Float(0.0, units='kg', iotype='out', desc= 'yaw system Cost')
    mainframeTotalCost = Float(0.0, units='kg', iotype='out', desc= 'mainframe total Cost including bedplate')
    electronicCablingCost = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling Cost')
    HVACCost = Float(0.0, units='kg', iotype='out', desc= 'HVAC system Cost')
    nacelleCoverCost = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover Cost')
    controlsCost = Float(0.0, units='kg', iotype='out', desc= 'control system Cost')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL Cost and Scaling model data (csmNacelle.py).

        Parameters
        ----------
        rotorDiameter : float
          diameter of the rotor [m]
        rotorMass : float
          mass of rotor including blades and hub [kg]
        maxRotorSpeed : float
          rotor speed at rated power [kW]
        maxRotorThrust : float
          maximum thrust from rotor [N]
        maxRotorTorque : float
          torque from rotor at rated power [Nm]
        drivetrainDesign : int
          drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive
        ratedPower : float
          Machine rated power [kW]
        crane : bool
          boolean for presence of a service crane up tower
        advancedBedplate : int
          indicator for drivetrain bedplate design: 0 - conventional
        year : int
          year of project start
        month : int
          month of project start
        offshore : bool
          boolean for land or offshore wind project
        
        Returns
        -------
        nacelleMass : float
          nacelle mass [kg]
        lowSpeedShaftMass : float
          low speed shaft Mass [kg]
        mainBearingsMass : float
          bearings system Mass [kg]
        gearboxMass : float
          gearbox and housing Mass [kg]
        mechanicalBrakeMass : float
          high speed shaft, coupling, and mechanical brakes Mass [kg]
        generatorMass : float
          generator and housing Mass [kg]
        VSElectronicsMass : float
          variable speed electronics Mass [kg]
        yawSystemMass : float
          yaw system Mass [kg]
        mainframeTotalMass : float
          mainframe total Mass including bedplate [kg]
        electronicCablingMass : float
          electronic cabling Mass [kg]
        HVACMass : float
          HVAC system Mass [kg]
        nacelleCoverMass : float
          nacelle cover Mass [kg]
        controlsMass : float
          control system Mass [kg]  
        nacelleCost : float
          nacelle cost [USD]
        lowSpeedShaftCost : float
          low speed shaft Cost [USD]
        mainBearingsCost : float
          bearings system Cost [USD]
        gearboxCost : float
          gearbox and housing Cost [USD]
        mechanicalBrakeCost : float
          high speed shaft, coupling, and mechanical brakes Cost [USD]
        generatorCost : float
          generator and housing Cost [USD]
        VSElectronicsCost : float
          variable speed electronics Cost [USD]
        yawSystemCost : float
          yaw system Cost [USD]
        mainframeTotalCost : float
          mainframe total Cost including bedplate [USD]
        electronicCablingCost : float
          electronic cabling Cost [USD]
        HVACCost : float
          HVAC system Cost [USD]
        nacelleCoverCost : float
          nacelle cover Cost [USD]
        controlsCost : float
          control system Cost [USD]               
        """

        super(nacelle_csm_component, self).__init__()
        
        self.nac = csmNacelle()

    def execute(self):
        """
        Execute nacelle model of the NREL Cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1
           
        self.nac.compute(self.rotorDiameter, self.ratedPower, self.rotorMass, self.maxRotorSpeed, \
                    self.maxRotorThrust, self.maxRotorTorque, self.drivetrainDesign, offshore, \
                    self.crane, self.advancedBedplate, self.year, self.month)

        self.nacelleCost = self.nac.getCost()
        self.nacelleMass = self.nac.getMass()

        [self.lowSpeedShaftMass, self.bearingsMass, self.gearboxMass, self.mechanicalBrakeMass, self.generatorMass, \
         self.VSElectronicsMass, self.electronicCablingMass, self.HVACMass, \
         self.controlsMass, self.yawSystemMass, self.mainframeTotalMass, self.nacelleCoverMass] = \
                self.nac.getNacelleComponentMasses()

        [self.lowSpeedShaftCost, self.bearingsCost, self.gearboxCost, self.mechanicalBrakeCost, self.generatorCost, \
         self.VSElectronicsCost, self.electronicCablingCost, self.HVACCost, \
         self.controlsCost, self.yawSystemCost, self.mainframeTotalCost, self.nacelleCoverCost] = \
                self.nac.getNacelleComponentCosts() 
           
#-----------------------------------------------------------------

class nacelle_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # Rotor
    rotorDiameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotorMass = Float(123193.30, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    maxRotorSpeed = Float(12.12609, iotype='in', units='rpm', desc='rotor speed at rated power')
    maxRotorThrust = Float(500930.1, iotype='in', units='N', desc='maximum thurst from rotor')    
    maxRotorTorque = Float(4365249, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    # Drivetrain
    drivetrainDesign = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    ratedPower = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advancedBedplate = Int(1, iotype='in', desc= 'indicator for drivetrain bedplate design 1 - conventional')   
    
    # Plant Configuration
    offshore = Bool(False, iotype='in', desc = 'boolean for land or offshore wind project')

    # ------------- Outputs -------------- 
  
    # system masses
    nacelleMass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    lowSpeedShaftMass = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft mass')
    bearingsMass = Float(0.0, units='kg', iotype='out', desc= 'bearings system mass')
    gearboxMass = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing mass')
    mechanicalBrakeMass = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generatorMass = Float(0.0, units='kg', iotype='out', desc= 'generator and housing mass')
    VSElectronicsMass = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics mass')
    yawSystemMass = Float(0.0, units='kg', iotype='out', desc= 'yaw system mass')
    mainframeTotalMass = Float(0.0, units='kg', iotype='out', desc= 'mainframe total mass including bedplate')
    electronicCablingMass = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling mass')
    HVACMass = Float(0.0, units='kg', iotype='out', desc= 'HVAC system mass')
    nacelleCoverMass = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover mass')
    controlsMass = Float(0.0, units='kg', iotype='out', desc= 'control system mass')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL Cost and Scaling model data (csmNacelle.py).

        Parameters
        ----------
        rotorDiameter : float
          diameter of the rotor [m]
        rotorMass : float
          mass of rotor including blades and hub [kg]
        maxRotorSpeed : float
          rotor speed at rated power [kW]
        maxRotorThrust : float
          maximum thrust from rotor [N]
        maxRotorTorque : float
          torque from rotor at rated power [Nm]
        drivetrainDesign : int
          drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive
        ratedPower : float
          Machine rated power [kW]
        crane : bool
          boolean for presence of a service crane up tower
        advancedBedplate : int
          indicator for drivetrain bedplate design: 0 - conventional
        offshore : bool
          boolean for land or offshore wind project
        
        Returns
        -------
        nacelleMass : float
          nacelle mass [kg]
        lowSpeedShaftMass : float
          low speed shaft Mass [kg]
        mainBearingsMass : float
          bearings system Mass [kg]
        gearboxMass : float
          gearbox and housing Mass [kg]
        mechanicalBrakeMass : float
          high speed shaft, coupling, and mechanical brakes Mass [kg]
        generatorMass : float
          generator and housing Mass [kg]
        VSElectronicsMass : float
          variable speed electronics Mass [kg]
        yawSystemMass : float
          yaw system Mass [kg]
        mainframeTotalMass : float
          mainframe total Mass including bedplate [kg]
        electronicCablingMass : float
          electronic cabling Mass [kg]
        HVACMass : float
          HVAC system Mass [kg]
        nacelleCoverMass : float
          nacelle cover Mass [kg]
        controlsMass : float
          control system Mass [kg]              
        """
        super(nacelle_mass_csm_component, self).__init__()
        
        self.nac = csmNacelle()

    def execute(self):
        """
        Execute nacelle model of the NREL Cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1
           
        self.nac.computeMass(self.rotorDiameter, self.ratedPower, self.rotorMass, self.maxRotorSpeed, \
                    self.maxRotorThrust, self.maxRotorTorque, self.drivetrainDesign, offshore, \
                    self.crane, self.advancedBedplate)

        self.nacelleMass = self.nac.getMass()

        [self.lowSpeedShaftMass, self.bearingsMass, self.gearboxMass, self.mechanicalBrakeMass, self.generatorMass, \
         self.VSElectronicsMass, self.electronicCablingMass, self.HVACMass, \
         self.controlsMass, self.yawSystemMass, self.mainframeTotalMass, self.nacelleCoverMass] = \
                self.nac.getNacelleComponentMasses() 
           
#-----------------------------------------------------------------

class nacelle_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # Rotor
    rotorDiameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotorMass = Float(123193.30, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    maxRotorSpeed = Float(12.12609, iotype='in', units='rpm', desc='rotor speed at rated power')
    maxRotorThrust = Float(500930.1, iotype='in', units='N', desc='maximum thurst from rotor')    
    maxRotorTorque = Float(4365249, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    # Drivetrain
    drivetrainDesign = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    ratedPower = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower') 
    mainframeMass = Float(93090.15, iotype='in', desc= 'mainframe mass') 
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')
    offshore = Bool(False, iotype='in', desc = 'boolean for land or offshore wind project')

    # ------------- Outputs -------------- 

    # system costs
    nacelleCost = Float(0.0, units='USD', iotype='out', desc='nacelle cost')
    lowSpeedShaftCost = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft Cost')
    bearingsCost = Float(0.0, units='kg', iotype='out', desc= 'bearings system Cost')
    gearboxCost = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing Cost')
    mechanicalBrakeCost = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes Cost')
    generatorCost = Float(0.0, units='kg', iotype='out', desc= 'generator and housing Cost')
    VSElectronicsCost = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics Cost')
    yawSystemCost = Float(0.0, units='kg', iotype='out', desc= 'yaw system Cost')
    mainframeTotalCost = Float(0.0, units='kg', iotype='out', desc= 'mainframe total Cost including bedplate')
    electronicCablingCost = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling Cost')
    HVACCost = Float(0.0, units='kg', iotype='out', desc= 'HVAC system Cost')
    nacelleCoverCost = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover Cost')
    controlsCost = Float(0.0, units='kg', iotype='out', desc= 'control system Cost')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL Cost and Scaling model data (csmNacelle.py).

        Parameters
        ----------
        rotorDiameter : float
          diameter of the rotor [m]
        rotorMass : float
          mass of rotor including blades and hub [kg]
        maxRotorSpeed : float
          rotor speed at rated power [kW]
        maxRotorThrust : float
          maximum thrust from rotor [N]
        maxRotorTorque : float
          torque from rotor at rated power [Nm]
        drivetrainDesign : int
          drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive
        ratedPower : float
          Machine rated power [kW]
        crane : bool
          boolean for presence of a service crane up tower
        mainframeMass : float
          total mass of mainframe [kg]
        year : int
          year of project start
        month : int
          month of project start
        offshore : bool
          boolean for land or offshore wind project
        
        Returns
        -------
        nacelleCost : float
          nacelle cost [USD]
        lowSpeedShaftCost : float
          low speed shaft Cost [USD]
        mainBearingsCost : float
          bearings system Cost [USD]
        gearboxCost : float
          gearbox and housing Cost [USD]
        mechanicalBrakeCost : float
          high speed shaft, coupling, and mechanical brakes Cost [USD]
        generatorCost : float
          generator and housing Cost [USD]
        VSElectronicsCost : float
          variable speed electronics Cost [USD]
        yawSystemCost : float
          yaw system Cost [USD]
        mainframeTotalCost : float
          mainframe total Cost including bedplate [USD]
        electronicCablingCost : float
          electronic cabling Cost [USD]
        HVACCost : float
          HVAC system Cost [USD]
        nacelleCoverCost : float
          nacelle cover Cost [USD]
        controlsCost : float
          control system Cost [USD]               
        """
        super(nacelle_cost_csm_component, self).__init__()
        
        self.nac = csmNacelle()

    def execute(self):
        """
        Execute nacelle model of the NREL Cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1
           
        self.nac.computeCost(self.rotorDiameter, self.ratedPower, self.rotorMass, self.maxRotorSpeed, \
                    self.maxRotorThrust, self.maxRotorTorque, self.drivetrainDesign, offshore, self.mainframeMass, \
                    self.crane, self.year, self.month)

        self.nacelleCost = self.nac.getCost()

        [self.lowSpeedShaftCost, self.bearingsCost, self.gearboxCost, self.mechanicalBrakeCost, self.generatorCost, \
         self.VSElectronicsCost, self.electronicCablingCost, self.HVACCost, \
         self.controlsCost, self.yawSystemCost, self.mainframeTotalCost, self.nacelleCoverCost] = \
                self.nac.getNacelleComponentCosts() 
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    nac = nacelle_csm_component()
        
    # First test
    nac.rotorDiameter = 126.0
    nac.ratedPower = 5000.0
    nac.rotorMass = 123193.30
    nac.maxRotorSpeed = 12.12609
    nac.maxRotorThrust = 500930.1
    nac.maxRotorTorque = 4365249
    nac.drivetrainDesign = 1
    nac.offshore = False
    nac.crane=True
    nac.advancedBedplate=0
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    
    print "Nacelle csm component"
    print "Nacelle mass: {0}".format(nac.nacelleMass)
    print "Nacelle cost: {0}".format(nac.nacelleCost)
    print   
    print "lss mass: {0}".format(nac.lowSpeedShaftMass)
    print "bearings mass: {0}".format(nac.bearingsMass)
    print "gearbox mass: {0}".format(nac.gearboxMass)
    print "mechanical brake mass: {0}".format(nac.mechanicalBrakeMass)
    print "generator mass: {0}".format(nac.generatorMass)
    print "yaw system mass: {0}".format(nac.yawSystemMass)
    print "mainframe total mass: {0}".format(nac.mainframeTotalMass)
    print   
    print "lss Cost: {0}".format(nac.lowSpeedShaftCost)
    print "bearings Cost: {0}".format(nac.bearingsCost)
    print "gearbox Cost: {0}".format(nac.gearboxCost)
    print "mechanical brake Cost: {0}".format(nac.mechanicalBrakeCost)
    print "generator Cost: {0}".format(nac.generatorCost)
    print "yaw system Cost: {0}".format(nac.yawSystemCost)
    print "mainframe total Cost: {0}".format(nac.mainframeTotalCost)

    # simple test of module

    nac = nacelle_mass_csm_component()
        
    # First test
    nac.rotorDiameter = 126.0
    nac.ratedPower = 5000.0
    nac.rotorMass = 123193.30
    nac.maxRotorSpeed = 12.12609
    nac.maxRotorThrust = 500930.1
    nac.maxRotorTorque = 4365249
    nac.drivetrainDesign = 1
    nac.offshore = False
    nac.crane=True
    nac.advancedBedplate=0
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    print
    print
    print "Nacelle mass csm component"
    print "Nacelle mass: {0}".format(nac.nacelleMass)
    print   
    print "lss mass: {0}".format(nac.lowSpeedShaftMass)
    print "bearings mass: {0}".format(nac.bearingsMass)
    print "gearbox mass: {0}".format(nac.gearboxMass)
    print "mechanical brake mass: {0}".format(nac.mechanicalBrakeMass)
    print "generator mass: {0}".format(nac.generatorMass)
    print "yaw system mass: {0}".format(nac.yawSystemMass)
    print "mainframe total mass: {0}".format(nac.mainframeTotalMass)
   
    # simple test of module

    nac = nacelle_cost_csm_component()
        
    # First test
    nac.rotorDiameter = 126.0
    nac.ratedPower = 5000.0
    nac.rotorMass = 123193.30
    nac.maxRotorSpeed = 12.12609
    nac.maxRotorThrust = 500930.1
    nac.maxRotorTorque = 4365249
    nac.drivetrainDesign = 1
    nac.offshore = False
    nac.crane=True
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    print
    print
    print "Nacelle csm cost component"
    print "Nacelle cost: {0}".format(nac.nacelleCost)
    print   
    print "lss Cost: {0}".format(nac.lowSpeedShaftCost)
    print "bearings Cost: {0}".format(nac.bearingsCost)
    print "gearbox Cost: {0}".format(nac.gearboxCost)
    print "mechanical brake Cost: {0}".format(nac.mechanicalBrakeCost)
    print "generator Cost: {0}".format(nac.generatorCost)
    print "yaw system Cost: {0}".format(nac.yawSystemCost)
    print "mainframe total Cost: {0}".format(nac.mainframeTotalCost) 


if __name__ == "__main__":

    example()