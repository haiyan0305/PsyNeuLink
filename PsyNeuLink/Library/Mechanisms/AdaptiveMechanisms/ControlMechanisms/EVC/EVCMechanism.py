# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# *************************************************  EVCMechanism ******************************************************

"""

Overview
--------

An EVCMechanism is a `ControlMechanism <ControlMechanism>` that regulates it `ControlSignals <ControlSignal>` in order
to optimize the performance of the System to which it belongs.  EVCMechanism is one of the most powerful, but also one
of the most complex components in PsyNeuLink.  It is designed to implement a form of the Expected Value of Control (EVC)
Theory described in `Shenhav et al. (2013) <https://www.ncbi.nlm.nih.gov/pubmed/23889930>`_, which provides useful
background concerning the purpose and structure of the EVCMechanism.

An EVCMechanism is similar to a standard `ControlMechanism`, with the following exceptions:

  * it can only be assigned to a System as its `controller <System_Base.controller>`, and not in any other capacity
    (see `ControlMechanism_System_Controller`);
  ..
  * it has several specialized functions that are used to search over the `values <ControlSignal.value>`\\s of its
    its `ControlSignals <ControlSignal>`, and evaluate the performance of its `system <EVCMechanism.system>`;  by
    default, it simulates its `system <EVCMechanism.system>` and evaluates its performance under all combinations of
    ControlSignal values to find the one that optimizes the `Expected Value of Control <EVCMechanism_EVC>`, however
    its functions can be customized or replaced to implement other optimization procedures.
  ..
  * it creates a specialized set of `prediction Mechanisms` EVCMechanism_Prediction_Mechanisms` that are used to
    simulate the performnace of its `system <EVCMechanism.system>`.

.. _EVCMechanism_EVC:

Expected Value of Control (EVC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The EVCMechanism uses it `function <EVCMechanism.function>` to select an `allocation_policy` for its `system
<EVCMechanism.system>`.  In the `default configuration <EVC_Default_Configuration>`, an EVCMechanism carries out an
exhaustive evaluation of allocation policies, simulating its `system <EVCMechanism.system>` under each, and using an
`ObjectiveMechanism` and several `auxiliary functions <EVCMechanism_Functions>` to calculate the **expected
value of control (EVC)** for each `allocation_policy`: a cost-benefit analysis that weighs the `cost
<ControlSignal.cost> of the ControlSignals against the outcome of the `system <EVCMechanism.system>` \\s performance for
a given `allocation_policy`. The EVCMechanism selects the `allocation_policy` that generates the maximum EVC, and
implements that for the next `TRIAL`. Each step of this procedure can be modified, or replaced entirely, by assigning
custom functions to corresponding parameters of the EVCMechanism, as described `below <EVCMechanism_Functions>`.

.. _EVCMechanism_Creation:

Creating an EVCMechanism
------------------------

An EVCMechanism can be created in any of the ways used to `create Mechanisms <Mechanism_Creation>`;  it is also
created automatically when a `System` is created and the EVCMechanism class is specified in the **controller**
argument of the System's constructor (see `System_Creation`).  The ObjectiveMechanism, the OutputStates it
monitors and evaluates, and the parameters controlled by an EVCMechanism can be specified in the standard way for a
ControlMechanism (see `ControlMechanism_ObjectiveMechanism` and `ControlMechanism_Control_Signals`, respectively).

.. note::
   Although an EVCMechanism can be created on its own, it can only be assigned to, and executed within a `System` as
   the System's `controller <System_Base.controller>`.

When an EVCMechanism is assigned to, or created by a System, it is assigned the OutputStates to be monitored and
parameters to be controlled specified for that System (see `System_Control`), and a `prediction Mechanism
<EVCMechanism_Prediction_Mechanisms>` is created for each `ORIGIN` Mechanism in the `system <EVCMechanism.system>`.
The prediction Mechanisms are assigned to the EVCMechanism's `prediction_mechanisms` attribute. The OutputStates used
to determine an EVCMechanism’s allocation_policy and the parameters it controls can be listed using its show method.
The EVCMechanism and the Components associated with it in its `system <EVCMechanism.system>` can be displayed using
the System's `System_Base.show_graph` method with its **show_control** argument assigned as `True`

An EVCMechanism that has been constructed automatically can be customized by assigning values to its attributes (e.g.,
those described above, or its `function <EVCMechanism.function>` as described under `EVC_Default_Configuration `below).


.. _EVCMechanism_Structure:

Structure
---------

Like any ControlMechanism, an EVCMechanism belongs to a `System` (identified in its `system <EVCMechanism.system>`
attribute) and, in addition to the standard Components of a `ControlMechanism`, has a specialized set of
`prediction mechanisms <EVCMechanism_Prediction_Mechanisms>` and `functions <EVCMechanism_Functions>`
that it uses to simulate and evaluate the performance of its `system <EVCMechanism.system>` under the influence of
different values of its `ControlSignals <EVCMechanism_ControlSignals>`.  Each of these specialized Components is
described below.

.. _EVCMechanism_Input:

Input
~~~~~

.. _EVCMechanism_ObjectiveMechanism:

ObjectiveMechanism
^^^^^^^^^^^^^^^^^^

Like any ControlMechanism, an EVCMechanism receives its input from the *OUTCOME* `OutputState
<ObjectiveMechanism_Output>` of an `ObjectiveMechanism`, via a MappingProjection to its `primary InputState
<InputStatePrimary>`.  The ObjectiveFunction is listed in the EVCMechanism's `objective_mechanism
<EVCMechanism.objective_mechanism>` attribute.  By default, the ObjectiveMechanism's function is a `LinearCombination`
function with its `operation <LinearCombination.operation>` attribute assigned as *PRODUCT*, which takes the product of
the `value <OutputState.value>`\\s of the OutputStates that it monitors (listed in its `monitored_values
<ObjectiveMechanism.monitored_values>` attribute.  However, this can be customized in a variety of ways:

    * by specifying a different `function <ObjectiveMechanism.function>` for the ObjectiveMechanism
      (see `ObjectiveMechanism_Weights_and_Exponents_Example` for an example);
    ..
    * using a list to specify the OutputStates to be monitored  (and the `tuples format
      <ObjectiveMechanism_OutputState_Tuple>` to specify weights and/or exponents for them) in the
      **objective_mechanism** argument of the EVCMechanism's constructor;
    ..
    * using the  **monitored_values** argument of the `objective_mechanism <EVCMechanism.objective_mechanism>`'s
      constructor;
    ..
    * specifying a different `ObjectiveMechanism` in the EVCMechanism's **objective_mechanism** argument of the
      EVCMechanism's constructor. The result of the `objective_mechanism <EVCMechanism.objective_mechanism>`'s
      `function <ObjectiveMechanism.function>` is used as the outcome in the calculations described below.  Note,
      however

    .. _EVCMechanism_Objective_Mechanism_Function_Note:

    .. note::
       If a constructor for an `ObjectiveMechanism` is used for the **objective_mechanism** argument of the
       EVCMechanism's constructor, then the default values of its attributes override any used by the EVCMechanism
       for its `objective_mechanism <EVCMechanism.objective_mechanism>`.  In particular, whereas an EVCMechanism uses
       the same default `function <ObjectiveMechanism.function>` as an `ObjectiveMechanism` (`LinearCombination`),
       it uses *PRODUCT* rather than *SUM* as the default value of the `operation <LinearCombination.operation>`
       attribute of the function.  As a consequence, if the constructor for an ObjectiveMechanism is used to specify
       the EVCMechanism's **objective_mechanism** argument, and the **operation** argument is not specified,
       *SUM* rather than *PRODUCT* will be used for the ObjectiveMechanism's `function
       <ObjectiveMechanism.function>`.  To restore *PRODUCT*, it must now be specified explicitly in the
       **operation** argument of the constructor for the ObjectiveMechanism (see 1st example under
       `System_Control_Examples`).

The result of the EVCMechanism's `objective_mechanism <EVCMechanism.objective_mechanism>` is used by its `function
<EVCMechanism>` to evaluate the performance of its `system <EVCMechanism.system>` when computing the `EVC
<EVCMechanism_EVC>`.


.. _EVCMechanism_Prediction_Mechanisms:

Prediction Mechanisms
^^^^^^^^^^^^^^^^^^^^^

These are used to provide input to the `system <EVCMechanism.system>` when the EVCMechanism's default `function
<EVCMechanism.function>` (`ControlSignalGridSearch`) `simulates its execution <EVC_Default_Configuration>` to evaluate
the EVC for each `allocation_policy`.  When an EVCMechanism is created, a prediction Mechanism is created for each
`ORIGIN` Mechanism in its `system <EVCMechanism.system>`, and for each `Projection <Projection>` received by an `ORIGIN`
Mechanism, a `MappingProjection` from the same source is created that projects to the corresponding prediction
Mechanism. The type of `Mechanism <Mechanism>` used for the prediction Mechanisms is specified by the EVCMechanism's
`prediction_mechanism_type` attribute, and their parameters can be specified with the `prediction_mechanism_params`
attribute. The default type is an 'IntegratorMechanism`, that calculates an exponentially weighted time-average of
its input. The prediction mechanisms for an EVCMechanism are listed in its `prediction_mechanisms` attribute.


.. _EVCMechanism_Functions:

Function
~~~~~~~~

By default, the primary `function <EVCMechanism.function>` is `ControlSignalGridSearch` (see
`EVC_Default_Configuration`), that systematically evaluates the effects of its ControlSignals on the performance of
its `system <EVCMechanism.system>` to identify an `allocation_policy <EVCMechanism.allocation_policy>` that yields the
highest `EVC <EVCMechanism_EVC>`.  However, any function can be used that returns an appropriate value (i.e., that
specifies an `allocation_policy` for the number of `ControlSignals <EVCMechanism_ControlSignals>` in the EVCMechanism's
`control_signals` attribute, using the correct format for the `allocation <ControlSignal.allocation>` value of each
ControlSignal).  In addition to its primary `function <EVCMechanism.function>`, an EVCMechanism has several auxiliary
functions, that can be used by its `function <EVCMechanism.function>` to calculate the EVC to select an
`allocation_policy` with the maximum EVC among a range of policies specified by its ControlSignals.  The default
set of functions and their operation are described in the section that follows;  however, the EVCMechanism's
`function <EVCMechanism.function>` can call any other function to customize how the EVC is calcualted.

.. _EVCMechanism_Default_Configuration:

Default Configuration of EVC Function and its Auxiliary Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In its default configuration, an EVCMechanism simulates and evaluates the performance of its `system
<EVCMechanism.system>` under a set of allocation_policies determined by the `allocation_samples
<ControlSignal.allocation_samples>` attributes of its `ControlSignals <EVCMechanism_ControlSignals>`, and implements
(for the next `TRIAL` of execution) the one that generates the maximum `EVC <EVCMechanism_EVC>`.  This is carried out
by the EVCMechanism's default `function <EVCMechanism.function>` and three auxiliary functions, as described below.

The default `function <EVCMechanism.function>` of an EVCMechanism is `ControlSignalGridSearch`. It identifies the
`allocation_policy` with the maximum `EVC <EVCMechanism_EVC>` by a conducting an exhaustive search over every possible
`allocation_policy`— that is, all combinations of `allocation <ControlSignal.allocation>` values for its `ControlSignal
<EVCMechanism_ControlSignals>`, where the `allocation <ControlSignal.allocation>` values sampled for each ControlSignal
are determined by its `allocation_samples` attribute.  For each `allocation_policy`, the EVCMechanism executes the
`system <EVCMechanism.system>`, evaluates the `EVC <EVCMechanism_EVC>` for that policy, and returns the
`allocation_policy` that yields the greatest EVC value. The following steps are used to calculate the EVC in each
`allocation_policy`:

  * **Implement the policy and simulate the System** - assign the `allocation <ControlSignal.allocation>` that the
    selected `allocation_policy` specifies for each ControlSignal, and then simulate the `system <EVCMechanism.system>`
    using the corresponding parameter values.
  |
  * **Evaluate the System's performance** - this is carried out by the EVCMechanism's `objective_mechanism
    <EVCMechanism.objective_mechanism>`, which is executed as part of the simulation of the System.  The `function
    <ObjectiveMechanism.function>` for a default ObjectiveMechanism is a `LinearCombination` Function that combines the
    `value <OutputState.value>`\\s of the OutputStates listed in the EVCMechanism's `monitored_output_states
    <EVCMechanism.monitored_output_states>` attribute (and the `objective_mechanism
    <EVCMechanism.objective_mechanism>`'s `monitored_values <ObjectiveMechanism.monitored_values>` attribute)
    by taking their elementwise (Hadamard) product.  However, this behavior can be customized in a variety of ways,
    as described `above EVCMechanism_ObjectiveMechanism`.

  * **Calculate EVC** - call the EVCMechanism's `value_function <EVCMechanism.value_function>` passing it the
    outcome (received from the `objective_mechanism`) and a list of the `costs <ControlSignal.cost>` \\s of its
    `ControlSignals <EVCMechanism_ControlSignals>`; the default `value_function <EVCMechanism.value_function>` calls
    two additional auxiliary functions, in the following order:

    - `cost_function <EVCMechanism.cost_function>`, which sums the costs;  this can be configured to weight and/or
      exponentiate individual costs (see `cost_function <EVCMechanism.cost_function>` attribute);

    - `combine_outcome_and_cost_function <EVCMechanism.combine_outcome_and_cost_function>`, which subtracts the sum of
      the costs from the outcome to generate the EVC;  this too can be configured (see
      `combine_outcome_and_cost_function <EVCMechanism.combine_outcome_and_cost_function>`).

In addition to modifying the default functions (as noted above), any or all of them can be replaced with a custom
function to modify how the `allocation_policy <EVCMechanism.allocation_policy>` is determined, so long as the custom
function accepts arguments and return values that are compatible with any that call that function (see note below).

.. _EVCMechanism_Calling_and_Assigning_Functions:

    .. note::
       The `EVCMechanism auxiliary functions <EVCMechanism_Functions>` described above are all implemented
       as PsyNeuLink `Functions <Function>`.  Therefore, to call a function itself, it must be referenced as
       ``<EVCMechanism>.<function_attribute>.function``.  A custom function assigned to one of the auxiliary functions
       can be either a PsyNeuLink `Function <Function>`, or a generic python function or method (including a lambda
       function).  If it is one of the latter, it is automatically "wrapped" as a PsyNeuLink `Function <Function>`
       (specifically, it is assigned as the `function <UserDefinedFunction.function>` attribute of a
       `UserDefinedFunction` object), so that it can be referenced and called in the same manner as
       the default function assignment. Therefore, once assigned, it too must be referenced as
       ``<EVCMechanism>.<function_attribute>.function``.

.. _EVCMechanism_ControlSignals:

ControlSignals
~~~~~~~~~~~~~~

The OutputStates of an EVCMechanism (like any `ControlMechanism`) are a set of `ControlSignals
<ControlSignal>`, that are listed in its `control_signals <EVCMechanism.control_signals>` attribute (as well as its
`output_states <ControlMechanism.output_states>` attribute).  Each ControlSignal is assigned a  `ControlProjection`
that projects to the `ParameterState` for a parameter controlled by the EVCMechanism.  Each ControlSignal is
assigned an item of the EVCMechanism's `allocation_policy`, that determines its `allocation <ControlSignal.allocation>`
for a given `TRIAL` of execution.  The `allocation <ControlSignal.allocation>` is used by a ControlSignal to determine
its `intensity <ControlSignal.intensity>`, which is then assigned as the `value <ControlProjection.value>` of the
ControlSignal's ControlProjection.   The `value <ControlProjection>` of the ControlProjection is used by the
`ParameterState` to which it projects to modify the value of the parameter (see `ControlSignal_Modulation` for
description of how a ControlSignal modulates the value of a parameter it controls).  A ControlSignal also calculates a
`cost <ControlSignal.cost>`, based on its `intensity <ControlSignal.intensity>` and/or its time course. The
`cost <ControlSignal.cost>` is included in the evaluation that the EVCMechanism carries out for a given
`allocation_policy`, and that it uses to adapt the ControlSignal's `allocation  <ControlSignal.allocation>` in the
future.  When the EVCMechanism chooses an `allocation_policy` to evaluate,  it selects an allocation value from the
ControlSignal's `allocation_samples <ControlSignal.allocation_samples>` attribute.


.. _EVCMechanism_Execution:

Execution
---------

An EVCMechanism must be the `controller <System_Base.controller>` of a System, and as a consequence it is always the
last `Mechanism <Mechanism>` to be executed in a `TRIAL` for its `system <EVCMechanism.system>` (see `System Control
<System_Execution_Control>` and `Execution <System_Execution>`). When an EVCMechanism is executed, it updates the
value of its `prediction_mechanisms` and `objective_mechanism`, and then calls its `function <EVCMechanism.function>`,
which determines and implements the `allocation_policy` for the next `TRIAL` of its `system <EVCMechanism.system>`
\\s execution.  The default `function <EVCMechanism.function>` executes the following steps (described in greater
detailed `above <EVC_Default_Configuration>`):

* samples every allocation_policy (i.e., every combination of the `allocation` \\s specified for the EVCMechanism's
  ControlSignals specified by their `allocation_samples` attributes);  for each `allocation_policy`, it:

  * Executes the EVCMechanism's `system <EVCMechanism.system>` with the parameter values specified by that
    `allocation_policy`;  this includes the EVCMechanism's `objective_mechanism`, which provides the result
    to the EVCMechanism.

  * Calls the EVCMechanism's `value_function <EVCMechanism.value_function>`, which in turn calls EVCMechanism's
    `cost_function <EVCMechanism.cost_function>` and `combine_outcome_and_cost_function
    <EVCMechanism.combine_outcome_and_cost_function>` to evaluate the EVC for that `allocation_policy`.

  * Selects and returns the `allocation_policy` that generates the maximum EVC value.

This procedure can be modified by specifying a custom function for any or all of the `functions
<EVCMechanism_Functions>` referred to above.


.. _EVCMechanism_Examples:

Example
-------

The following example implements a System with an EVCMechanism (and two processes not shown)::

    mySystem = system(processes=[myRewardProcess, myDecisionProcess],
                      controller=EVCMechanism,
                      monitor_for_control=[Reward, DDM_DECISION_VARIABLE,(RESPONSE_TIME, 1, -1)],

It uses the System's `monitor_for_control` argument to assign three outputStates to be monitored.  The first one
references the Reward Mechanism (not shown);  its `primary OutputState <OutputState_Primary>` will be used by default.
The second and third use keywords that are the names of outputStates of a  `DDM` Mechanism (also not shown).
The last one (RESPONSE_TIME) is assigned a weight of 1 and an exponent of -1. As a result, each calculation of the EVC
computation will multiply the value of the primary OutputState of the Reward Mechanism by the value of the
*DDM_DECISION_VARIABLE* OutputState of the DDM Mechanism, and then divide that by the value of the *RESPONSE_TIME*
OutputState of the DDM Mechanism.

See `ObjectiveMechanism <ObjectiveMechanism_Monitored_Values_Examples>` for additional examples of how to specify it's
**monitored_values** argument, `ControlMechanism <ControlMechanism_Examples>` for additional examples of how to
specify ControlMechanisms, and `System <System_Examples>` for how to specify the `controller <System_Base.controller>`
of a System.

.. _EVCMechanism_Class_Reference:

Class Reference
---------------

"""
import numbers

