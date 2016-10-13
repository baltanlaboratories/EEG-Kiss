'''
Created on 19 mei 2015

@author: Bas.Kooiker
'''

class Foo:
    def func(self, **args):
        f = args.get('one', None)
        if f:
            print f
            
foo = Foo()
foo.func(one=13)
