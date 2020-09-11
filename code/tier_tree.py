# vim: set sw=4 noet ts=4 fileencoding=utf-8:
import logging
import pdb
from airtable_reader import Airtable_Reader

class Tier_Tree():

	custom_tier_tree = []

	def __init__(self):
		self.log = self.setup_logger(logging.DEBUG)
		self.ar = Airtable_Reader()

	def setup_logger(self, logger_level):
		''' 
			Args: logger supports levels DEBUG, INFO, WARNING, ERROR, CRITICAL.
			logger_level should be passed in in the format logging.LEVEL 
		'''

		logging.basicConfig(level=logger_level)
		logger = logging.getLogger(__name__)
		return logger

	def class_constructor(self, arg):
		'''
			This function is called when __init__ is called because 
			it is set as class attribute function for __init__. 
			Thus, arguments passed here will get set. 
			Pass in a dict or list for args to init multiple parameters.
		'''

		# Sets instance attributes
		self.instance_attrs = arg
		#constructor_arg = arg

	def create_minimum_attributes_dict(self, name, hierarchy_level):
		'''
			The idea behind this is that this attributes_dict is the 
			MINIMUM for all tier_classes created. They may include more 
			class attributes, but MUST satisfy these. It will be passed 
			in to New_Tier_Class and constructed every time a tier class 
			like "Main" or "Tasks" is setup.
		'''
		attributes_dict = {
			"__init__" : self.class_constructor,
			"name" : name,
			"hierarchy_level" : hierarchy_level,
			#XXX user must input connections later, but all classes 
			# have this field is a class attribute! 
			# I need an instance attribute!
			#XXX these are made automatically by the Ruminant template as they
			# are field names
			"connections_above" : [],
			"connections_below" : [],
			"connections_equal_how" : [],
			"connections_equal_why" : [],
			"is_root" : False,
		}
		return attributes_dict

	def create_tier_class(self, attributes_dict):
		''' 
			Creates a class dynamically, setting CLASS attributes as passed in.
		'''

		# Dynamically create class based on user input
		# type(
			# class_name, 
			# base / inheritance, 
			# attributes (in the form of a dictionary)
			# )
		name = attributes_dict["name"]
		#XXX Base of type Tier??
		New_Tier_Class = type(
			name, 
			(object,), 
			attributes_dict	
		)
		return New_Tier_Class

	def setup_tier_tree_attributes(self, 
		n_tier_classes, get_min_attrs, get_attrs):

		''' 
			This function creates and sets the attributes_dict of all 
			desired tier_classes based on user input
			Args: 
				n_tier_classes: the number of tier classes you want to make
				get_min_attrs: a function that returns an attribute dict
					consisting of an attributes dict such as returned by
					create_min_attributes_dict(), but with name and
					hierarchy level filled in.
				get_attrs: a function which returns whether to continue
					getting class attributes and a desired class attribute
		'''

		tier_tree = []	

		# Loop through and create attributes for all desired tier_classes
		# and then use the constructed tier_class to append and create
		# tier tree
		for n_tier_class in range(n_tier_classes):
			# input minimum attributes as defined by 
			# self.create_minimum_attributes_dict
			# Gets minimum attributes such as hierarchy_level and name of 
			# the tier class to be set

			#attributes_dict = self.input_min_attributes()
			attributes_dict = get_min_attrs()
			name = attributes_dict["name"]
			# a list of all the names of the class attribute names added here
			attributes = []

			keep_inputting = True
			while keep_inputting:
				# Input whatever function will return a desired 
				# class_attribute for a given name of a tier_class
				# Must also return whether inputting should continue
				#NOTE: this is a major difference between this func and airtable
				# version of the func because this one has the user input
				# the field names here whereas the airtable tier_tree
				# relies on fields being set in airtable already
				keep_inputting, class_attribute = get_attrs(name)
				if keep_inputting == False:
					break

				# If it is a valid class attribute, store it in attr_dict
				else:

					#NOTE Hopefully they don't enter hierarchy_level,
					# or name because that overwrites previously setup
					# name and hierarchy_level attributes to None

					# Stores the unset class_attribute 
					# in the dict of class attrs as a temporary None type
					attributes_dict[class_attribute] = None
					attributes.append(class_attribute)

			# Sets fields class attribute with names of all added class attrs
			attributes_dict["fields"] = attributes

			# Creates a Tier_Class with the filled out attributes_dict
			# and then adds it to the tier_tree
			tier_tree = self.construct_tier_tree(
				tier_tree, attributes_dict)
		# Setup the class attribute for this instance's custom tier_tree
		#set_tier_tree_attribute(tier_tree)
		return tier_tree

	def get_airtable_tier_tree(self):
		'''
		Returns a tier_tree object based on the fields setup in Airtable.
		Use Ruminant Template to see an example.
		'''

		tier_tree = []
		# For each table create a different attributes dict with different
		# names and hierarchy level
		for hierarchy_level, tables in self.ar.all_tables.items():
			for (table_name, airtable) in tables:
				self.log.info("table_name: {}, airtable: {} \n".format(
					table_name, airtable))

				# set tier_tree attr_dict with name and h_level for each 
				# table
				attr_dict = self.create_minimum_attributes_dict(
					table_name, hierarchy_level)

				#XXX add each field from airtable to a class attribute keeping
				# track of all column / field names and accepted type

				# set all the tier_tree class attributes based on table fields
				fields = self.ar.all_tables_field_names
				table_fields = fields[table_name]
				attr_dict["fields"] = table_fields
				#for field_name in table_fields:
					#attr_dict[field_name] = None
				# create and store tier_trees based on the fields
				tier_tree = self.construct_tier_tree(tier_tree, attr_dict)
		return tier_tree

		
	def construct_tier_tree(self, tier_tree, attributes_dict):
		'''
		Args:
			tier_tree: could be an empty list or an existing tier_tree
			attributes_dict: dictionary with desired class attributes and a 
				default value.
				Ex: {'Desc' : 'Default description', 'Time created' : None}

			This function constructs / appends to a given tier_tree using
			an attributes_dict and its hierarchy level to appropriately
			assign it to a hierarchy_dict within tier_tree.
			tier_tree Ex: [{0 : [<Main class object>]}, 
				{1 : [<Tasks class object>]}]
		'''
		
		# Create a tier_class with the newly created attributes_dict
		# for each desired tier_class
		Tier_Class = self.create_tier_class(attributes_dict)

		# Create tier_tree, [{0 : [tier_classes]}]
		h_level = Tier_Class.hierarchy_level

		# Check if the tier_tree hierarchy_dict of a given h_level
		# already exists; append to it if it does, replace / add if not
		h_dict_index = self.find_existing_hierarchy_dict(
			tier_tree, h_level)
		if h_dict_index != None:
			# by getting the existing h_dict's index within the tier tree
			# we don't rely on ordered addition of tier_trees
			tier_tree[h_dict_index][h_level].append(Tier_Class)
		else:		
			# Create hierarchy_level dict
			hierarchy_dict = {}
			# for example [{0: []}]
			h_dict_inner_list = [Tier_Class]
			hierarchy_dict[h_level] = h_dict_inner_list
			# Append to tier_tree
			tier_tree.append(hierarchy_dict)
		return tier_tree

	def find_existing_hierarchy_dict(self, tier_tree, h_level):
		'''
			Checks if a hierarchy_dict with a key corresponding to a give
			hierarchy level is already present in tier_tree.
			Returns the index of the h_dict if it is present in the tree
		'''
		h_dict_index = None
		for i, h_dict in enumerate(tier_tree):
			#NOTE that there is one h_dict per hierarchy_level and its value
			# is a list of corresponding tier classes of that h_level
			if h_level in h_dict:
				h_dict_index = i

		return h_dict_index

	#def set_tier_tree_attribute(self, tier_tree):
		#custom_tier_tree = tier_tree










