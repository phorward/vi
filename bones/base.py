# -*- coding: utf-8 -*-
from vi import html5
from vi.framework.components.button import Button
from vi.priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from vi.config import conf


class BaseBoneExtractor(object):
	"""
		Base "Catch-All" extractor for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs):
		super().__init__()
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

extractorDelegateSelector.insert(0, lambda *args, **kwargs: True, BaseBoneExtractor)


class BaseViewBoneDelegate( object ):
	"""
		Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure, *args, **kwargs ):
		super().__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.moduleName=moduleName

	def render(self, data, field):
		value = conf["emptyValue"]

		if field in data.keys():
			value = str(data[field])

		delegato = html5.Div(value)
		delegato.addClass("vi-delegato", "vi-delegato--base")
		return delegato

viewDelegateSelector.insert(0, lambda *args, **kwargs: True, BaseViewBoneDelegate)

# --- Single -----------------------------------------------------------------------------------------------------------

class BaseEditBone(html5.Input):
	"""
		Base edit widget.
	"""
	def __init__(self, moduleName, boneName, boneStructure, *args, **kwargs):
		super().__init__()

		self.moduleName = moduleName
		self.boneName = boneName
		self.boneStructure = boneStructure

		self.update()

	def _setValue(self, value):
		super()._setValue(value or "")

	def unserialize(self, data, errorInfo=None):
		self["value"] = data.get(self.boneName)

	def serializeForPost(self, prefix=""):
		return {
			(prefix or self.boneName): self["value"]
		}

	def serializeForDocument(self):
		return {
			self.boneName: self["value"]
		}

	def setError(self, error):
		pass

	def update(self):
		if self.boneStructure.get("readOnly", False):
			self.disable()

	@staticmethod
	def checkFor(_moduleName, _boneName, _boneStructure):
		return True

# Register this Bone in the global queue as generic fallback.
editBoneSelector.insert(0, BaseEditBone.checkFor, BaseEditBone)


# --- Multiple ---------------------------------------------------------------------------------------------------------

class BaseMultiEditBoneEntry(html5.Div):
	template = """
	<button [name]="removeBtn" class="btn-delete" text="Delete" icon="icons-delete"></button>
	"""

	def __init__(self, widget):
		super().__init__(self.template)
		self.widget = widget
		self.attachWidget()

	def _getValue(self):
		return self.widget["value"]

	def _setValue(self, value):
		self.widget["value"] = value

	def unserialize(self, data, errorInfo=None):
		self.widget.unserialize(data, errorInfo=errorInfo)

	def serializeForPost(self, prefix=""):
		return self.widget.serializeForPost(prefix=prefix)

	def serializeForDocument(self):
		return self.widget.serializeForDocument()

	def attachWidget(self):
		self.prependChild(self.widget)

	def onRemoveBtnClick(self):
		self.parent().removeChild(self)

	def focus(self):
		self.widget.focus()

class BaseMultiEditBone(html5.Div):
	entryBoneConstructor = BaseEditBone
	entryConstructor = BaseMultiEditBoneEntry
	style = []
	template = """
		<div [name]="widgets" class="vi-bone-widgets"></div>
		<div [name]="actions" class="vi-bone-actions">
			<button [name]="addBtn" class="btn-add" text="Add" icon="icons-add"></button>
		</div>
	"""

	def __init__(self, moduleName, boneName, boneStructure):
		super().__init__(self.template)
		self.addClass(self.style)

		self.moduleName = moduleName
		self.boneName = boneName
		self.boneStructure = boneStructure

	def onAddBtnClick(self):
		last = self.widgets.children(-1)
		if last and not last["value"]:
			last.focus()
			return

		entry = self.addEntry()
		entry.focus()

	def addEntry(self, value=None):
		entry = self.entryConstructor(self.entryBoneConstructor(self.moduleName, self.boneName, self.boneStructure))

		if value:
			entry["value"] = value

		self.widgets.appendChild(entry)
		return entry

	def _setValue(self, value):
		self.widgets.removeAllChildren()

		if not isinstance(value, list):
			return

		for entry in value:
			self.addEntry(entry)

	def _getValue(self):
		ret = []

		for entry in self.widgets.children():
			value = entry["value"]
			if not value:
				continue

			ret.append(value)

		return ret

	def unserialize(self, data, errorInfo=None):
		self["value"] = data.get(self.boneName)

	def serializeForDocument(self):
		return {
			self.boneName: self["value"]
		}

	def serializeForPost(self, prefix=""):
		retDict = {}
		retList = []
		cnt = 0

		for widget in self.widgets.children():
			value = widget["value"]
			if not value:
				continue

			if isinstance(value, dict):
				retDict.update(
					widget.serializeForPost(
						prefix=(prefix or self.boneName) + ".%d" % cnt
					)
				)
			else:
				retList.append(value)

			cnt += 1

		assert not(retDict and retList), \
			"Something inside the bone implementation of %s is wrong" % self.entryBoneConstructor.__class__.__name__

		if retList:
			return {
				(prefix or self.boneName): retList
			}

		return retDict

	@staticmethod
	def checkFor(_moduleName, boneName, boneStructure):
		return boneStructure[boneName].get("multiple")

