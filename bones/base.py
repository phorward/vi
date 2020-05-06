# -*- coding: utf-8 -*-
from vi import html5
from vi.framework.components.button import Button
from vi.priorityqueue import boneSelector
from vi.config import conf


class BaseBone(html5.Div):
	template = """<ignite-input [name]="widget">"""
	style = ["vi-bone"]

	def __init__(self, moduleName: str, boneName: str, skelStructure: dict, data: dict=None, *args, **kwargs):
		super().__init__(
			self.template,
			style=self.style
		)

		self.moduleName = moduleName
		self.boneName = boneName
		self.skelStructure = skelStructure

		if "widget" not in dir(self):
			self.widget = None

		self.value = None

		if data:
			self.unserialize(data)

		self.update()

	def focus(self):
		"""
		Focus the widget.
		"""
		if self.widget:
			self.widget.focus()
		else:
			super().focus()

	def _setValue(self, value: str):
		"""
		Implements lvalue call for widget["value"]
		"""
		if self.widget:
			self.widget["value"] = value

		self.value = value

	def _getValue(self) -> str:
		"""
		Implements rvalue call for widget["value"]
		"""
		if self.widget:
			return self.widget["value"]

		return self.value

	def unserialize(self, data: dict, errorInfo=None):
		"""
		Unserialize the value from a list-dict-serialized structure.
		"""
		self["value"] = data.get(self.boneName)

	def serializeForPost(self, prefix=""):
		"""
		Serialize the bone's value to be sent to the server via POST.
		"""
		return {
			(prefix or self.boneName): self["value"]
		}

	def serializeForDocument(self):
		"""
		Serialize the bone's value in a list-dict-serialized style.
		"""
		return {
			self.boneName: self["value"]
		}

	def setError(self, error):
		#todo
		pass

	def update(self):
		#todo
		if self.skelStructure.get("readOnly", False):
			self.disable()

	@classmethod
	def editBone(cls, moduleName: str, boneName: str, skelStructure: dict, data=None) -> html5.Widget:
		"""
		Creates a Widget that is used to edit the bone.
		"""
		return cls(moduleName, boneName, skelStructure, data=data)

	@classmethod
	def getEditBoneFactory(cls, moduleName: str, boneName: str, skelStructure: dict) -> callable:
		"""
		Generates a factory for editBones with the equal base configuration.
		"""
		return lambda data=None: cls(moduleName, boneName, skelStructure, data=data)

	@classmethod
	def viewBone(cls, moduleName: str, boneName: str, skelStructure: dict, data=None) -> html5.Widget:
		"""
		Creates a Widget that is used to display the bone extracted from data.
		"""
		return html5.Span(html5.TextNode((data.get(boneName) if data else None) or conf["emptyValue"]))

	@classmethod
	def getViewBoneFactory(cls, moduleName: str, boneName: str, skelStructure: dict) -> callable:
		"""
		Generates a factory for viewBones with equal base configuration.
		Returns a function to be called with data where the bone will be extracted from.
		"""
		return lambda data=None: cls.viewBone(moduleName, boneName, skelStructure, data)

	@classmethod
	def checkFor(cls, moduleName: str, boneName: str, skelStructure: str) -> bool:
		"""
		Check function for the plugin handling.
		"""
		return True


boneSelector.insert(0, BaseBone.checkFor, BaseBone)


class BaseMultiBoneEntry(html5.Div):
	template = """
	<button [name]="removeBtn" class="btn--delete" text="Delete" icon="icons-delete"></button>
	"""

	def __init__(self, widget: BaseBone):
		super().__init__(self.template)
		self.widget = widget
		self.attachWidget()

		# Proxy some functions of the original widget
		for fct in ["_getValue", "_setValue", "unserialize", "serializeForPost", "serializeForDocument", "focus"]:
			setattr(self, fct, getattr(self.widget, fct))

	def attachWidget(self):
		self.prependChild(self.widget)

	def onRemoveBtnClick(self):
		self.parent().removeChild(self)

	def focus(self):
		self.widget.focus()

