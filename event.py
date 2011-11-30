#!/usr/bin/env python

#
# Name: Eventobject
# Description: Event triggering
# This is a part of AltExt project.
#


##########
# Hook object
class Hook:
    def __init__(self):
        self.handlers = set()

    def Handle(self, handler):
        self.handlers.add(handler)
        return self

    def Unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Cannot unhandle event.")
        return self

    def Fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def GetHandlerCount(self):
        return len(self.handlers)

    __iadd__ = Handle
    __isub__ = Unhandle
    __call__ = Fire
    __len__  = GetHandlerCount