# Register this Bone in the global queue as generic fallback.
editBoneSelector.insert(1, BaseMultiEditBone.checkFor, BaseMultiEditBone)


# --- Language ---------------------------------------------------------------------------------------------------------

class BaseLangEditBone(html5.Div):
	entryBoneConstructor = BaseEditBone
	style = []
	template = """
		<div [name]="widgets" class="vi-bone-widgets"></div>
		<div [name]="actions" class="vi-bone-actions"></div>
	"""

	def __init__(self, moduleName, boneName, boneStructure):
		super().__init__(self.template)
		self.addClass(self.style)

		self.moduleName = moduleName
		self.boneName = boneName
		self.boneStructure = boneStructure

		self.btn4Lang = {}

		for lang in self.boneStructure[boneName]["languages"]:
			langBtn = Button(lang, callback=self.onLangBtnClick)
			langBtn.lang = lang
			langBtn.addClass("btn--lang")

			self.btn4Lang[lang] = langBtn

			if lang == conf["defaultLanguage"]:
				langBtn.addClass("is-active")

			self.actions.appendChild(langBtn)

			langWidget = self.entryBoneConstructor(moduleName, boneName, boneStructure)
			langWidget.lang = lang

			if lang != conf["defaultLanguage"]:
				langWidget.hide()

			self.widgets.appendChild(langWidget)

	def onLangBtnClick(self, sender):
		for widget in self.widgets.children():
			if widget.lang == sender.lang:
				widget.show()
				self.btn4Lang[widget.lang].addClass("is-active")
			else:
				widget.hide()
				self.btn4Lang[widget.lang].removeClass("is-active")

	def _getValue(self):
		return {
			widget.lang: widget["value"] for widget in self.widgets.children()
		}

	def _setValue(self, value):
		if not isinstance(value, dict):
			return

		for widget in self.widgets.children():
			widget["value"] = value.get(widget.lang)

	def unserialize(self, data):
		self["value"] = data.get(self.boneName)

	def serializeForPost(self, prefix=""):
		ret = {}

		for lang in self.widgets.children():
			ret.update(
				lang.serializeForPost(prefix=(prefix or self.boneName) + "." + lang.lang)
			)

		return ret

	def serializeForDocument(self):
		return {
			self.boneName: self["value"]
		}

	@staticmethod
	def checkFor(_moduleName, boneName, boneStructure):
		return not boneStructure[boneName].get("multiple") and isinstance(boneStructure[boneName].get("languages"), list)

# Register this Bone in the global queue as generic fallback.
editBoneSelector.insert(2, BaseLangEditBone.checkFor, BaseLangEditBone)

# --- Multi+Language ---------------------------------------------------------------------------------------------------

class BaseMultiLangEditBone(BaseLangEditBone):
	entryBoneConstructor = BaseMultiEditBone

	@staticmethod
	def checkFor(_moduleName, boneName, boneStructure):
		return boneStructure[boneName].get("multiple") and isinstance(boneStructure[boneName].get("languages"), list)

# Register this Bone in the global queue as generic fallback.
editBoneSelector.insert(2, BaseMultiLangEditBone.checkFor, BaseMultiLangEditBone)
