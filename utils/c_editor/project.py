import os
from xml.dom.minidom import parse

class CharacterProject:
    def __init__(self, path):
        self.doc = parse(path)
        root = self.doc.getElementsByTagName('character')[0]
        #root = self.doc.DocumentElement
        self.directory = os.path.dirname(path) + '/'

        image = root.getAttribute('image')

        # movements
        self.movements = []
        for mov in self.doc.getElementsByTagName('movement'):
            self.movements.append(mov.getAttribute('name'))

    def get_picture(self, movement):
        mov = self.doc.getElementsByTagName('movement')[0]
        img = mov.getElementsByTagName('frame')[0].getAttribute('image')
        return self.directory + img