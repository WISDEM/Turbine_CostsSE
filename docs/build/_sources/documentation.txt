Module Documentation
--------------------

.. only:: latex

    An HTML version of this documentation is available which is better formatted for reading the code documentation and contains hyperlinks to the source code.

This documentation covers turbine component mass-cost models for the full set of turbine components from the rotor to tower.


Component Cost Interface
^^^^^^^^^^^^^^^^^^^^^^^^

The component cost objects in the mass-to-cost model set need only implement the __init__ method and set the cost attribute of the parent interface ComponentCost.  The interface contains no methods that must be implemented.


Rotor Mass-Cost Models
^^^^^^^^^^^^^^^^^^^^^^

Rotor mass-cost models include individual models for the blade, hub, pitch system and spinner components as well as combined model for the full hub system and the overall rotor.

.. _BladeCost-class-label:

BladeCost
"""""""""

.. currentmodule:: turbine_costSE.src.rotor_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: BladeCost
        :members:


.. only:: html

    .. autoclass:: BladeCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~BladeCost.__init__

.. autogenerate
    .. autosummary::
        :toctree: generated

        ~BladeCost.__init__

.. _HubCost-class-label:

HubCost
"""""""""

.. currentmodule:: turbine_costSE.src.rotor_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: HubCost
        :members:


.. only:: html

    .. autoclass:: HubCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~HubCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~HubCost.__init__

.. _PitchCost-class-label:

PitchCost
"""""""""

.. currentmodule:: turbine_costSE.src.rotor_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: PitchCost
        :members:


.. only:: html

    .. autoclass:: PitchCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~PitchCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~PitchCost.__init__

.. _SpinnerCost-class-label:

SpinnerCost
"""""""""

.. currentmodule:: turbine_costSE.src.rotor_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: SpinnerCost
        :members:


.. only:: html

    .. autoclass:: SpinnerCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~SpinnerCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~SpinnerCost.__init__

.. _HubSystemCost-class-label:

HubSystemCost
"""""""""

.. currentmodule:: turbine_costSE.src.rotor_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: HubSystemCost
        :members:


.. only:: html

    .. autoclass:: HubSystemCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~HubSystemCost.__init__

.. autogenerate
    .. autosummary::
        :toctree: generated

        ~HubSystemCost.__init__


.. _RotorCost-class-label:

RotorCost
"""""""""

.. currentmodule:: turbine_costSE.src.rotor_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: RotorCost
        :members:


.. only:: html

    .. autoclass:: RotorCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~RotorCost.__init__

.. autogenerate
    .. autosummary::
        :toctree: generated

        ~RotorCost.__init__

Nacelle Mass-Cost Models
^^^^^^^^^^^^^^^^^^^^^^

Nacelle mass-cost models include individual models for the low speed shaft, main bearing set, gearbox, high speed shaft and brake, generator, bedplate and yaw system as well as an overall nacelle cost model which includes power electronics, overall mainframe, controls, cables, HVAC and nacelle cover.

.. _LowSpeedShaftCost-class-label:

LowSpeedShaftCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: LowSpeedShaftCost
        :members:


.. only:: html

    .. autoclass:: LowSpeedShaftCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~LowSpeedShaftCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~LowSpeedShaftCost.__init__

.. _MainBearingsCost-class-label:

MainBearingsCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: MainBearingsCost
        :members:


.. only:: html

    .. autoclass:: MainBearingsCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~MainBearingsCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~MainBearingsCost.__init__

.. _Gearbox-class-label:

GearboxCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: GearboxCost
        :members:


.. only:: html

    .. autoclass:: GearboxCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~GearboxCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~GearboxCost.__init__

.. _HighSpeedShaftCost-class-label:

HighSpeedShaftCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: HighSpeedShaftCost
        :members:


.. only:: html

    .. autoclass:: HighSpeedShaftCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~HighSpeedShaftCost.__init__

.. autogenerate
    .. autosummary::
        :toctree: generated

        ~HighSpeedShaftCost.__init__

.. _GeneratorCost-class-label:

GeneratorCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: GeneratorCost
        :members:


.. only:: html

    .. autoclass:: GeneratorCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~GeneratorCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~GeneratorCost.__init__

.. _BedplateCost-class-label:

BedplateCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: BedplateCost
        :members:


.. only:: html

    .. autoclass:: BedplateCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~BedplateCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~BedplateCost.__init__


.. _YawSystemCost-class-label:

YawSystemCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: YawSystemCost
        :members:


.. only:: html

    .. autoclass:: YawSystemCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~YawSystemCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~YawSystemCost.__init__

.. _NacelleSystemCost-class-label:

NacelleSystemCost
"""""""""

.. currentmodule:: turbine_costSE.src.nacelle_costsSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: NacelleSystemCost
        :members:


.. only:: html

    .. autoclass:: NacelleSystemCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~NacelleSystemCost.__init__
	

.. autogenerate
    .. autosummary::
        :toctree: generated

        ~NacelleSystemCost.__init__



Tower Mass-Cost Model
^^^^^^^^^^^^^^^^^^^^^^

Tower mass-cost models include the mass to cost model of the tower component.

.. _TowerCost-class-label:

TowerCost
"""""""""

.. currentmodule:: turbine_costSE.src.tower_costSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: TowerCost
        :members:


.. only:: html

    .. autoclass:: TowerCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~TowerCost.__init__


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~TowerCost.__init__

Overall Turbine Mass-Cost Model
^^^^^^^^^^^^^^^^^^^^^^

Turbine mass-cost models take mass for all major components of the turbine and compute overall turbine cost.

.. _TurbineCost-class-label:

TurbineCost
"""""""""

.. currentmodule:: turbine_costSE.src.turbine_costSE

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: TurbineCost
        :members:


.. only:: html

    .. autoclass:: TurbineCost

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~TurbineCost.__init__

.. autogenerate
    .. autosummary::
        :toctree: generated

        ~TurbineCost.__init__


PPI Index Calculations
^^^^^^^^^^^^^^^^^^^^^^

All of the above mass-cost models use a Price Producer Indices (PPIs) to scale the costs from a reference year and month (typically September 2002).  The PPI class is imported by all the above models through the config file.

.. _PPI-class-label:

PPI
"""""""""

.. currentmodule:: turbine_costSE.src.csmPPI

.. rubric:: Class Summary:

.. only:: latex

    .. autoclass:: PPI
        :members:


.. only:: html

    .. autoclass:: PPI

        .. rubric:: Methods
        .. autosummary::
            :nosignatures:

            ~PPI.__init__
            ~PPI.compute


.. autogenerate
    .. autosummary::
        :toctree: generated

        ~PPI.__init__
        ~PPI.compute

