from PsyNeuLink.Components.Process import *

# myMechanism = DDM(function=NavarroAndFuss(drift_rate=1.0,
#                                       threshold=10.0,
#                                       starting_point=0.0),
#                   name='My_DDM',
#                   prefs={REPORT_OPUTPUT_PREF: PreferenceEntry(True,PreferenceLevel.INSTANCE)}
#                   )
#

myMechanism = DDM(function=BogaczEtAl(drift_rate=.1,
                                      threshold=1.0,
                                      starting_point=0.0),
                  name='My_DDM',
                  prefs={REPORT_OUTPUT_PREF: PreferenceEntry(True,PreferenceLevel.INSTANCE)}
                  )


# simple_ddm_process = process('Simple DDM Process')
simple_ddm_process = process(pathway=[myMechanism],
                             prefs={REPORT_OUTPUT_PREF: True})
simple_ddm_process.execute(1.0)

print ('Decision variable: ', myMechanism.output_values[0])
print ('RT mean: ', myMechanism.output_values[1])
print ('ER mean: ', myMechanism.output_values[2])

