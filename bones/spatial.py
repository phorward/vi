# -*- coding: utf-8 -*-
from vi import html5

from vi.i18n import translate
from vi.priorityqueue import boneSelector


class SpatialBone(html5.Div):
	def __init__(self, moduleName, boneName, readOnly, *args, **kwargs):
		super(SpatialBone, self).__init__(*args, **kwargs)
		moduleName = moduleName or "embed"

		self.boneName = boneName
		self.readOnly = readOnly
		self.latitude = html5.Input()
		self.longitude = html5.Input()
		self.latitude["type"] = "number"
		self.longitude["type"] = "number"
		self.appendChild(self.latitude)
		lbl = html5.Label(translate("longitude"))
		lbl["for"] == moduleName + "_" + boneName + "_longitude"
		self.appendChild(lbl)
		self.longitude["name"] = moduleName + "_" + boneName + "_longitude"
		self.appendChild(self.longitude)
		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure(moduleName, boneName, skelStructure, *args, **kwargs):
		readOnly = "readonly" in skelStructure[boneName].keys() and skelStructure[boneName]["readonly"]
		return SpatialBone(moduleName, boneName, readOnly)

	def unserialize(self, data):
		if self.boneName not in data:
			return

		try:
			self.latitude["value"], self.longitude["value"] = data[self.boneName]
		except KeyError:
			pass
		except TypeError:
			pass

	def serializeForPost(self):
		return {
			"{0}.lat".format(self.boneName): self.latitude["value"],
			"{0}.lng".format(self.boneName): self.longitude["value"]
		}

	def serializeForDocument(self):
		return self.serializeForPost()

	def setExtendedErrorInformation(self, errorInfo):
		pass


def CheckForSpatialBone(moduleName, boneName, skelStucture, *args, **kwargs):
	return skelStucture[boneName]["type"] == "spatial" or skelStucture[boneName]["type"].startswith("spatial.")


# Register this Bone in the global queue
boneSelector.insert(5, CheckForSpatialBone, SpatialBone)
