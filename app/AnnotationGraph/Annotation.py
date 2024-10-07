from AnnotationGraph import TrackedMap

class Annotation(TrackedMap):
    def __init__(self):
        self.id = ''
        self.label=''
        self.layerId=''
        self.startId=''
        self.endId=''
        self.parentId=''
        self.ordinal=0
        self.confidence=0
        self.turn=''
            
    def get_id(self):
        return self.id
    
    def set_id(self, new_id):
        self.id=new_id

    def get_label(self):
        return self.label, self.confidence
    
    def set_label(self, new_label, new_confidence):
        self.label=new_label
        self.confidence=new_confidence

    def get_layerId(self):
        return self.layerId

    def set_layerId(self, new_layerId):
        self.layerId=new_layerId
    
    def get_layerId(self):
        return self.layerId