.. _documentation-label:

.. currentmodule:: turbine_costsse.turbine_costsse

Documentation
-------------

Documentation for Turbine_CostsSE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for Turbine_CostsSE:

.. literalinclude:: ../src/turbine_costsse/turbine_costsse.py
    :language: python
    :start-after: Turbine_CostsSE(Assembly)
    :end-before: def configure(self)
    :prepend: class Turbine_CostsSE(Assembly):


Referenced Sub-System Modules (Rotor)
=====================================
.. module:: turbine_costsse.turbine_costsse
.. class:: BladeCost
.. class:: HubCost
.. class:: PitchSystemCost
.. class:: SpinnerCost
.. class:: HubSystemCostAdder
.. class:: RotorCostAdder
.. class:: Rotor_CostsSE

Referenced Sub-System Modules (Nacelle)
=======================================
.. module:: turbine_costsse.turbine_costsse
.. class:: LowSpeedShaftCost
.. class:: BearingsCost
.. class:: GearboxCost
.. class:: HighSpeedSideCost
.. class:: GeneratorCost
.. class:: BedplateCost
.. class:: NacelleSystemCostAdder
.. class:: Nacelle_CostsSE

Referenced Sub-System Modules (Tower)
=====================================
.. module:: turbine_costsse.turbine_costsse
.. class:: TowerCost
.. class:: TowerCostAdder
.. class:: Tower_CostsSE

Referenced Turbine Cost Modules
===============================
.. module:: turbine_costsse.turbine_costsse
.. class:: Turbine_CostsSE
.. class:: TurbineCostAdder

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI


.. currentmodule:: turbine_costsse.turbine_costsse


Documentation for NREL_CSM_TCC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_TCC:

.. literalinclude:: ../src/turbine_costsse/nrel_csm_tcc.py
    :language: python
    :start-after: tcc_csm_assembly(Assembly)
    :end-before: def configure(self)
    :prepend: class tcc_csm_assembly(Assembly):

Referenced Sub-System Modules (Blades)
======================================
.. module:: turbine_costsse.nrel_csm_tcc
.. class:: blades_csm_component

Referenced Sub-System Modules (Hub)
===================================
.. module:: turbine_costsse.nrel_csm_tcc
.. class:: hub_csm_component


Referenced Sub-System Modules (Nacelle)
=======================================
.. module:: turbine_costsse.nrel_csm_tcc
.. class:: nacelle_csm_component

Referenced Sub-System Modules (Tower)
=====================================
.. module:: turbine_costsse.nrel_csm_tcc
.. class:: tower_csm_component

Referenced Turbine Cost Modules
===============================
.. module:: turbine_costsse.nrel_csm_tcc
.. class:: tcc_csm_assembly
.. class:: tcc_csm_component
.. class:: rotor_mass_adder

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI


