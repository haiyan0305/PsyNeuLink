# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# ******************************************  LearningSignal *****************************************************

"""
Overview
--------

A LearningSignal is a type of `ModulatorySignal <ModulatorySignal>` that is specialized for use with a
`LearningMechanism` and one or more `LearningProjections <LearningProjection>`, to modify the `matrix
<MappingProjection.matrix>` parameter of the `MappingProjections <MappingProjection>` to which they project.  A
LearningSignal receives the value of a `learning_signal <LearningMechanism>` calculated by the `LearningMechanism` to
which it belongs, which in general is a matrix of weight changes to be made to the `matrix <MappingProjection>`
parameter of the MappingProjection(s) being learned.  The LearningSignal assigns its `learning_signal
<LearningSignal.learning_signal>` as the value of its LearningProjection(s), which convey it to the
MappingProjections` *MATRIX* `ParameterState(s) <ParameterState>`, which in turn modify the matrix parameter(s) of
the MappingProjection(s) being learned.

.. _LearningSignal_Creation:

Creating a LearningSignal
------------------------

A LearningSignal is created automatically whenever a `MappingProjection` is `specified for learning
<LearningMechanism_Creation>` and the Projection belongs to the same `Composition <Composition>` as the
`LearningMechanism`. LearningSignals can also be specified in the **learning_signals** argument of the constructor
for a `LearningMechanism`. Although a LearningSignal can be created directly using its constructor (or any of the
other ways for `creating an OutputState <OutputStates_Creation>`), this is neither necessary nor advisable, as a
LearningSignal has dedicated Components and requirements for configuration that must be met for it to function properly.

.. _LearningSignal_Specification:

Specifying LearningSignals
~~~~~~~~~~~~~~~~~~~~~~~~~~

When a LearningSignal is specified in the **learning_signals** argument of the constructor for a `LearningMechanism`,
the `ParameterState(s) <ParameterState>` of the `MappingProjection(s) <MappingProjection>` being learning must be
specified.  This can take any of the following forms:

  * an existing LearningSignal, or a reference to the class (in which case a default LearningSignal is created);

  * a **ParameterState**, which must be for the `matrix <MappingProjection.matrix>` parameter of the
    `MappingProjection` to be learned;
  ..
  * a **Projection**, which must be either a `LearningProjection`, or a `MappingProjection` to which the
    LearningSignal should send a `LearningProjection`.  In both cases, it is assumed that the LearningProjection
    projects to the *MATRIX* `ParameterState` of a `MappingProjection`.
  ..
  * a **tuple**, with the name of the parameter as its 1st item. and the Projection to which it belongs as the 2nd;
    note that this is a convenience format, which is simpler to use than a specification dictionary (see below),
    but precludes specification of any `parameters <LearningSignal_Structure>` for the LearningSignal.
  ..
  * a **specification dictionary**, that must contain at least the following two entries:

    * *NAME*:str
        the string must be the name of the `MappingProjection` to be learned; the LearningSignal is named by
        appending "_LearningSignal" to the name of the Projection.

    * *PROJECTION*:MappingProjection
        the MappingProjection must be valid `projection specification <Projection_Specification>`
        for the one to be learned.

    The dictionary can also contain entries for any other LearningSignal attributes to be specified
    (e.g., a *LEARNING_RATE* entry); see `below <LearningSignal_Structure>` for a description of LearningSignal
    attributes.

.. _LearningSignal_Structure:

Structure
---------

A LearningSignal is owned by an `LearningMechanism`, and "trains" one or more `MappingProjections <MappingProjection>`
by modulating the value of their `matrix <MappingProjection.matrix>` parameters.  This is governed by three
attributes of the LearningSignal, as described below.

.. _LearningSignal_Projections:

Projections
~~~~~~~~~~~

When a LearningSignal is created, it can be assigned one or more `LearningProjections <LearningProjection>`,
using either the **projections** argument of its constructor, or in an entry of a dictionary assigned to the
**params** argument with the key *PROJECTIONS*.  These will be assigned to its `efferents
<LearningSignal.efferents>` attribute.  See `State Projections <State_Projections>` for additional details
concerning the specification of Projections when creating a State.

.. note::
   Although a LearningSignal can be assigned more than one `LearningProjection`, all of those Projections will convey
   the same `learning_signal <LearningMechanism>` (received from the LearningMechanism to which the LearningSignal
   belongs).  Thus, for them to be meaningful, they should project to MappingProjections that are responsible for
   identical or systematically-related `error signals <LearningMechanism.error_signal>` (e.g., as in `convolutional
   networks <html LINK>`_.

.. _LearningSignal_Modulation:

Modulation
~~~~~~~~~~

A LearningSignal has a `modulation <LearningSignal.modulation>` attribute that determines how the LearningSignal's
`value <LearningSignal.value>` (i.e., its `learning_signal <LearningSignal.learning_signal>`) is used by the
ParameterState(s) to which it projects to modify the `matrix <MappingProjection.matrix>` parameter(s) of their
MappingProjection(s) (see `ModulatorySignal Modulation <ModulatorySignal_Modulation>` for an explanation of how the
`modulation <LearningSignal.modulation>` attribute is specified and used to modify the value of a parameter).  The
default value is set to the value of the `modulation <LearningMechanism.modulation>` attribute of the
LearningMechanism to which the LearningSignal belongs;  this is the same for all of the LearningSignals belonging to
that LearningMechanism. The default value of `modulation <LearningMechanism.modulation>` for a LearningMechanism is
`ADDITIVE`, which causes the `learning_signal <LearningSignal.learning_signal>` (i.e., its matrix of weight changes)
to be added to the `matrix <MappingProjection.matrix>` parameter of the MappingProjection being learned.  The
`modulation <LearningSignal.modulation>` can be individually specified for a LearningSignal using a
specification dictionary where the LearningSignal itself is specified, as described
`above <LearningSignal_Specification>`. The `modulation <LearningSignal.modulation>` value of a LearningSignal is
used by all of the `LearningProjections <LearningProjection>` that project from that LearningSignal.

.. _LearningSignal_Learning_Rate:

Learning Rate and Function
~~~~~~~~~~~~~~~~~~~~~~~~~~

A LearningSignal has a `learning_rate <LearningSignal.learning_rate>` attribute that can be used to specify the
`learning_rate <LearningProjection.learning_rate>` parameter for its `LearningProjection(s) <LearningProjection>`
(i.e., those listed in its `efferents <LearningSignal.efferents>` attribute).  If specified, it is applied
multiplicatively to the LearningProjection`s `learning_signal <LearningProjection.learning_signal>` and thus can be
used to modulate the learning_rate in addition to (and on top of) one specified for the `LearningMechanism` or its
`function <LearningMechanism.function>`.  Specification of the `learning_rate <LearningSignal.learning_rate>` for a
LearningSignal supersedes the `learning_rate <LearningProjection.learning_rate>` for its LearningProjections,
as well the `learning_rate <Process.learning_rate>` for any Process(es) and/or the
`learning_rate <System.learning_rate>` for any System(s) to which the LearningSignal's owner belongs
(see `learning_rate <LearningMechanism_Learning_Rate>` of LearningMechanism for additional details).

The `function <LearningSignal.function>` of a LearningSignal converts the `learning_signal
<LearningMechanism.learning_signal>` it receives from the LearningMechanism to which it belongs to its `value
<LearningSignal.value>` (i.e., the LearningSignal's `learning_signal <LearningSignal.learning_signal>`). By default
this is an identity function (`Linear` with **slope**\\ =1 and **intercept**\\ =0), that simply uses the
LearningMechanism's `learning_signal <LearningMechanism.learning_signal>` as its own.  However, the LearningSignal's
`function <LearningSignal.function>` can be assigned another `TransferFunction`, or any other function that takes a
scalar, ndarray or matrix and returns a similar value.

.. note:: The `index <OutputState.OutputState.index>` and `assign <OutputState.OutputState.assign>`
        attributes of a LearningSignal are automatically assigned and should not be modified.


.. _LearningSignal_Execution:

Execution
---------

A LearningSignal cannot be executed directly.  It is executed whenever the `LearningMechanism` to which it belongs is
executed.  When this occurs, the LearningMechanism provides the LearningSignal with a
`learning_signal <LearningMechanism.learning_signal>`, that is used by its `function <LearningSignal.function>` to
compute its `value <LearningSignal.value>` (i.e., its own `learning_signal <LearningSignal.learning_signal>` for that
`TRIAL`. That value is used by its `LearningProjection(s) <LearningProjection>` to modify the `matrix
<MappingProjection.matrix>` parameter of the `MappingProjection(s) <MappingProjection>` to which the LearningSignal
projects.

.. note::
   The changes in a MappingProjection's matrix parameter in response to the execution of a LearningSignal are not
   applied until the MappingProjection is next executed; see :ref:`Lazy Evaluation <LINK>` for an explanation of
   "lazy" updating).

Class Reference
---------------

"""

