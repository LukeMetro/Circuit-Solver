'''
Luke Metro - lmetro - Section C - 15-112
History.py

History class to store the key of the object that was deleted from the
adjacency list and the list before it was deleted
'''

class History(object):

	def __init__(self, data, graph, deletedComponentKey, currentComponentKey, 
				operation):
		self.data = data
		self.graph = graph
		self.deletedKey = deletedComponentKey
		self.presentKey = currentComponentKey
		self.operation = operation