import numpy as np
import typecheck as tc

from PsyNeuLink.Components.Component import function_type
from PsyNeuLink.Components.Functions.Function import ModulationParam, _is_modulation_param, LinearCombination
from PsyNeuLink.Components.System import System
from PsyNeuLink.Components.Mechanisms.AdaptiveMechanisms.ControlMechanism.ControlMechanism \
    import ControlMechanism_Base
from PsyNeuLink.Components.Mechanisms.Mechanism import MechanismList
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms import IntegratorMechanism
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.ObjectiveMechanism import ObjectiveMechanism
from PsyNeuLink.Components.Projections.PathwayProjections.MappingProjection import MappingProjection
from PsyNeuLink.Components.ShellClasses import Function
from PsyNeuLink.Globals.Defaults import defaultControlAllocation
from PsyNeuLink.Globals.Keywords import FUNCTION, INITIALIZING, INIT_FUNCTION_METHOD_ONLY, \
                                        PARAMETER_STATES, SUM, EVC_MECHANISM, CONTROL, COST_FUNCTION, \
                                        PREDICTION_MECHANISM, PREDICTION_MECHANISM_PARAMS, PREDICTION_MECHANISM_TYPE
from PsyNeuLink.Globals.Preferences.ComponentPreferenceSet import is_pref_set
from PsyNeuLink.Globals.Preferences.PreferenceSet import PreferenceLevel
from PsyNeuLink.Globals.Utilities import ContentAddressableList
from PsyNeuLink.Library.Mechanisms.AdaptiveMechanisms.ControlMechanisms.EVC.EVCAuxiliary import \
    ControlSignalGridSearch, \
    ValueFunction