class BaseMultiBone(BaseBone):
	boneFactory = BaseBone  # Defines the constructor of the bone used for each entry
	rowConstructor = BaseMultiBoneEntry  # Defines the constructor of the entry bone wrapper used for each entry
	template = """
		<div [name]="widgets" class="vi-bone-widgets"></div>
		<div [name]="actions" class="vi-bone-actions">
			<button [name]="addBtn" class="btn--add" text="Add" icon="icons-add"></button>
		</div>
	"""

	def onAddBtnClick(self):
		last = self.widgets.children(-1)
		if last and not last["value"]:
			last.focus()
			return

		entry = self.addEntry()
		entry.focus()

	def addEntry(self, value=None):
		entry = self.boneFactory(self.moduleName, self.boneName, self.skelStructure)
		if self.rowConstructor:
			entry = self.rowConstructor(entry)

		if value:
			entry["value"] = value

		self.widgets.appendChild(entry)
		return entry

	def _setValue(self, value: list):
		self.widgets.removeAllChildren()

		if not isinstance(value, list):
			return

		for entry in value:
			self.addEntry(entry)

	def _getValue(self) -> list:
		ret = []

		for entry in self.widgets.children():
			value = entry["value"]
			if not value:
				continue

			ret.append(value)

		return ret

	def serializeForPost(self, prefix="") -> dict:
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
			"Something inside the bone implementation of %r is wrong" % self.boneFactory.__class__.__name__

		if retList:
			return {
				(prefix or self.boneName): retList
			}

		return retDict

	@classmethod
	def checkFor(cls, moduleName: str, boneName: str, skelStructure: dict) -> bool:
		return skelStructure[boneName].get("multiple")

	@classmethod
	def viewBone(cls, moduleName: str, boneName: str, skelStructure: dict, data=None) -> html5.Widget:
		values = (data.get(boneName) if data else None) or []

		ul = html5.Ul(style=["vi-bone-view-multiple-wrapper"])
		for value in values:
			# this is done temporarily only, to suggest the bone it is "alone" in the data...
			data.update({boneName: value})

			ul.appendChild(
				html5.Li(cls.boneFactory.viewBone(moduleName, boneName, skelStructure, data))
			)

		# here we reset the data dict to the original values
		data.update({boneName: values})

		return ul


# Register this Bone in the global queue as generic fallback.
boneSelector.insert(1, BaseMultiBone.checkFor, BaseMultiBone)


class BaseLangBone(BaseBone):
	boneFactory = BaseBone  # Defines the factory for the bone used for each language
	template = """
		<div [name]="widgets" class="vi-bone-widgets"></div>
		<div [name]="actions" class="vi-bone-actions"></div>
	"""

	def __init__(self, moduleName: str, boneName: str, skelStructure: dict, data=None):
		super().__init__(moduleName, boneName, skelStructure, data=data)

		self.btn4Lang = {}
		for lang in self.skelStructure[self.boneName]["languages"]:
			langBtn = Button(lang, callback=self.onLangBtnClick)
			langBtn.lang = lang
			langBtn.addClass("btn--lang")

			self.btn4Lang[lang] = langBtn

			if lang == conf["defaultLanguage"]:
				langBtn.addClass("is-active")

			self.actions.appendChild(langBtn)

			langWidget = self.boneFactory(self.moduleName, self.boneName, self.skelStructure)
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

	def _getValue(self) -> dict:
		return {
			widget.lang: widget["value"] for widget in self.widgets.children()
		}

	def _setValue(self, value: dict):
		if not isinstance(value, dict):
			return

		for widget in self.widgets.children():
			widget["value"] = value.get(widget.lang)

	def serializeForPost(self, prefix="") -> dict:
		ret = {}

		for lang in self.widgets.children():
			ret.update(
				lang.serializeForPost(prefix=(prefix or self.boneName) + "." + lang.lang)
			)

		return ret

	@classmethod
	def checkFor(cls, moduleName: str, boneName: str, skelStructure: dict) -> bool:
		return not skelStructure[boneName].get("multiple") and isinstance(skelStructure[boneName].get("languages"), list)

	@classmethod
	def viewBone(cls, moduleName, boneName, skelStructure, data=None):
		values = (data.get(boneName) if data else None) or []

		ul = html5.Ul(style="vi-bone-view-language")
		for lang in skelStructure[boneName]["languages"]:
			value = values.get(lang)

			# this is done temporarily only, to suggest the bone it is "alone" in the data...
			data.update({boneName: value})

			ul.appendChild(
				html5.Li(
					html5.Span(lang),
					cls.boneFactory.viewBone(moduleName, boneName, skelStructure, data),
					style=["vi-bone-view-language-wrapper", "vi-bone-view-language-wrapper-%s" % lang]
				)
			)

		# here we reset the data dict to the original values
		data.update({boneName: values})
		return ul


# Register this Bone in the global queue as generic fallback.
boneSelector.insert(2, BaseLangBone.checkFor, BaseLangBone)


class BaseMultiLangBone(BaseLangBone):
	boneFactory = BaseMultiBone

	@classmethod
	def checkFor(cls, moduleName, boneName, skelStructure):
		return skelStructure[boneName].get("multiple") and isinstance(skelStructure[boneName].get("languages"), list)


# Register this Bone in the global queue as generic fallback.
boneSelector.insert(2, BaseMultiLangBone.checkFor, BaseMultiLangBone)
