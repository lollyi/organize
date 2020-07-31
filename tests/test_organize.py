# vim: set sw=4 noet ts=4 fileencoding=utf-8:

import unittest
import logging
import sys
sys.path.append('../lib')
import organize

def setup_logger(logger_level):
	''' Args: logger supports levels DEBUG, INFO, WARNING, ERROR, CRITICAL.
	logger_level should be passed in in the format logging.LEVEL '''

	logging.basicConfig(level=logger_level)
	logger = logging.getLogger(__name__)
	return logger

class Test_Organize(unittest.TestCase):

	def setUp(self):
		self.log = setup_logger(logging.DEBUG)	
		self.class_constructor = organize.class_constructor
		self.fake_attributes_dict1 = {
			"__init__" : self.class_constructor,
			"name" : "Fake_Tier1",
			"hierarchy_level" : 0,
		}
		self.Fake_Class1 = type(
			"Fake_Tier1", (object,), self.fake_attributes_dict1)
		self.fake_attributes_dict2 = {
			"__init__" : self.class_constructor,
			"name" : "Lower_Fake_Tier2",
			"hierarchy_level" : 1,
		}
		self.Fake_Class2 = type(
			"Fake_Tier2", (object,), self.fake_attributes_dict2)
		self.fake_attributes_dicts_list = [
			self.fake_attributes_dict1, self.fake_attributes_dict2
		]
		self.n_tier_classes = 2

#	def test_create_tier_class_90(self):
#		self.log.debug("\n TEST 90 \n")
#		New_Tier_Class = organize.create_tier_class(fake_attributes_dict1)
		
	#XXX may want to later make a class to encompass setup funcs and then this
	# will need to be fixed
	def test_setup_tier_tree_100(self):
		self.log.debug("\n TEST 100 \n")
		# Need a way to simulate input of create_tier_class()
		tier_tree = organize.setup_tier_tree(
			self.n_tier_classes,
			self.fake_attributes_dicts_list
		)
		fake_tier_tree = [
			{0: [self.Fake_Class1]}, {1: [self.Fake_Class2]}
		]
		self.log.debug("tier_tree: {}".format(tier_tree))
		self.log.debug("fake_tier_tree: {}".format(fake_tier_tree))
		#XXX need to test that tree_tier's classes have the same attributes
		# and structure, but since they are constructed in different places
		# this assert fails to do so.
		assert(len(tier_tree) == len(fake_tier_tree))
		assert(tier_tree == fake_tier_tree)

	def tearDown(self):
		pass




if __name__ == "__main__":
	unittest.main()

