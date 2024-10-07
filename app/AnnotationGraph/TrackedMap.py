class TrackedMap:
    def __init__(self):
        self.id=''
        self.schema=''
        self.anchors=''
        self.annotations=''
        
    def set_id(self, new_id):
        self.id = new_id
    
    def get_id(self):
        return self.id