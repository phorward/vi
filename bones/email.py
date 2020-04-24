# -*- coding: utf-8 -*-
import re

from vi import html5

from vi.priorityqueue import editBoneSelector, viewBoneSelector
from vi.exception import InvalidBoneValueException

import vi.bones.string as strBone


class EmailViewBoneDelegate( strBone.StringViewBoneDelegate ):
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super( EmailViewBoneDelegate, self ).__init__( moduleName, boneName, skelStructure, *args, **kwargs)

	def getViewElement(self,labelstr,datafield):

		# check if rendering of EmailBones is wanted as String
		if ("params" in self.skelStructure[self.boneName].keys()
			and isinstance(self.skelStructure[self.boneName]["params"], dict)
			and self.skelStructure[self.boneName]["params"].get("renderAsString")):
			return super(EmailViewBoneDelegate, self).getViewElement(labelstr, datafield)

		delegato = html5.Div(labelstr)
		delegato.addClass("vi-delegato", "vi-delegato--mail")

		return delegato

class EmailEditBone( strBone.StringEditBone ):
	def __init__(self, moduleName, boneName,readOnly,*args, **kwargs ):
		super( EmailEditBone,  self ).__init__( moduleName, boneName,readOnly, *args, **kwargs )

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return EmailEditBone(moduleName, boneName, readOnly)

	def unserialize(self, data):
		if self.boneName in data.keys():
			self.input["value"] = data[ self.boneName ] if data[ self.boneName ] else ""

	def serializeForPost(self):
		if not self["value"] or re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._-]+.[a-zA-Z]{2,6}$",self.input["value"]):
			return( { self.boneName: self.input["value"] } )
		raise InvalidBoneValueException()

	def setSpecialType(self):
		self.input["type"]="email"

	def setExtendedErrorInformation(self, errorInfo ):
		pass


def CheckForEmailBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="str.email" )

#Register this Bone in the global queue
editBoneSelector.insert( 4, CheckForEmailBone, EmailEditBone)
viewBoneSelector.insert( 4, CheckForEmailBone, EmailViewBoneDelegate)