from PsyNeuLink.Scheduling.TimeScale import CentralClock, Clock, TimeScale

class EVCError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


class EVCMechanism(ControlMechanism_Base):
    """EVCMechanism(                                                   \
    system=True,                                                       \
    objective_mechanism=None,                                          \
    prediction_mechanism_type=IntegratorMechanism,                     \
    prediction_mechanism_params=None,                                  \
    function=ControlSignalGridSearch                                   \
    value_function=ValueFunction,                                      \
    cost_function=LinearCombination(operation=SUM),                    \
    combine_outcome_and_cost_function=LinearCombination(operation=SUM) \
    save_all_values_and_policies:bool=:keyword:`False`,                \
    control_signals=None,                                              \
    params=None,                                                       \
    name=None,                                                         \
    prefs=None)

    Subclass of `ControlMechanism <ControlMechanism>` that optimizes the `ControlSignals <ControlSignal>` for a
    `System`.

    COMMENT:
        Class attributes:
            + componentType (str): System Default Mechanism
            + paramClassDefaults (dict):
                + SYSTEM (System)
                + MONITORED_OUTPUT_STATES (list of Mechanisms and/or OutputStates)

        Class methods:
            None

       **********************************************************************************************

       PUT SOME OF THIS STUFF IN ATTRIBUTES, BUT USE DEFAULTS HERE

        # - specification of System:  required param: SYSTEM
        # - kwDefaultController:  True =>
        #         takes over all unassigned ControlProjections (i.e., without a sender) in its System;
        #         does not take monitored states (those are created de-novo)
        # TBI: - CONTROL_PROJECTIONS:
        #         list of projections to add (and for which outputStates should be added)

        # - input_states: one for each performance/environment variable monitiored

        ControlProjection Specification:
        #    - wherever a ControlProjection is specified, using kwEVC instead of CONTROL_PROJECTION
        #     this should override the default sender SYSTEM_DEFAULT_CONTROLLER in ControlProjection._instantiate_sender
        #    ? expclitly, in call to "EVC.monitor(input_state, parameter_state=NotImplemented) method

        # - specification of function: default is default allocation policy (BADGER/GUMBY)
        #   constraint:  if specified, number of items in variable must match number of input_states in INPUT_STATES
        #                  and names in list in kwMonitor must match those in INPUT_STATES

       **********************************************************************************************

       NOT CURRENTLY IN USE:

        system : System
            System for which the EVCMechanism is the controller;  this is a required parameter.

        default_variable : Optional[number, list or np.ndarray] : `defaultControlAllocation <LINK]>`

    COMMENT


    Arguments
    ---------

    system : System : default None
        specifies the `System` for which the EVCMechanism should serve as a `controller <System_Base.controller>`;
        the EVCMechanism will inherit any `OutputStates <OutputState>` specified in the **monitor_for_control**
        argument of the `system <EVCMechanism.system>`'s constructor, and any `ControlSignals <ControlSignal>`
        specified in its **control_signals** argument.

    objective_mechanism : ObjectiveMechanism, List[OutputState or Tuple[OutputState, list or 1d np.array, list or 1d
    np.array]] : \
    default MonitoredOutputStatesOptions.PRIMARY_OUTPUT_STATES
        specifies either an `ObjectiveMechanism` to use for the EVCMechanism or a list of the OutputStates it should
        monitor; if a list of `OutputState specifications <ObjectiveMechanism_Monitored_Values>` is used,
        a default ObjectiveMechanism is created and the list is passed to its **monitored_output_states** argument.

    prediction_mechanism_type : CombinationFunction: default IntegratorMechanism
        the `Mechanism <Mechanism>` class used for `prediction Mechanism(s) <EVCMechanism_Prediction_Mechanisms>`.
        Each instance is named using the name of the `ORIGIN` Mechanism + "PREDICTION_MECHANISM"
        and assigned an `OutputState` with a name based on the same.

    prediction_mechanism_params : Optional[Dict[param keyword, param value]] : default None
        a `parameter dictionary <ParameterState_Specification>` passed to the constructor for a Mechanism
        of `prediction_mechanism_type`. The same parameter dictionary is passed to all
        `prediction mechanisms <EVCMechanism_Prediction_Mechanisms>` created for the EVCMechanism.

    function : function or method : ControlSignalGridSearch
        specifies the function used to determine the `allocation_policy` for the next execution of the
        EVCMechanism's `system <EVCMechanism.system>` (see `function <EVCMechanism.function>` for details).

    value_function : function or method : value_function
        specifies the function used to calculate the `EVC <EVCMechanism_EVC>` for the current `allocation_policy`
        (see `value_function <EVCMechanism.value_function>` for details).

    cost_function : function or method : LinearCombination(operation=SUM)
        specifies the function used to calculate the cost associated with the current `allocation_policy`
        (see `cost_function <EVCMechanism.cost_function>` for details).

    combine_outcome_and_cost_function : function or method : LinearCombination(operation=SUM)
        specifies the function used to combine the outcome and cost associated with the current `allocation_policy`,
        to determine its value (see `combine_outcome_and_cost_function` for details).

    save_all_values_and_policies : bool : default False
        specifes whether to save every `allocation_policy` tested in `EVC_policies` and their values in `EVC_values`.

    control_signals : List[Attribute of Mechanism or its function, ParameterState, or tuple[str, Mechanism]
        specifies the parameters to be controlled by the EVCMechanism
        (see `control_signals <EVCMechanism.control_signals>` for details).

    params : Optional[Dict[param keyword, param value]]
        a `parameter dictionary <ParameterState_Specification>` that can be used to specify the parameters for the
        Mechanism, its `function <EVCMechanism.function>`, and/or a custom function and its parameters.  Values
        specified for parameters in the dictionary override any assigned to those parameters in arguments of the
        constructor.

    name : str : default EVCMechanism-<index>
        a string used for the name of the Mechanism.
        If not is specified, a default is assigned by `MechanismRegistry`
        (see :doc:`Registry <LINK>` for conventions used in naming, including for default and duplicate names).

    prefs : Optional[PreferenceSet or specification dict] : default Process.classPreferences
        the `PreferenceSet` for the Mechanism.
        If it is not specified, a default is assigned using `classPreferences` defined in __init__.py
        (see `PreferenceSet <LINK>` for details).

    Attributes
    ----------

    system : System
        the `System` for which EVCMechanism is the `controller <System_Base.controller>`.

    prediction_mechanisms : List[ProcessingMechanism]
        list of `predictions mechanisms <EVCMechanism_Prediction_Mechanisms>` generated for the EVCMechanism's
        `system <EVCMechanism.system>` when the EVCMechanism is created, one for each `ORIGIN` Mechanism in the System.

    origin_prediction_mechanisms : Dict[ProcessingMechanism, ProcessingMechanism]
        dictionary of `prediction mechanisms <EVCMechanism_Prediction_Mechanisms>` added to the EVCMechanism's
        `system <EVCMechanism.system>`, one for each of its `ORIGIN` Mechanisms.  The key for each
        entry is an `ORIGIN` Mechanism of the System, and the value is the corresponding prediction Mechanism.

    prediction_mechanism_type : ProcessingMechanism : default IntegratorMechanism
        the `ProcessingMechanism <ProcessingMechanism>` class used for `prediction Mechanism(s)
        <EVCMechanism_Prediction_Mechanisms>`. Each instance is named based on `ORIGIN` Mechanism +
        "PREDICTION_MECHANISM", and assigned an `OutputState` with a name based on the same.

    prediction_mechanism_params : Dict[param key, param value] : default None
        a `parameter dictionary <ParameterState_Specification>` passed to `prediction_mechanism_type` when
        the `prediction Mechanism <EVCMechanism_Prediction_Mechanisms>` is created.  The same dictionary will be passed
        to all instances of `prediction_mechanism_type` created.

    predicted_input : Dict[ProcessingMechanism, value]
        dictionary with the `value <Mechanism_Base.value>` of each `prediction Mechanism
        <EVCMechanism_Prediction_Mechanisms>` listed in `prediction_mechanisms` corresponding to each `ORIGIN`
        Mechanism of the System. The key for each entry is the name of an `ORIGIN` Mechanism, and its
        value the `value <Mechanism_Base.value>` of the corresponding prediction Mechanism.

    objective_mechanism : ObjectiveMechanism
        the 'ObjectiveMechanism' used by the EVCMechanism to evaluate the performance of its `system
        <EVCMechanism.system>`.  If a list of OutputStates is specified in the **objective_mechanism** argument of the
        EVCMechanism's constructor, they are assigned as the `monitored_values <ObjectiveMechanism.monitored_values>`
        attribute for the `objective_mechanism <EVCMechanism.objective_mechanism>`.

    monitored_output_states : List[OutputState]
        list of the OutputStates monitored by `objective_mechanism <EVCMechanism.objective_mechanism>` (and listed in
        its `monitored_values <ObjectiveMechanism.monitored_values>` attribute), and used to evaluate the
        performance of the EVCMechanism's `system <EVCMechanism.system>`.

    COMMENT:
    [TBI]
        monitored_values : 3D np.array
            an array of values of the outputStates in `monitored_output_states` (equivalent to the values of
            the EVCMechanism's `input_states <EVCMechanism.input_states>`).
    COMMENT

    monitored_output_states_weights_and_exponents: List[Tuple[scalar, scalar]]
        a list of tuples, each of which contains the weight and exponent (in that order) for an OutputState in
        `monitored_outputStates`, listed in the same order as the outputStates are listed in `monitored_outputStates`.

    function : function : default ControlSignalGridSearch
        determines the `allocation_policy` to use for the next round of the System's
        execution. The default function, `ControlSignalGridSearch`, conducts an exhaustive (*grid*) search of all
        combinations of the `allocation_samples` of its ControlSignals (and contained in its
        `control_signal_search_space` attribute), by executing the System (using `run_simulation`) for each
        combination, evaluating the result using `value_function`, and returning the `allocation_policy` that yielded
        the greatest `EVC <EVCMechanism_EVC>` value (see `EVCMechanism_Default_Configuration` for additional details).
        If a custom function is specified, it must accommodate a **controller** argument that specifies an EVCMechanism
        (and provides access to its attributes, including `control_signal_search_space`), and must return an array with
        the same format (number and type of elements) as the EVCMechanism's `allocation_policy` attribute.

    COMMENT:
        NOTES ON API FOR CUSTOM VERSIONS:
            Gets controller as argument (along with any standard params specified in call)
            Must include **kwargs to receive standard args (variable, params, time_scale, and context)
            Must return an allocation policy compatible with controller.allocation_policy:
                2d np.array with one array for each allocation value

            Following attributes are available:
            controller._get_simulation_system_inputs gets inputs for a simulated run (using predictionMechanisms)
            controller._assign_simulation_inputs assigns value of prediction_mechanisms to inputs of `ORIGIN` Mechanisms
            controller.run will execute a specified number of trials with the simulation inputs
            controller.monitored_states is a list of the Mechanism OutputStates being monitored for outcome
            controller.input_value is a list of current outcome values (values for monitored_states)
            controller.monitored_output_states_weights_and_exponents is a list of parameterizations for OutputStates
            controller.control_signals is a list of control_signal objects
            controller.control_signal_search_space is a list of all allocationPolicies specifed by allocation_samples
            control_signal.allocation_samples is the set of samples specified for that control_signal
            [TBI:] control_signal.allocation_range is the range that the control_signal value can take
            controller.allocation_policy - holds current allocation_policy
            controller.output_values is a list of current control_signal values
            controller.value_function - calls the three following functions (done explicitly, so each can be specified)
            controller.cost_function - aggregate costs of control signals
            controller.combine_outcome_and_cost_function - combines outcomes and costs
    COMMENT

    value_function : function : default ValueFunction
        calculates the `EVC <EVCMechanism_EVC>` for a given `allocation_policy`.  It takes as its arguments an
        `EVCMechanism`, an **outcome** value and a list or ndarray of **costs**, uses these to calculate an EVC,
        and returns a three item tuple with the calculated EVC, and the outcome value and aggregated value of costs
        used to calculate the EVC.  The default, `ValueFunction`,  calls the EVCMechanism's `cost_function
        <EVCMechanism.cost_function>` to aggregate the value of the costs, and then calls its
        `combine_outcome_and_costs <EVCMechanism.combine_outcome_and_costs>` to calculate the EVC from the outcome
        and aggregated cost (see `EVCMechanism_Default_Configuration` for additional details).  A custom
        function can be assigned to `value_function` so long as it returns a tuple with three items: the calculated
        EVC (which must be a scalar value), and the outcome and cost from which it was calculated (these can be scalar
        values or `None`). If used with the EVCMechanism's default `function <EVCMechanism.function>`, a custom
        `value_function` must accommodate three arguments (passed by name): a **controller** argument that is the
        EVCMechanism for which it is carrying out the calculation; an **outcome** argument that is a value; and a
        `costs` argument that is a list or ndarray.  A custom function assigned to `value_function` can also call any
        of the `helper functions <EVCMechanism_Functions>` that it calls (however, see `note
        <EVCMechanism_Calling_and_Assigning_Functions>` above).

    cost_function : function : default LinearCombination(operation=SUM)
        calculates the cost of the `ControlSignals <ControlSignal>` for the current `allocation_policy`.  The default
        function sums the `cost <ControlSignal.cost>` of each of the EVCMechanism's `ControlSignals
        <EVCMechanism_ControlSignals>`.  The `weights <LinearCombination.weights>` and/or `exponents
        <LinearCombination.exponents>` parameters of the function can be used, respectively, to scale and/or
        exponentiate the contribution of each ControlSignal cost to the combined cost.  These must be specified as
        1d arrays in a *WEIGHTS* and/or *EXPONENTS* entry of a `parameter dictionary <ParameterState_Specification>`
        assigned to the **params** argument of the constructor of a `LinearCombination` function; the length of
        each array must equal the number of (and the values listed in the same order as) the ControlSignals in the
        EVCMechanism's `control_signals <EVCMechanism.control_signals>` attribute. The default function can also be
        replaced with any `custom function <EVCMechanism_Calling_and_Assigning_Functions>` that takes an array as
        input and returns a scalar value.  If used with the EVCMechanism's default `value_function
        <EVCMechanism.value_function>`, a custom `cost_function <EVCMechanism.cost_function>` must accommodate two
        arguments (passed by name): a **controller** argument that is the EVCMechanism itself;  and a **costs**
        argument that is a 1d array of scalar values specifying the `cost <ControlSignal.cost>` for each ControlSignal
        listed in the `control_signals` attribute of the ControlMechanism specified in the **controller** argument.

    combine_outcome_and_cost_function : function : default LinearCombination(operation=SUM)
        combines the outcome and cost for given `allocation_policy` to determine its `EVC <EVCMechanisms_EVC>`. The
        default function subtracts the cost from the outcome, and returns the difference.  This can be modified using
        the `weights <LinearCombination.weights>` and/or `exponents <LinearCombination.exponents>` parameters of the
        function, as described for the `cost_function <EVCMechanisms.cost_function>`.  The default function can also be
        replaced with any `custom function <EVCMechanism_Calling_and_Assigning_Functions>` that returns a scalar value.  If used with the EVCMechanism's default `value_function`, a custom
        If used with the EVCMechanism's default `value_function`, a custom combine_outcome_and_cost_function must
        accomoudate three arguments (passed by name): a **controller** argument that is the EVCMechanism itself; an
        **outcome** argument that is a 1d array with the outcome of the current `allocation_policy`; and a **cost**
        argument that is 1d array with the cost of the current `allocation_policy`.

    control_signal_search_space : 2d np.array
        an array each item of which is an `allocation_policy`.  By default, it is assigned the set of all possible
        allocation policies, using np.meshgrid to construct all permutations of `ControlSignal` values from the set
        specified for each by its `allocation_samples <EVCMechanism.allocation_samples>` attribute.

    EVC_max : 1d np.array with single value
        the maximum `EVC <EVCMechanism_EVC>` value over all allocation policies in `control_signal_search_space`.

    EVC_max_state_values : 2d np.array
        an array of the values for the OutputStates in `monitored_output_states` using the `allocation_policy` that
        generated `EVC_max`.

    EVC_max_policy : 1d np.array
        an array of the ControlSignal `intensity <ControlSignal.intensity> values for the allocation policy that
        generated `EVC_max`.

    save_all_values_and_policies : bool : default False
        specifies whether or not to save every `allocation_policy and associated EVC value (in addition to the max).
        If it is specified, each `allocation_policy` tested in the `control_signal_search_space` is saved in
        `EVC_policies`, and their values are saved in `EVC_values`.

    EVC_policies : 2d np.array
        array with every `allocation_policy` tested in `control_signal_search_space`.  The `EVC <EVCMechanism_EVC>`
        value of each is stored in `EVC_values`.

    EVC_values :  1d np.array
        array of `EVC <EVCMechanism_EVC>` values, each of which corresponds to an `allocation_policy` in `EVC_policies`;

    allocation_policy : 2d np.array : defaultControlAllocation
        determines the value assigned as the `variable <ControlSignal.variable>` for each `ControlSignal` and its
        associated `ControlProjection`.  Each item of the array must be a 1d array (usually containing a scalar)
        that specifies an `allocation` for the corresponding ControlSignal, and the number of items must equal the
        number of ControlSignals in the EVCMechanism's `control_signals` attribute.

    control_signals : ContentAddressableList[ControlSignal]
        list of the EVCMechanism's `ControlSignals <EVCMechanism_ControlSignals>`, including any that it inherited
        from its `system <EVCMechanism.system>`.

    """

    componentType = EVC_MECHANISM
    initMethod = INIT_FUNCTION_METHOD_ONLY


    classPreferenceLevel = PreferenceLevel.SUBTYPE
    # classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to Type automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'DefaultControlMechanismCustomClassPreferences',
    #     kp<pref>: <setting>...}

    class ClassDefaults(ControlMechanism_Base.ClassDefaults):
        # This must be a list, as there may be more than one (e.g., one per control_signal)
        variable = defaultControlAllocation

    from PsyNeuLink.Components.Functions.Function import LinearCombination
    # from Components.__init__ import DefaultSystem
    paramClassDefaults = ControlMechanism_Base.paramClassDefaults.copy()
    paramClassDefaults.update({PARAMETER_STATES: False})

    @tc.typecheck
    def __init__(self,
                 system=None,
                 objective_mechanism:tc.optional(tc.any(ObjectiveMechanism, list))=None,
                 prediction_mechanism_type=IntegratorMechanism.IntegratorMechanism,
                 prediction_mechanism_params:tc.optional(dict)=None,
                 control_signals:tc.optional(list) = None,
                 modulation:tc.optional(_is_modulation_param)=ModulationParam.MULTIPLICATIVE,
                 function=ControlSignalGridSearch,
                 value_function=ValueFunction,
                 cost_function=LinearCombination(operation=SUM,
                                                 context=componentType+COST_FUNCTION),
                 combine_outcome_and_cost_function=LinearCombination(operation=SUM,
                                                                     context=componentType+FUNCTION),
                 save_all_values_and_policies:bool=False,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 context=componentType+INITIALIZING):

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(system=system,
                                                  prediction_mechanism_type=prediction_mechanism_type,
                                                  prediction_mechanism_params=prediction_mechanism_params,
                                                  objective_mechanism=objective_mechanism,
                                                  control_signals=control_signals,
                                                  modulation=modulation,
                                                  function=function,
                                                  value_function=value_function,
                                                  cost_function=cost_function,
                                                  combine_outcome_and_cost_function=combine_outcome_and_cost_function,
                                                  save_all_values_and_policies=save_all_values_and_policies,
                                                  params=params)

        super(EVCMechanism, self).__init__(# default_variable=default_variable,
                                           # size=size,
                                           objective_mechanism=objective_mechanism,
                                           control_signals=control_signals,
                                           function=function,
                                           params=params,
                                           name=name,
                                           prefs=prefs,
                                           context=self)

    def _instantiate_input_states(self, context=None):
        """Instantiate PredictionMechanisms
        """
        if self.system is not None:
            self._instantiate_prediction_mechanisms(context=context)
        super()._instantiate_input_states(context=context)

    def _instantiate_prediction_mechanisms(self, context=None):
        """Add prediction Mechanism and associated process for each `ORIGIN` (input) Mechanism in the System

        Instantiate prediction_mechanisms for `ORIGIN` Mechanisms in self.system; these will now be `TERMINAL`
        Mechanisms:
            - if their associated input mechanisms were TERMINAL MECHANISMS, they will no longer be so
            - therefore if an associated input Mechanism must be monitored by the EVCMechanism, it must be specified
                explicitly in an OutputState, Mechanism, controller or System OBJECTIVE_MECHANISM param (see below)

        For each `ORIGIN` Mechanism in self.system:
            - instantiate a corresponding predictionMechanism
            - instantiate a Process, with a pathway that projects from the ORIGIN to the prediction Mechanism
            - add the process to self.system.processes

        Instantiate self.predicted_input dict:
            - key for each entry is an `ORIGIN` Mechanism of the System
            - value of each entry is the value of the corresponding predictionMechanism:
            -     each value is a 2d array, each item of which is the value of an InputState of the predictionMechanism

        Args:
            context:
        """

        # Dictionary of prediction_mechanisms, keyed by the ORIGIN Mechanism to which they correspond
        self.origin_prediction_mechanisms = {}

        # self.predictionProcesses = []

        # List of prediction Mechanism tuples (used by system to execute them)
        self.prediction_mechs = []

        # Get any params specified for predictionMechanism(s) by EVCMechanism
        try:
            prediction_mechanism_params = self.paramsCurrent[PREDICTION_MECHANISM_PARAMS]
        except KeyError:
            prediction_mechanism_params = {}


        for origin_mech in self.system.origin_mechanisms.mechanisms:

            # # IMPLEMENT THE FOLLOWING ONCE INPUT_STATES CAN BE SPECIFIED IN CONSTRUCTION OF ALL MECHANISMS
            # #           (AS THEY CAN CURRENTLY FOR ObjectiveMechanisms)
            # state_names = []
            # variables = []
            # for state_name in origin_mech.input_states.keys():
            #     state_names.append(state_name)
            #     variables.append(origin_mech_intputStates[state_name].instance_defaults.variable)

            # Instantiate predictionMechanism
            prediction_mechanism = self.paramsCurrent[PREDICTION_MECHANISM_TYPE](
                name=origin_mech.name + " " + PREDICTION_MECHANISM,
                default_variable = origin_mech.input_state.instance_defaults.variable,
                # default_variable=variables,
                # INPUT_STATES=state_names,
                params = prediction_mechanism_params,
                context=context,
            )
            prediction_mechanism._role = CONTROL
            prediction_mechanism.origin_mech = origin_mech

            # Assign projections to prediction_mechanism that duplicate those received by origin_mech
            #    (this includes those from ProcessInputState, SystemInputState and/or recurrent ones
            for orig_input_state, prediction_input_state in zip(origin_mech.input_states,
                                                            prediction_mechanism.input_states):
                for projection in orig_input_state.path_afferents:
                    MappingProjection(sender=projection.sender,
                                      receiver=prediction_input_state,
                                      matrix=projection.matrix)

            # Assign list of processes for which prediction_mechanism will provide input during the simulation
            # - used in _get_simulation_system_inputs()
            # - assign copy,
            #       since don't want to include the prediction process itself assigned to origin_mech.processes below
            prediction_mechanism.use_for_processes = list(origin_mech.processes.copy())

            # # FIX: REPLACE REFERENCE TO THIS ELSEWHERE WITH REFERENCE TO MECH_TUPLES BELOW
            self.origin_prediction_mechanisms[origin_mech] = prediction_mechanism

            # Add to list of EVCMechanism's prediction_object_items
            # prediction_object_item = prediction_mechanism
            self.prediction_mechs.append(prediction_mechanism)

            # Add to system execution_graph and execution_list
            self.system.execution_graph[prediction_mechanism] = set()
            self.system.execution_list.append(prediction_mechanism)

        self.prediction_mechanisms = MechanismList(self, self.prediction_mechs)

        # Assign list of destinations for predicted_inputs:
        #    the variable of the ORIGIN Mechanism for each process in the system
        self.predicted_input = {}
        for i, origin_mech in zip(range(len(self.system.origin_mechanisms)), self.system.origin_mechanisms):
            # self.predicted_input[origin_mech] = self.system.processes[i].origin_mechanisms[0].input_value
            self.predicted_input[origin_mech] = self.system.processes[i].origin_mechanisms[0].instance_defaults.variable

    def _instantiate_attributes_after_function(self, context=None):

        super()._instantiate_attributes_after_function(context=context)

        if self.system is None or not self.system.enable_controller:
            return

        cost_Function = self.cost_function
        if isinstance(cost_Function, Function):
            # Insure that length of the weights and/or exponents arguments for the cost_function
            #    matches the number of control signals
            num_control_projections = len(self.control_projections)
            if cost_Function.weights is not None:
                num_cost_weights = len(cost_Function.weights)
                if  num_cost_weights != num_control_projections:
                    raise EVCError("The length of the weights argument {} for the {} of {} "
                                   "must equal the number of its control signals {}".
                                   format(num_cost_weights,
                                          COST_FUNCTION,
                                          self.name,
                                          num_control_projections))
            if cost_Function.exponents is not None:
                num_cost_exponents = len(cost_Function.exponents)
                if  num_cost_exponents != num_control_projections:
                    raise EVCError("The length of the exponents argument {} for the {} of {} "
                                   "must equal the number of its control signals {}".
                                   format(num_cost_exponents,
                                          COST_FUNCTION,
                                          self.name,
                                          num_control_projections))

    @tc.typecheck
    def assign_as_controller(self, system:System, context=None):
        super().assign_as_controller(system=system, context=context)
        self._instantiate_prediction_mechanisms(context=context)

    def _execute(self,
                    variable=None,
                    runtime_params=None,
                    clock=CentralClock,
                    time_scale=TimeScale.TRIAL,
                    context=None):
        """Determine `allocation_policy <EVCMechanism.allocation_policy>` for next run of System

        Update prediction mechanisms
        Construct control_signal_search_space (from allocation_samples of each item in control_signals):
            * get `allocation_samples` for each ControlSignal in `control_signals`
            * construct `control_signal_search_space`: a 2D np.array of control allocation policies, each policy of which
              is a different combination of values, one from the `allocation_samples` of each ControlSignal.
        Call self.function -- default is ControlSignalGridSearch
        Return an allocation_policy
        """

        if not 'System.controller setter' in context:
            self._update_predicted_input()
        # self.system._cache_state()

        # CONSTRUCT SEARCH SPACE

        control_signal_sample_lists = []
        control_signals = self.control_signals

        # Get allocation_samples for all ControlSignals
        num_control_signals = len(control_signals)

        for control_signal in self.control_signals:
            control_signal_sample_lists.append(control_signal.allocation_samples)

        # Construct control_signal_search_space:  set of all permutations of ControlProjection allocations
        #                                     (one sample from the allocationSample of each ControlProjection)
        # Reference for implementation below:
        # http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
        self.control_signal_search_space = \
            np.array(np.meshgrid(*control_signal_sample_lists)).T.reshape(-1,num_control_signals)

        # EXECUTE SEARCH

        # IMPLEMENTATION NOTE:
        # self.system._store_system_state()

        allocation_policy = self.function(controller=self,
                                          variable=variable,
                                          runtime_params=runtime_params,
                                          time_scale=time_scale,
                                          context=context)
        # IMPLEMENTATION NOTE:
        # self.system._restore_system_state()

        return allocation_policy

    def _update_predicted_input(self):
        """Assign values of prediction mechanisms to predicted_input

        Assign value of each predictionMechanism.value to corresponding item of self.predictedIinput
        Note: must be assigned in order of self.system.processes

        """

        # Assign predicted_input for each process in system.processes

        # The number of ORIGIN mechanisms requiring input should = the number of prediction mechanisms
        num_origin_mechs = len(self.system.origin_mechanisms)
        num_prediction_mechs = len(self.origin_prediction_mechanisms)
        if num_origin_mechs != num_prediction_mechs:
            raise EVCError("PROGRAM ERROR:  The number of ORIGIN mechanisms ({}) does not equal"
                           "the number of prediction_predictions mechanisms ({}) for {}".
                           format(num_origin_mechs, num_prediction_mechs, self.system.name))
        for origin_mech in self.system.origin_mechanisms:
            # Get origin Mechanism for each process
            # Assign value of predictionMechanism to the entry of predicted_input for the corresponding ORIGIN Mechanism
            self.predicted_input[origin_mech] = self.origin_prediction_mechanisms[origin_mech].value
            # self.predicted_input[origin_mech] = self.origin_prediction_mechanisms[origin_mech].output_state.value

    def run_simulation(self,
                       inputs,
                       allocation_vector,
                       runtime_params=None,
                       time_scale=TimeScale.TRIAL,
                       context=None):
        """
        Run simulation of `System` for which the EVCMechanism is the `controller <System_Base.controller>`.

        Arguments
        ----------

        inputs : List[input] or ndarray(input) : default default_variable
            the inputs used for each in a sequence of executions of the Mechanism in the `System`.  This should be the
            `value <Mechanism_Base.value> for each `prediction Mechanism <EVCMechanism_Prediction_Mechanisms>` listed
            in the `prediction_mechanisms` attribute.  The inputs are available from the `predicted_input` attribute.

        allocation_vector : (1D np.array)
            the allocation policy to use in running the simulation, with one allocation value for each of the
            EVCMechanism's ControlSignals (listed in `control_signals`).

        runtime_params : Optional[Dict[str, Dict[str, Dict[str, value]]]]
            a dictionary that can include any of the parameters used as arguments to instantiate the mechanisms,
            their functions, or Projection(s) to any of their states.  See `Mechanism_Runtime_Parameters` for a full
            description.

        time_scale :  TimeScale : default TimeScale.TRIAL
            specifies whether the Mechanism is executed on the `TIME_STEP` or `TRIAL` time scale.

        """

        if self.value is None:
            # Initialize value if it is None
            self.value = self.allocation_policy

        # Implement the current allocation_policy over ControlSignals (outputStates),
        #    by assigning allocation values to EVCMechanism.value, and then calling _update_output_states
        for i in range(len(self.control_signals)):
            # self.control_signals[list(self.control_signals.values())[i]].value = np.atleast_1d(allocation_vector[i])
            self.value[i] = np.atleast_1d(allocation_vector[i])
        self._update_output_states(runtime_params=runtime_params, time_scale=time_scale,context=context)

        # Execute simulation run of system for the current allocation_policy
        sim_clock = Clock('EVC SIMULATION CLOCK')

        self.system.run(inputs=inputs, clock=sim_clock, time_scale=time_scale, context=context)

        # Get outcomes for current allocation_policy
        #    = the values of the monitored output states (self.input_states)
        # self.objective_mechanism.execute(context=EVC_SIMULATION)
        monitored_states = self._update_input_states(runtime_params=runtime_params, time_scale=time_scale,context=context)

        for i in range(len(self.control_signals)):
            self.control_signal_costs[i] = self.control_signals[i].cost

        return monitored_states

    # The following implementation of function attributes as properties insures that even if user sets the value of a
    #    function directly (i.e., without using assign_params), it will still be wrapped as a UserDefinedFunction.
    # This is done to insure they can be called by value_function in the same way as the defaults
    #    (which are all Functions), and so that they can be passed a params dict.

    # def wrap_function(self, function):
    #     if isinstance(function, function_type):
    #         return ValueFunction(function)
    #     elif inspect.isclass(assignment) and issubclass(assignment, Function):
    #         self._value_function = ValueFunction()
    #     else:
    #         self._value_function = assignment

    @property
    def value_function(self):
        return self._value_function

    @value_function.setter
    def value_function(self, assignment):
        if isinstance(assignment, function_type):
            self._value_function = ValueFunction(assignment)
        elif assignment is ValueFunction:
            self._value_function = ValueFunction()
        else:
            self._value_function = assignment

    @property
    def cost_function(self):
        return self._cost_function

    @cost_function.setter
    def cost_function(self, value):
        from PsyNeuLink.Components.Functions.Function import UserDefinedFunction
        if isinstance(value, function_type):
            udf = UserDefinedFunction(function=value)
            self._cost_function = udf
        else:
            self._cost_function = value

    @property
    def combine_outcome_and_cost_function(self):
        return self._combine_outcome_and_cost_function

    @combine_outcome_and_cost_function.setter
    def combine_outcome_and_cost_function(self, value):
        from PsyNeuLink.Components.Functions.Function import UserDefinedFunction
        if isinstance(value, function_type):
            udf = UserDefinedFunction(function=value)
            self._combine_outcome_and_cost_function = udf
        else:
            self._combine_outcome_and_cost_function = value
