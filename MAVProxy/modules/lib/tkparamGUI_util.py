class ParamUpdateList():
    '''List of Params'''
    def __init__(self, params):
        self.params = params

class ParamUpdate():
    '''Updated value for a param'''
    def __init__(self, name, value):
        self.name = name
        self.value = value