import typecheck as tc

from psyneulink.components.functions.function import Linear, ModulationParam, _is_modulation_param
from psyneulink.components.states.modulatorysignals.modulatorysignal import ModulatorySignal
from psyneulink.components.states.outputstate import PRIMARY
from psyneulink.components.states.state import State_Base
from psyneulink.globals.context import ContextFlags
from psyneulink.globals.keywords import COMMAND_LINE, LEARNED_PARAM, LEARNING_PROJECTION, LEARNING_SIGNAL, OUTPUT_STATE_PARAMS, PARAMETER_STATE, PARAMETER_STATES, PROJECTION_TYPE, RECEIVER
from psyneulink.globals.preferences.componentpreferenceset import is_pref_set
from psyneulink.globals.preferences.preferenceset import PreferenceLevel
from psyneulink.globals.utilities import parameter_spec

__all__ = [
    'LearningSignal', 'LearningSignalError',
]


class LearningSignalError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value


    def __str__(self):
        return repr(self.error_value)


class LearningSignal(ModulatorySignal):
    """
    LearningSignal(                                      \
        owner,                                           \
        function=Linear(),                               \
        modulation=ModulationParam.MULTIPLICATIVE        \
        learning_rate=None                               \
        params=None,                                     \
        projections=None,                                \
        name=None,                                       \
        prefs=None)

    A subclass of `ModulatorySignal <ModulatorySignal>` used by a `LearningMechanism` to modify the `matrix
    <MappingProjection.matrix>` parameter of one more more `MappingProjection(s) <MappingProjection>`.

    COMMENT:

        Description
        -----------
            The LearningSignal class is a subtype of the OutputState type in the State category of Component,
            It is used as the sender for LearningProjections
            Its FUNCTION updates its value:
                note:  currently, this is the identity function, that simply maps variable to self.value

        Class attributes:
            + componentType (str) = LEARNING_SIGNAL
            + paramClassDefaults (dict)
                + FUNCTION (Linear)
                + FUNCTION_PARAMS   (Operation.PRODUCT)

        Class methods:
            function (executes function specified in params[FUNCTION];  default: Linear)

        StateRegistry
        -------------
            All OutputStates are registered in StateRegistry, which maintains an entry for the subclass,
              a count for all instances of it, and a dictionary of those instances
    COMMENT


    Arguments
    ---------

    owner : LearningMechanism
        specifies the `LearningMechanism` to which to assign the LearningSignal.

    function : Function or method : default Linear
        specifies the function used by the LearningSignal to generate its
        `learning_signal <LearningSignal.learning_signal>`.

    learning_rate : float or None : default None
        specifies the learning_rate for the LearningSignal's `LearningProjections <LearningProjection>`
        (see `learning_rate <LearningSignal.learning_rate>` for details).

    modulation : ModulationParam : default ModulationParam.MULTIPLICATIVE
        specifies the way in which the `value <LearningSignal.value>` of the LearningSignal is used to modify the value
        of the `matrix <MappingProjection.matrix>` parameter for the `MappingProjection(s) <MappingProjection>` to which
        the LearningSignal's `LearningProjection(s) <LearningProjection>` project.

    params : Dict[param keyword: param value] : default None
        a `parameter specification dictionary <ParameterState_Specification>` that can be used to specify the
        parameters for the LearningSignal and/or a custom function and its parameters. Values specified for
        parameters in the dictionary override any assigned to those parameters in arguments of the constructor.

    projections : list of Projection specifications
        specifies the `LearningProjection(s) <GatingProjection>` to be assigned to the LearningSignal, and that will be
        listed in its `efferents <LearningSignal.efferents>` attribute (see `LearningSignal_Projections` for additional
        details).

    name : str : default see ModulatorySignal `name <ModulatorySignal.name>`
        specifies the name of the LearningSignal; see LearningSignal `name <ModulatorySignal.name>` for additional
        details.

    prefs : PreferenceSet or specification dict : default State.classPreferences
        specifies the `PreferenceSet` for the LearningSignal; see `prefs <LearningSignal.prefs>` for details.


    Attributes
    ----------

    owner : LearningMechanism
        the `LearningMechanism` to which the LearningSignal belongs.

    variable : number, list or np.ndarray
        used by `function <LearningSignal.function>` to generate the LearningSignal's
        `learning_signal <LearningSignal.learning_signal>`.

    function : TransferFunction :  default Linear(slope=1, intercept=0)
        converts `variable <LearningSignal.variable>` into the LearningSignal's
        `learning_signal <LearningSignal.learning_signal>`. The default is the identity function, which assigns the
        LearningSignal's `variable <LearningSignal.variable>` as its `learning_signal <LearningSignal.learning_signal>`.

    learning_rate : float : None
        determines the learning rate for the LearningSignal.  It is used to specify the
        `learning_rate <LearningProjection.learning_rate>` parameter for its LearningProjection(s) (listed in the
        `efferents <LearningSignal.efferents>` attribute). See `LearningSignal_Learning_Rate` for additional details.

    value : number, list or np.ndarray
        result of the LearningSignal's `function <LearningSignal.function>`; same as its
        `learning_signal <LearningSignal.learning_signal>`.

    learning_signal : number, ndarray or matrix
        result of the LearningSignal's `function <LearningSignal.function>`; same as its `value <LearningSignal.value>`.

    efferents : [List[LearningProjection]]
        a list of the `LearningProjections <LearningProjection>` assigned to (i.e., that project from) the
        LearningSignal.

    modulation : ModulationParam
        determines the way in which the `value <LearningSignal.value>` of the LearningSignal is used to modify the
        value of the `matrix <MappingProjection.matrix>` parameter for the `MappingProjection` to which the
        LearningSignal's `LearningProjection(s) <LearningProjection>` project.

    name : str
        name of the LearningSignal; the first LearningSignal is always assigned the name *LEARNING_SIGNAL*;  any
        additional LearningSignals without the **name** argument of their constructor specified are assigned a default
        name (see `name <ModulatorySignal.name>`).

        .. note::
            Unlike other PsyNeuLink components, State names are "scoped" within a Mechanism, meaning that States with
            the same name are permitted in different Mechanisms.  However, they are *not* permitted in the same
            Mechanism: States within a Mechanism with the same base name are appended an index in the order of their
            creation.

    prefs : PreferenceSet or specification dict
        the `PreferenceSet` for the LearningSignal; if it is not specified in the **prefs** argument of the constructor,
        a default is assigned using `classPreferences` defined in __init__.py (see :doc:`PreferenceSet <LINK>` for
        details).

    """

    #region CLASS ATTRIBUTES

    componentType = LEARNING_SIGNAL
    paramsType = OUTPUT_STATE_PARAMS

    stateAttributes = ModulatorySignal.stateAttributes

    connectsWith = [PARAMETER_STATE]
    connectsWithAttribute = [PARAMETER_STATES]
    projectionSocket = RECEIVER
    modulators = []

    classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to TYPE automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'OutputStateCustomClassPreferences',
    #     kp<pref>: <setting>...}

    paramClassDefaults = State_Base.paramClassDefaults.copy()
    paramClassDefaults.update({
        PROJECTION_TYPE: LEARNING_PROJECTION,
        LEARNED_PARAM:None
    })
    #endregion


    @tc.typecheck
    def __init__(self,
                 owner=None,
                 reference_value=None,
                 variable=None,
                 size=None,
                 index=PRIMARY,
                 assign=None,
                 function=Linear(),
                 learning_rate: tc.optional(parameter_spec) = None,
                 modulation:tc.optional(_is_modulation_param)=None,
                 projections=None,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 context=None):

        if context is None:
            context = ContextFlags.COMMAND_LINE
            self.context.source = ContextFlags.COMMAND_LINE
        else:
            context = ContextFlags.CONSTRUCTOR
            self.context.source = ContextFlags.CONSTRUCTOR

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(function=function,
                                                  learning_rate=learning_rate,
                                                  params=params)

        # FIX: 5/26/16
        # IMPLEMENTATION NOTE:
        # Consider adding self to owner.output_states here (and removing from LearningProjection._instantiate_sender)
        #  (test for it, and create if necessary, as per OutputStates in LearningProjection._instantiate_sender),

        # Validate sender (as variable) and params, and assign to variable and paramInstanceDefaults
        super().__init__(owner=owner,
                         reference_value=reference_value,
                         variable=variable,
                         size=size,
                         modulation=modulation,
                         index=index,
                         assign=None,
                         projections=projections,
                         params=params,
                         name=name,
                         prefs=prefs,
                         context=context,
                         function=function,
                         )

    def _get_primary_state(self, projection):
        return projection.parameter_state

    @property
    def learning_signal(self):
        return self.value

    def _assign_default_state_name(self, context=None):
        # Preserve LEARNING_SIGNAL as name of the first LearningSignal
        #    as documented, and as it is used by System._instantiate_learning_graph
        if self.name is self.componentName:
            return self.name
        # Otherwise, allow ModulatorySignal to construct default name as usual
        else:
            super()._assign_default_state_name(context=context)

