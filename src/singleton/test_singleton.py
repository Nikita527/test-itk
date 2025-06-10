from singleton import SingletonWithMeta, SingletonWithNew, instance

a = SingletonWithMeta()
b = SingletonWithMeta()
assert a is b
a.value = 100
assert b.value == 100

c = SingletonWithNew()
d = SingletonWithNew()
assert c is d
c.value = 200
assert d.value == 200

e1 = instance
e2 = instance
assert e1 is e2
e1.value = 300
assert e2.value == 300
