# 1 ---------

# A simple test of turbine_costsse model
from turbine_costsse.turbine_costsse import Turbine_CostsSE

turbine = Turbine_CostsSE()

# 1 ---------
# 2 ---------

# NREL 5 MW turbine component masses based on Sunderland model approach

# Rotor
turbine.blade_mass = 17650.67  # inline with the windpact estimates
turbine.hub_mass = 31644.5
turbine.pitch_system_mass = 17004.0
turbine.spinner_mass = 1810.5

# Drivetrain and Nacelle
turbine.low_speed_shaft_mass = 31257.3
#bearingsMass = 9731.41
turbine.main_bearing_mass = 9731.41 / 2
turbine.second_bearing_mass = 9731.41 / 2
turbine.gearbox_mass = 30237.60
turbine.high_speed_side_mass = 1492.45
turbine.generator_mass = 16699.85
turbine.bedplate_mass = 93090.6
turbine.yaw_system_mass = 11878.24

# Tower
turbine.tower_mass = 434559.0

# 2 ---------
# 3 ---------

# Additional non-mass cost model input variables
turbine.machine_rating = 5000.0
turbine.advanced = True
turbine.blade_number = 3
turbine.drivetrain_design = 1
turbine.crane = True
turbine.offshore = True

# Target year for analysis results
turbine.year = 2010
turbine.month =  12

# 3 ---------
# 4 --------- 

turbine.run()

# 4 ----------
# 5 ----------

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

# 5 ---------- 
# 6 ----------

# A simple test of nrel_csm_tcc model
from nrel_csm_tcc.nrel_csm_tcc import tcc_csm_assembly
import numpy as np

trb = tcc_csm_assembly()

# 6 ----------
# 7 ----------

# NREL 5 MW main parameters
trb.rotor_diameter = 126.0
trb.advanced_blade = True
trb.blade_number = 3
trb.hub_height = 90.0    
trb.machine_rating = 5000.0
trb.offshore = True
trb.drivetrain_design = 1

# 7 ----------
# 8 ----------

# Rotor force calculations for nacelle inputs
maxTipSpd = 80.0
maxEfficiency = 0.90201
ratedWindSpd = 11.5064
thrustCoeff = 0.50
airDensity = 1.225

ratedHubPower  = trb.machine_rating / maxEfficiency 
rotorSpeed     = (maxTipSpd/(0.5*trb.rotor_diameter)) * (60.0 / (2*np.pi))
trb.rotor_thrust  = airDensity * thrustCoeff * np.pi * trb.rotor_diameter**2 * (ratedWindSpd**2) / 8
trb.rotor_torque = ratedHubPower/(rotorSpeed*(np.pi/30))*1000

# 8 -----------

# Target year for analysis results
trb.year = 2009
trb.month = 12

# 8 -----------
# 9 -----------

trb.run()

# 9 -----------
# 10 ----------

print "Offshore turbine in 20 m of water"
print "Turbine mass: {0}".format(trb.turbine_mass)
print "Turbine cost: {0}".format(trb.turbine_cost)

# 10 ----------