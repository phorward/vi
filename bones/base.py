# -*- coding: utf-8 -*-
from vi import html5

from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from vi.config import conf

class BaseBoneExtractor(object):
	"""
		Base "Catch-All" extractor for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super(BaseBoneExtractor, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName = moduleName

	def render(self, data, field):
		if field in data.keys():
			return str(data[field])

		return conf["emptyValue"]

	def raw(self, data, field):
		if field in data.keys():
			if isinstance(data[field], list):
				return [str(x) for x in data[field]]

			return str(data[field])

		return None

class BaseViewBoneDelegate( object ):
	"""
		Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super(BaseViewBoneDelegate, self).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render(self, data, field):
		value = conf[ "emptyValue" ]

		if field in data.keys():
			value = str(data[field])

		delegato = html5.Div(value)
		delegato.addClass("vi-delegato", "vi-delegato--base")
		return delegato



class BaseEditBone(html5.ignite.Input):
	"""
		Base edit widget for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, readOnly, *args, **kwargs):
		super(BaseEditBone, self).__init__(*args, **kwargs)
		self.boneName = boneName
		self.readOnly = readOnly
		self.setParams()

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		return BaseEditBone(moduleName, boneName, skelStructure[boneName].get("readonly", False))

	def setParams(self):
		if self.readOnly:
			self["disabled"] = True

	def unserialize(self, data, extendedErrorInformation = None):
		if self.boneName in data.keys():
			self["value"] = data.get(self.boneName, "")

	def serializeForPost(self):
		return {
			self.boneName: self["value"]
		}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo):
		pass

# Register this Bone in the global queue as generic fallback.
editBoneSelector.insert(0, lambda *args, **kwargs: True, BaseEditBone)
viewDelegateSelector.insert(0, lambda *args, **kwargs: True, BaseViewBoneDelegate)
extractorDelegateSelector.insert(0, lambda *args, **kwargs: True, BaseBoneExtractor)
