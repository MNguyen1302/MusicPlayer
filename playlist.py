class Playlist:
    def __init__(self,id,name):
        self.__id=id
        self.__name=name
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self,id):
        self.__id=id
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self,name):
        self.__name=name
    
    