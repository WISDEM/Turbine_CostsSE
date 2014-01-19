"""
nacelle_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from commonse.config import *
import numpy as np

class nacelle_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # Variables
    rotor_diameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotor_mass = Float(123193.3010, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    rotor_thrust = Float(500930.0837, iotype='in', units='N', desc='maximum thurst from rotor')    
    rotor_torque = Float(4365248.7375, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')

    # Parameters
    drivetrain_design = Int(1, iotype='in', desc = 'drivetrain configuration type 1 - 3-stage, 2 - single speed, 3 - multi-generator, 4 - direct drive')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advanced_bedplate = Int(0, iotype='in', desc= 'indicator for drivetrain bedplate design 0 - conventional')   
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    offshore = Bool(True, iotype='in', desc = 'boolean for land or offshore wind project')

    # Outputs
    nacelle_mass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    lowSpeedShaft_mass = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft mass')
    bearings_mass = Float(0.0, units='kg', iotype='out', desc= 'bearings system mass')
    gearbox_mass = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing mass')
    mechanicalBrakes_mass = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generator_mass = Float(0.0, units='kg', iotype='out', desc= 'generator and housing mass')
    VSElectronics_mass = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics mass')
    yawSystem_mass = Float(0.0, units='kg', iotype='out', desc= 'yaw system mass')
    mainframeTotal_mass = Float(0.0, units='kg', iotype='out', desc= 'mainframe total mass including bedplate')
    electronicCabling_mass = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling mass')
    HVAC_mass = Float(0.0, units='kg', iotype='out', desc= 'HVAC system mass')
    nacelleCover_mass = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover mass')
    controls_mass = Float(0.0, units='kg', iotype='out', desc= 'control system mass')

    nacelle_cost = Float(0.0, units='USD', iotype='out', desc='nacelle cost')
    lowSpeedShaft_cost = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft _cost')
    bearings_cost = Float(0.0, units='kg', iotype='out', desc= 'bearings system _cost')
    gearbox_cost = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing _cost')
    mechanicalBrakes_cost = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes _cost')
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
        mechanicalBrakes_mass : float
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
        mechanicalBrakes_cost : float
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

    def execute(self):
        """
        Execute nacelle model of the NREL _cost and Scaling Model.
        """

        print "In {0}.execute()...".format(self.__class__)

        # basic variable initialization        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1

        ppi.curr_yr = self.year
        ppi.curr_mon = self.month

        # Low Speed Shaft
        lenShaft  = 0.03 * self.rotor_diameter                                                                   
        mmtArm    = lenShaft / 5                                                                 
        bendLoad  = 1.25*9.81*self.rotor_mass                                                           
        bendMom   = bendLoad * mmtArm                                                                 
        hFact     = 0.1                                                                                    
        hollow    = 1/(1-(hFact)**4)                                                                   
        outDiam   = ((32./np.pi)*hollow*3.25*((self.rotor_torque*3./371000000.)**2+(bendMom/71070000)**2)**(0.5))**(1./3.) 
        inDiam    = outDiam * hFact 
                                                                              
        self.lowSpeedShaft_mass      = 1.25*(np.pi/4)*(outDiam**2-inDiam**2)*lenShaft*7860

        LowSpeedShaftCost2002 = 0.0998 * self.rotor_diameter ** 2.8873
        lssCostEsc     = ppi.compute('IPPI_LSS')
        
        self.lowSpeedShaft_cost = LowSpeedShaftCost2002 * lssCostEsc

        d_mass_d_outD = 1.25*(np.pi/4) * (1 - 0.1**2) * 2 * outDiam * lenShaft*7860
        d_outD_mult = ((32./np.pi)*hollow*3.25)**(1./3.) * (1./6.) * ((self.rotor_torque*3./371000000.)**2+(bendMom/71070000.)**2)**(-5./6.)
        d_outD_d_diameter = d_outD_mult * 2. * (bendMom/71070000) * (1./71070000.) * (bendLoad * 0.03 / 5)
        d_outD_d_mass = d_outD_mult * 2. * (bendMom/71070000) * (1./71070000.) * (mmtArm * 1.25 * 9.81)
        d_outD_d_torque = d_outD_mult * 2. * (self.rotor_torque*3./371000000.) * (3./371000000.)
        self.d_lss_mass_d_r_diameter = d_mass_d_outD * d_outD_d_diameter + \
                                       1.25*(np.pi/4)*(outDiam**2-inDiam**2)*7860 * 0.03
        self.d_lss_mass_d_r_mass = d_mass_d_outD * d_outD_d_mass
        self.d_lss_mass_d_r_torque = d_mass_d_outD * d_outD_d_torque

        self.d_lss_cost_d_r_diameter = lssCostEsc * 2.8873 * 0.0998 * self.rotor_diameter ** 1.8873
        
        # Gearbox
        costCoeff = [None, 16.45  , 74.101     ,   15.25697015,  0 ]
        costExp   = [None,  1.2491,  1.002     ,    1.2491    ,  0 ]
        massCoeff = [None, 65.601 , 81.63967335,  129.1702924 ,  0 ]
        massExp   = [None,  0.759 ,  0.7738    ,    0.7738    ,  0 ]

        self.gearbox_mass = massCoeff[self.drivetrain_design] * (self.rotor_torque/1000) ** massExp[self.drivetrain_design] 

        gearboxCostEsc     = ppi.compute('IPPI_GRB')        
        Gearbox2002 = costCoeff[self.drivetrain_design] * self.machine_rating ** costExp[self.drivetrain_design]  
        self.gearbox_cost = Gearbox2002 * gearboxCostEsc   
        
        if self.drivetrain_design == 4:
            self.d_gearbox_mass_d_r_torque = 0.0
            self.d_gearbox_cost_d_rating = 0.0
        else:
            self.d_gearbox_mass_d_r_torque = massExp[self.drivetrain_design]  * massCoeff[self.drivetrain_design] * ((self.rotor_torque/1000.) ** (massExp[self.drivetrain_design] - 1)) * (1/1000.)
            self.d_gearbox_cost_d_rating = gearboxCostEsc * costExp[self.drivetrain_design] * costCoeff[self.drivetrain_design] * self.machine_rating ** (costExp[self.drivetrain_design] - 1)

        # Generator
        costCoeff = [None, 65.000, 54.72533,  48.02963 , 219.3333 ] # $/kW - from 'Generators' worksheet
        massCoeff = [None, 6.4737, 10.50972,  5.343902 , 37.68400 ]
        massExp   = [None, 0.9223, 0.922300,  0.922300 , 1.000000 ]

        if (self.drivetrain_design < 4):
            self.generator_mass = massCoeff[self.drivetrain_design] * self.machine_rating ** massExp[self.drivetrain_design]   
        else:  # direct drive
            self.generator_mass = massCoeff[self.drivetrain_design] * self.rotor_torque ** massExp[self.drivetrain_design] 

        generatorCostEsc     = ppi.compute('IPPI_GEN')                                                  
        GeneratorCost2002 = costCoeff[self.drivetrain_design] * self.machine_rating 
        self.generator_cost = GeneratorCost2002 * generatorCostEsc

        if self.drivetrain_design < 4:
            self.d_generator_mass_d_r_torque = 0.0
            self.d_generator_mass_d_rating = massExp[self.drivetrain_design] * massCoeff[self.drivetrain_design] * self.machine_rating ** (massExp[self.drivetrain_design]-1)
        else:
            self.d_generator_mass_d_r_torque = massExp[self.drivetrain_design] * massCoeff[self.drivetrain_design] * self.rotor_torque ** (massExp[self.drivetrain_design]-1)
            self.d_generator_mass_d_rating = 0.0
        self.d_generator_cost_d_rating = generatorCostEsc * costCoeff[self.drivetrain_design]
        
        # Rest of the system
        
        # --- electrical connections           
        self.electronicCabling_mass = 0.0
        
        # --- bearings           
        self.bearings_mass = 0.00012266667 * (self.rotor_diameter ** 3.5) - 0.00030360 * (self.rotor_diameter ** 2.5)
        HousingMass  = self.bearings_mass 
        self.bearings_mass  += HousingMass
        
        self.d_bearings_mass_d_r_diameter = 2 * ( 3.5 * 0.00012266667 * (self.rotor_diameter ** 2.5) - 0.00030360 * 2.5 * (self.rotor_diameter ** 1.5))
        
        # --- mechanical brake           
        mechBrakeCost2002 = 1.9894 * self.machine_rating + (-0.1141)
        self.mechanicalBrakes_mass = mechBrakeCost2002 * 0.10
        
        self.d_brakes_mass_d_rating = 0.10 * 1.9894
        
        # --- variable-speed electronics
        self.VSElectronics_mass = 0.0

        # --- yaw drive bearings
        self.yawSystem_mass = 1.6 * (0.0009 * self.rotor_diameter ** 3.314)
        
        self.d_yaw_mass_d_r_diameter = 3.314 * 1.6 * (0.0009 * self.rotor_diameter ** 2.314)
        
        # --- hydraulics, cooling
        self.HVAC_mass = 0.08 * self.machine_rating
        
        self.d_hvac_mass_d_rating = 0.08

        # --- bedplate ---        
        if (self.advanced_bedplate == 0):   # not an actual option in cost and scaling model                                           
            BedplateWeightFac = 2.86  # modular
        elif (self.advanced_bedplate == 1): # test for mod-adv
            BedplateWeightFac = 2.40  # modular-advanced
        else:
            BedplateWeightFac = 0.71  # advanced

        # These RD functions from spreadsheet don't quite form a continuous composite function        
        '''if (self.rotor_diameter <= 15.0): # Removing for gradients - assuming large turbines only
            TowerTopDiam = 0.3
        elif (self.rotor_diameter <= 60.0):
            TowerTopDiam = (0.07042*self.rotor_diameter-0.715)
        else:'''
        TowerTopDiam = (12.29*self.rotor_diameter+2648)/1000

        MassFromTorque = BedplateWeightFac * 0.00368 * self.rotor_torque
        MassFromThrust      = 0.00158 * BedplateWeightFac * self.rotor_thrust * TowerTopDiam
        MassFromRotorWeight = 0.015   * BedplateWeightFac * self.rotor_mass     * TowerTopDiam
        
        # Bedplate(Length|Area) added by GNS
        BedplateLength = 1.5874 * 0.052 * self.rotor_diameter
        BedplateArea = 0.5 * BedplateLength * BedplateLength
        MassFromArea = 100 * BedplateWeightFac * BedplateArea

        # mfmCoeff[1,4] for different drivetrain configurations
        mfmCoeff = [None,22448,1.29490,1.72080,22448 ]
        mfmExp   = [None,    0,1.9525, 1.9525 ,    0 ]

        # --- nacelle totals        
        TotalMass = MassFromTorque + MassFromThrust + MassFromRotorWeight + MassFromArea
        
        if (self.drivetrain_design == 1) or (self.drivetrain_design == 4):
            self.bedplate_mass = TotalMass
        else:
            self.bedplate_mass = mfmCoeff[self.drivetrain_design] * (self.rotor_diameter ** mfmExp[self.drivetrain_design] )

        NacellePlatformsMass = .125 * self.bedplate_mass            
     
        # --- crane ---        
        if (self.crane):
            self.crane_mass =  3000.
        else:
            self.crane_mass = 0.  
            
        # --- main frame ---       
        self.mainframeTotal_mass = self.bedplate_mass + NacellePlatformsMass + self.crane_mass

        if (self.drivetrain_design == 1) or (self.drivetrain_design == 4):
            self.d_mainframe_mass_d_r_diameter = 1.125 * (((0.00158 * BedplateWeightFac * self.rotor_thrust * (12.29/1000.)) + \
                                                  (0.015   * BedplateWeightFac * self.rotor_mass * (12.29/1000.)) + \
                                                  (100 * BedplateWeightFac * 0.5 * (1.5874 * 0.052)**2. * (2 * self.rotor_diameter))))
            self.d_mainframe_mass_d_r_mass = 1.125 * (0.015   * BedplateWeightFac * TowerTopDiam)
            self.d_mainframe_mass_d_r_thrust = 1.125 * (0.00158 * BedplateWeightFac * TowerTopDiam)
            self.d_mainframe_mass_d_r_torque = 1.125 * BedplateWeightFac * 0.00368
        else:
            self.d_mainframe_mass_d_r_diameter = 1.125 * mfmCoeff[self.drivetrain_design] * \
                                                  (mfmExp[self.drivetrain_design] * self.rotor_diameter ** (mfmExp[self.drivetrain_design]-1))
            self.d_mainframe_mass_d_r_mass = 0.0
            self.d_mainframe_mass_d_r_thrust = 0.0
            self.d_mainframe_mass_d_r_torque = 0.0      

        # --- nacelle cover ---        
        nacelleCovCost2002 = 11.537 * self.machine_rating + (3849.7)
        self.nacelleCover_mass = nacelleCovCost2002 * 0.111111
        
        self.d_cover_mass_d_rating = 0.111111 * 11.537

        # --- control system ---
        self.controls_mass = 0.0

        # overall mass   
        self.nacelle_mass = self.lowSpeedShaft_mass + \
                    self.bearings_mass + \
                    self.gearbox_mass + \
                    self.mechanicalBrakes_mass + \
                    self.generator_mass + \
                    self.VSElectronics_mass + \
                    self.yawSystem_mass + \
                    self.mainframeTotal_mass + \
                    self.electronicCabling_mass + \
                    self.HVAC_mass + \
                    self.nacelleCover_mass + \
                    self.controls_mass
        
        self.d_nacelle_mass_d_r_diameter = self.d_lss_mass_d_r_diameter + self.d_bearings_mass_d_r_diameter + self.d_yaw_mass_d_r_diameter + self.d_mainframe_mass_d_r_diameter
        self.d_nacelle_mass_d_r_mass = self.d_lss_mass_d_r_mass + self.d_mainframe_mass_d_r_mass
        self.d_nacelle_mass_d_r_thrust = self.d_mainframe_mass_d_r_thrust
        self.d_nacelle_mass_d_r_torque = self.d_lss_mass_d_r_torque + self.d_gearbox_mass_d_r_torque + self.d_generator_mass_d_r_torque + self.d_mainframe_mass_d_r_torque
        self.d_nacelle_mass_d_rating = self.d_generator_mass_d_rating + self.d_brakes_mass_d_rating + self.d_hvac_mass_d_rating + self.d_cover_mass_d_rating
        
        # Rest of System Costs
        # Cost Escalators - obtained from ppi tables
        bearingCostEsc       = ppi.compute('IPPI_BRN')
        mechBrakeCostEsc     = ppi.compute('IPPI_BRK')
        VspdEtronicsCostEsc  = ppi.compute('IPPI_VSE')
        yawDrvBearingCostEsc = ppi.compute('IPPI_YAW')
        nacelleCovCostEsc    = ppi.compute('IPPI_NAC')
        hydrCoolingCostEsc   = ppi.compute('IPPI_HYD')
        mainFrameCostEsc     = ppi.compute('IPPI_MFM')
        econnectionsCostEsc  = ppi.compute('IPPI_ELC')

        # These RD functions from spreadsheet don't quite form a continuous composite function
        
        # --- electrical connections
        self.electronicCabling_cost = 40.0 * self.machine_rating # 2002
        self.electronicCabling_cost *= econnectionsCostEsc
        
        self.d_electronics_cost_d_rating = 40.0 * econnectionsCostEsc
        
        # --- bearings
        bearingMass = 0.00012266667 * (self.rotor_diameter ** 3.5) - 0.00030360 * (self.rotor_diameter ** 2.5)
        HousingMass  = bearingMass 
        brngSysCostFactor = 17.6 # $/kg
        Bearings2002 = bearingMass * brngSysCostFactor
        Housing2002  = HousingMass      * brngSysCostFactor
        self.bearings_cost = ( Bearings2002 + Housing2002 ) * bearingCostEsc
        
        self.d_bearings_cost_d_r_diameter = bearingCostEsc * brngSysCostFactor * self.d_bearings_mass_d_r_diameter
        
        # --- mechanical brake           
        mechBrakeCost2002 = 1.9894 * self.machine_rating + (-0.1141)
        self.mechanicalBrakes_cost = mechBrakeCostEsc * mechBrakeCost2002
        
        self.d_brakes_cost_d_rating = mechBrakeCostEsc * 1.9894
        
        # --- variable-speed electronics           
        VspdEtronics2002 = 79.32 * self.machine_rating
        self.VSElectronics_cost = VspdEtronics2002 * VspdEtronicsCostEsc
        
        self.d_vselectronics_cost_d_rating = VspdEtronicsCostEsc * 79.32

        # --- yaw drive bearings
        YawDrvBearing2002 = 2 * ( 0.0339 * self.rotor_diameter ** 2.9637 )
        self.yawSystem_cost = YawDrvBearing2002 * yawDrvBearingCostEsc
        
        self.d_yaw_cost_d_r_diameter = yawDrvBearingCostEsc * 2 * 2.9637 * ( 0.0339 * self.rotor_diameter ** 1.9637 )
        
        # --- hydraulics, cooling
        self.HVAC_cost = 12.0 * self.machine_rating # 2002
        self.HVAC_cost *= hydrCoolingCostEsc 
        
        self.d_hvac_cost_d_rating = hydrCoolingCostEsc * 12.0
 
        # --- control system ---   
        initControlCost = [ 35000, 55900 ]  # land, off-shore
        self.controls_cost = initControlCost[offshore] * ppi.compute('IPPI_CTL')

        # --- nacelle totals
        NacellePlatforms2002 = 8.7 * NacellePlatformsMass
        
        # --- nacelle cover ---        
        nacelleCovCost2002 = 11.537 * self.machine_rating + (3849.7)
        self.nacelleCover_cost = nacelleCovCostEsc * nacelleCovCost2002
        
        self.d_cover_cost_d_rating = nacelleCovCostEsc * 11.537
        
        # --- crane ---
        
        if (self.crane):
            self.crane_cost = 12000.
        else:
            self.crane_cost = 0.0
            
        # --- main frame ---
        # mfmCoeff[1,4] for different drivetrain configurations
        mfmCoeff = [None,9.4885,303.96,17.923,627.28 ]
        mfmExp   = [None,1.9525,1.0669,1.6716,0.8500 ]
        
        MainFrameCost2002 = mfmCoeff[self.drivetrain_design] * self.rotor_diameter ** mfmExp[self.drivetrain_design]
        BaseHardware2002  = MainFrameCost2002 * 0.7
        MainFrame2002 = ( MainFrameCost2002    + 
                          NacellePlatforms2002 + 
                          self.crane_cost       + # service crane 
                          BaseHardware2002 )
        self.mainframeTotal_cost = MainFrame2002 * mainFrameCostEsc
        
        self.d_mainframe_cost_d_r_diameter = mainFrameCostEsc * (1.7 * mfmCoeff[self.drivetrain_design] * mfmExp[self.drivetrain_design] * self.rotor_diameter ** (mfmExp[self.drivetrain_design]-1) + \
                                                                8.7 * self.d_mainframe_mass_d_r_diameter * (0.125/1.125))
        self.d_mainframe_cost_d_r_mass = mainFrameCostEsc * 8.7 * self.d_mainframe_mass_d_r_mass * (0.125/1.125)
        self.d_mainframe_cost_d_r_thrust = mainFrameCostEsc * 8.7 * self.d_mainframe_mass_d_r_thrust * (0.125/1.125)
        self.d_mainframe_cost_d_r_torque = mainFrameCostEsc * 8.7 * self.d_mainframe_mass_d_r_torque * (0.125/1.125)

        # overall system cost  
        self.nacelle_cost = self.lowSpeedShaft_cost + \
                    self.bearings_cost + \
                    self.gearbox_cost + \
                    self.mechanicalBrakes_cost + \
                    self.generator_cost + \
                    self.VSElectronics_cost + \
                    self.yawSystem_cost + \
                    self.mainframeTotal_cost + \
                    self.electronicCabling_cost + \
                    self.HVAC_cost + \
                    self.nacelleCover_cost + \
                    self.controls_cost

        self.d_nacelle_cost_d_r_diameter = self.d_lss_cost_d_r_diameter + self.d_bearings_cost_d_r_diameter + self.d_yaw_cost_d_r_diameter + self.d_mainframe_cost_d_r_diameter
        self.d_nacelle_cost_d_r_mass = self.d_mainframe_cost_d_r_mass
        self.d_nacelle_cost_d_r_thrust = self.d_mainframe_cost_d_r_thrust
        self.d_nacelle_cost_d_r_torque = self.d_mainframe_cost_d_r_torque
        self.d_nacelle_cost_d_rating = self.d_gearbox_cost_d_rating + self.d_generator_cost_d_rating + self.d_brakes_cost_d_rating + self.d_hvac_cost_d_rating + \
                                       self.d_cover_cost_d_rating + self.d_electronics_cost_d_rating + self.d_vselectronics_cost_d_rating

    def linearize(self):
       
        self.J = np.array([[self.d_nacelle_mass_d_r_diameter, self.d_nacelle_mass_d_r_mass, self.d_nacelle_mass_d_r_thrust, self.d_nacelle_mass_d_r_torque, self.d_nacelle_mass_d_rating],\
                           [self.d_lss_mass_d_r_diameter, self.d_lss_mass_d_r_mass, 0.0, self.d_lss_mass_d_r_torque, 0.0],\
                           [self.d_bearings_mass_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, self.d_gearbox_mass_d_r_torque, 0.0],\
                           [0.0, 0.0, 0.0, self.d_generator_mass_d_r_torque, self.d_generator_mass_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_brakes_mass_d_rating],\
                           [self.d_yaw_mass_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_hvac_mass_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, 0.0],\
                           [self.d_mainframe_mass_d_r_diameter, self.d_mainframe_mass_d_r_mass, self.d_mainframe_mass_d_r_thrust, self.d_mainframe_mass_d_r_torque, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_cover_mass_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, 0.0],\
                           [self.d_nacelle_cost_d_r_diameter, self.d_nacelle_cost_d_r_mass, self.d_nacelle_cost_d_r_thrust, self.d_nacelle_cost_d_r_torque, self.d_nacelle_cost_d_rating],\
                           [self.d_lss_cost_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [self.d_bearings_cost_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_gearbox_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_generator_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_brakes_cost_d_rating],\
                           [self.d_yaw_cost_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_electronics_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_hvac_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_vselectronics_cost_d_rating],\
                           [self.d_mainframe_cost_d_r_diameter, self.d_mainframe_cost_d_r_mass, self.d_mainframe_cost_d_r_thrust, self.d_mainframe_cost_d_r_torque, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_cover_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, 0.0]])
    
    def provideJ(self):
      
        inputs = ['rotor_diameter', 'rotor_mass', 'rotor_thrust', 'rotor_torque', 'machine_rating']
        outputs = ['nacelle_mass', 'lowSpeedShaft_mass', 'bearings_mass', 'gearbox_mass', 'generator_mass', 'mechanicalBrakes_mass', 'yawSystem_mass', \
                   'electronicCabling_mass', 'HVAC_mass', 'VSElectronics_mass', 'mainframeTotal_mass', 'nacelleCover_mass', 'controls_mass',\
                   'nacelle_cost', 'lowSpeedShaft_cost', 'bearings_cost', 'gearbox_cost', 'generator_cost', 'mechanicalBrakes_cost', 'yawSystem_cost', \
                   'electronicCabling_cost', 'HVAC_cost', 'VSElectronics_cost', 'mainframeTotal_cost', 'nacelleCover_cost', 'controls_cost']
    
        return inputs, outputs, self.J
       
#-----------------------------------------------------------------

def example():

    # simple test of module

    nac = nacelle_csm_component()
        
    # First test
    nac.rotor_diameter = 126.0
    nac.machine_rating = 5000.0
    nac.rotor_mass = 123193.30
    #nac.max_rotor_speed = 12.12609
    nac.rotor_thrust = 500930.1
    nac.rotor_torque = 4365249
    nac.drivetrain_design = 1
    nac.offshore = True
    nac.crane=True
    nac.advanced_bedplate=0
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    
    print "Nacelle csm component"
    print "Nacelle mass: {0}".format(nac.nacelle_mass)
    print   
    print "lss mass: {0}".format(nac.lowSpeedShaft_mass)
    print "bearings mass: {0}".format(nac.bearings_mass)
    print "gearbox mass: {0}".format(nac.gearbox_mass)
    print "mechanical brake mass: {0}".format(nac.mechanicalBrakes_mass)
    print "generator mass: {0}".format(nac.generator_mass)
    print "yaw system mass: {0}".format(nac.yawSystem_mass)
    print "mainframe total mass: {0}".format(nac.mainframeTotal_mass)
    print "econnections total mass: {0}".format(nac.electronicCabling_mass)
    print "hvac mass: {0}".format(nac.HVAC_mass)
    print "nacelle cover mass: {0}".format(nac.nacelleCover_mass)
    print "controls mass: {0}".format(nac.controls_mass)
    print
    print "Nacelle cost: {0}".format(nac.nacelle_cost)
    print   
    print "lss _cost: {0}".format(nac.lowSpeedShaft_cost)
    print "bearings _cost: {0}".format(nac.bearings_cost)
    print "gearbox _cost: {0}".format(nac.gearbox_cost)
    print "mechanical brake _cost: {0}".format(nac.mechanicalBrakes_cost)
    print "generator _cost: {0}".format(nac.generator_cost)
    print "yaw system _cost: {0}".format(nac.yawSystem_cost)
    print "mainframe total _cost: {0}".format(nac.mainframeTotal_cost)
    print "econnections total cost: {0}".format(nac.electronicCabling_cost)
    print "hvac cost: {0}".format(nac.HVAC_cost)
    print "nacelle cover cost: {0}".format(nac.nacelleCover_cost)
    print "controls cost: {0}".format(nac.controls_cost)

if __name__ == "__main__":

    example()