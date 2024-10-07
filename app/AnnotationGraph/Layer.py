import TrackedMap

class Layer(TrackedMap):
    def __init__(self):
        self.id=''
        self.description=''
        self.alignmnet=''
        self.peers=''
        self.peersOverlap=''
        self.saturated=''
        self.parentId=''
        self.parentIncludes=''