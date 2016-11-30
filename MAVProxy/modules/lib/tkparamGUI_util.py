class ParamUpdateList():
    '''List of parameters to be updated. Sent from MAVProxy to GUI.'''
    def __init__(self, params):
        self.params = params

class ParamSendList():
    '''List of parameters to be sent to the aircraft. Sent from GUI to MAVProxy.'''
    def __init__(self, params):
        self.params = params

class ParamFetch():
    '''Message to initiate a parameter fetch. Sent from GUI to MAVProxy.'''
    pass

class Param():
    '''A Parameter. Not to be sent down pipe by itself (use an above class).'''
    def __init__(self, name, value):
        self.name = name
        self.value = value
