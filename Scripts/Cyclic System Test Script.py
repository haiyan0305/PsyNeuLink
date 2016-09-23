from PsyNeuLink.Functions.System import system
from PsyNeuLink.Functions.Process import process
from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.Transfer import Transfer
from PsyNeuLink.Functions.Process import Mapping

a = Transfer(name='a')
b = Transfer(name='b')
c = Transfer(name='c')
d = Transfer(name='d')
e = Transfer(name='e')

# fb1 = Mapping(sender=c, receiver=b, name='fb1')
# fb2 = Mapping(sender=d, receiver=e, name = 'fb2')

# fb3 = Mapping(sender=e, receiver=a, name = 'fb3')

# p1 = process(configuration=[a, b, c, d], name='p1')

p1e = process(configuration=[a, b, c, e], name='p1e')
p2 = process(configuration=[e, b, c, d], name='p2')

# WORKS (treats e as an origin):
# a = system(processes=[p1e, p2], name='system')
        # Senders to b:
        # 	a
        # 	e
        # Senders to c:
        # 	b
        # a is origin
        # e is origin
        # Senders to d:
        # 	c
        #

# HAS CYCLE (does NOT treat e as an origin):
a = system(processes=[p2, p1e], name='system')
        # Senders to e:
        # 	c
        # a is origin
        # Senders to d:
        # 	c
        # Senders to b:
        # 	e
        # 	a
        # Senders to c:
        # 	b






# p4 = process(configuration=[a, b, c], name='p4')
# p5= process(configuration=[c, d, e], name='p5')
# a = system(processes=[p1, p2, p3], name='system')


# a = system(processes=[p4, p5], name='system')

a.inspect()

for projection in e.inputState.receivesFromProjections:
    print("Projection name: {}; sender: {};  receiver: {}".
          format(projection.name, projection.sender.owner.name, projection.receiver.owner.name))

a.execute()
