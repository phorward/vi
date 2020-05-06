# -*- coding: utf-8 -*-
from vi import html5
from vi.bones.base import BaseBone, BaseLangBone
from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.i18n import translate


class BooleanBone(BaseBone):
	template = """<ignite-switch [name]="widget" />"""
	style = ["vi-bone-container"]

	def _setValue(self, value):
		self.widget["checked"] = value

	def _getValue(self):
		return self.widget["checked"]

	@classmethod
	def viewBone(cls, moduleName: str, boneName: str, skelStructure: dict, data=None) -> html5.Widget:
		return html5.Span(html5.TextNode((translate(str(data.get(boneName))) if data else None) or conf["emptyValue"]))

	@classmethod
	def checkFor(cls, moduleName: str, boneName: str, skelStructure: str) -> bool:
		return skelStructure[boneName]["type"] == "bool" or skelStructure[boneName]["type"].startswith("bool")

boneSelector.insert(3, BooleanBone.checkFor, BooleanBone)


class BooleanLangBone(BaseLangBone):
	boneFactory = BooleanBone

	@classmethod
	def checkFor(cls, moduleName: str, boneName: str, skelStructure: str) -> bool:
		return ((skelStructure[boneName]["type"] == "bool" or skelStructure[boneName]["type"].startswith("bool"))
				and super().checkFor(moduleName, boneName, skelStructure))

# Register this Bone in the global queue as generic fallback.
boneSelector.insert(4, BooleanLangBone.checkFor, BooleanLangBone)


'''
class ExtendedBooleanSearch( html5.Div ):
	def __init__(self, extension, view, module, *args, **kwargs ):
		super( ExtendedBooleanSearch, self ).__init__( *args, **kwargs )
		self.view = view
		self.extension = extension
		self.module = module
		self.filterChangedEvent = EventDispatcher("filterChanged")
		self.appendChild(html5.TextNode(extension["name"]))
		self.selectionCb = html5.Select()
		self.appendChild(self.selectionCb)
		o = html5.Option()
		o["value"] = ""
		o.appendChild(html5.TextNode(translate("Ignore")))
		self.selectionCb.appendChild(o)
		o = html5.Option()
		o["value"] = "0"
		o.appendChild(html5.TextNode(translate("No")))
		self.selectionCb.appendChild(o)
		o = html5.Option()
		o["value"] = "1"
		o.appendChild(html5.TextNode(translate("Yes")))
		self.selectionCb.appendChild(o)
		self.sinkEvent("onChange")

	def onChange(self, event):
		event.stopPropagation()
		self.filterChangedEvent.fire()

	def updateFilter(self, filter):
		val = self.selectionCb["options"].item(self.selectionCb["selectedIndex"]).value
		if not val:
			if self.extension["target"] in filter.keys():
				del filter[self.extension["target"]]
		else:
			filter[self.extension["target"]] = val
		return (filter)

	@staticmethod
	def canHandleExtension( extension, view, module ):
		return( isinstance( extension, dict) and "type" in extension.keys() and (extension["type"]=="boolean" or extension["type"].startswith("boolean.") ) )


extendedSearchWidgetSelector.insert(1, ExtendedBooleanSearch.canHandleExtension, ExtendedBooleanSearch)
'''
