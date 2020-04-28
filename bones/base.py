# -*- coding: utf-8 -*-
from vi import html5
from vi.framework.components.button import Button
from vi.priorityqueue import boneSelector
from vi.config import conf

# --- Single -----------------------------------------------------------------------------------------------------------

class BaseBone(html5.Widget): # @AK: Wir erben von html5.Widget, weil wir damit den Typ des Tags verändern können (beim erben)
	_baseClass = "div"
	template = """<input [name]="widget">"""
	style = None    # @AK: Definiert styling-Klassen, die via addClass hinzugefügt werden

	def __init__(self, moduleName, boneName, boneStructure, data=None, *args, **kwargs):
		super().__init__(
			self.template,
			style=self.style
		)

		self.moduleName = moduleName
		self.boneName = boneName
		self.boneStructure = boneStructure

		if "widget" not in dir(self):
			self.widget = None

		self.value = None

		if data:
			self.unserialize(data)

		self.update()

	def focus(self):
		if self.widget:
			self.widget.focus()
		else:
			super().focus()

	def _setValue(self, value):
		# @AK: Unter widget["value"] wird hierbei der Raw-Wert abgelegt. BaseBone geht davon aus,
		#      dass der Wert entweder an ein "widget" weitergereicht wird, oder speichert den Wert selbst.
		if self.widget:
			self.widget["value"] = value
		else:
			self.value = value

	def _getValue(self):
		if self.widget:
			return self.widget["value"]

		return self.value

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
		#todo
		pass

	def update(self):
		#todo
		if self.boneStructure.get("readOnly", False):
			self.disable()

	@classmethod
	def editBone(cls, moduleName, boneName, boneStructure, data=None):
		"""
		Creates a Widget that is used to edit the bone.
		"""
		return cls(moduleName, boneName, boneStructure, data=data)

	@classmethod
	def getEditBoneFactory(cls, moduleName, boneName, boneStructure):
		"""
		Generates a factory for editBones with the equal base configuration.
		"""
		return lambda data=None: cls(moduleName, boneName, boneStructure, data=data)

	@classmethod
	def viewBone(cls, moduleName, boneName, boneStructure, data):
		"""
		Creates a Widget that is used to display the bone extracted from data.
		"""

		#@AK: Hatte hier erst überlegt sowas wie ein "viewTemplate" zu machen, aber wie soll man das dann ausdrücken
		#     bei Multiple? Macht keinen Sinn glaube ich.
		return html5.Span(html5.TextNode(data.get(boneName) or conf["emptyValue"]))

	@classmethod
	def getViewBoneFactory(cls, moduleName, boneName, boneStructure):
		"""
		Generates a factory for viewBones with equal base configuration.
		Returns a function to be called with data where the bone will be extracted from.
		"""
		return lambda data: cls.viewBone(moduleName, boneName, boneStructure, data)

	@classmethod
	def checkFor(cls, _moduleName, _boneName, _boneStructure):
		return True

boneSelector.insert(0, BaseBone.checkFor, BaseBone)

# --- Multiple ---------------------------------------------------------------------------------------------------------

class BaseMultiBoneEntry(html5.Widget): #@AK überlege noch diesen in BaseMultiBone einfließen zu lassen... was meinste?
										# der dient im Moment nur als Wrapper für einen Eintrag, reicht aber vieles durch.
	_baseClass = "div"
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

class BaseMultiBone(BaseBone):
	_baseClass = "div"
	boneFactory = BaseBone
	rowConstructor = BaseMultiBoneEntry
	style = None
	template = """
		<div [name]="widgets" class="vi-bone-widgets"></div>
		<div [name]="actions" class="vi-bone-actions">
			<button [name]="addBtn" class="btn-add" text="Add" icon="icons-add"></button>
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
		entry = self.boneFactory(self.moduleName, self.boneName, self.boneStructure)
		if self.rowConstructor:
			entry = self.rowConstructor(entry)

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
		#@AK: Diesen Affentanz müssen wir machen, weil der Core das parsing der Parameter beim fromClient() nicht so
		#     umsetzt wie ich es mal vorgeschlagen hatte, indem es immer bonename.0, bonename.1 etc. ist... nein hier
		#     ist es eine list, wenn es ein Wert je Sub-Widget ist und eine dict[key + "." + index] wenn es z.b. ein
		#     relationalBone ist... naja egal, mache hier nur meinen doofen job.
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
			"Something inside the bone implementation of %s is wrong" % self.boneFactory.__class__.__name__
			#@AK: Dieses assert wäre dann hinfällig (siehe oben)

		if retList:
			return {
				(prefix or self.boneName): retList
			}

		return retDict

	@classmethod
	def checkFor(cls, _moduleName, boneName, boneStructure):
		return boneStructure[boneName].get("multiple")

	@classmethod
	def viewBone(cls, moduleName, boneName, boneStructure, data=None):
		values = (data.get(boneName) if data else None) or []

		ul = html5.Ul()
		for value in values:
			ul.appendChild(
				html5.Li(cls.boneFactory.viewBone(moduleName, boneName, boneStructure, data={boneName: value}))
			)

		return ul

# Register this Bone in the global queue as generic fallback.
boneSelector.insert(1, BaseMultiBone.checkFor, BaseMultiBone)


# --- Language ---------------------------------------------------------------------------------------------------------

class BaseLangBone(BaseBone):
	_baseClass = "div"
	boneFactory = BaseBone
	style = None
	template = """
		<div [name]="widgets" class="vi-bone-widgets"></div>
		<div [name]="actions" class="vi-bone-actions"></div>
	"""

	def __init__(self, moduleName, boneName, boneStructure, data=None):
		super().__init__(moduleName, boneName, boneStructure, data=data)

		self.btn4Lang = {}
		for lang in self.boneStructure[self.boneName]["languages"]:
			langBtn = Button(lang, callback=self.onLangBtnClick)
			langBtn.lang = lang
			langBtn.addClass("btn--lang")

			self.btn4Lang[lang] = langBtn

			if lang == conf["defaultLanguage"]:
				langBtn.addClass("is-active")

			self.actions.appendChild(langBtn)

			langWidget = self.boneFactory(self.moduleName, self.boneName, self.boneStructure)
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

	def unserialize(self, data, errorInfo=None):
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

	@classmethod
	def checkFor(cls, _moduleName, boneName, boneStructure):
		return not boneStructure[boneName].get("multiple") and isinstance(boneStructure[boneName].get("languages"), list)

	@classmethod
	def viewBone(cls, moduleName, boneName, boneStructure, data=None):
		values = (data.get(boneName) if data else None) or []

		ul = html5.Ul()
		for lang in boneStructure[boneName]["languages"]:
			value = values.get(lang)
			ul.appendChild(
				html5.Li(
					html5.Span(lang),
					cls.boneFactory.viewBone(moduleName, boneName, boneStructure, data={boneName: value})
				)
			)

		return ul

# Register this Bone in the global queue as generic fallback.
boneSelector.insert(2, BaseLangBone.checkFor, BaseLangBone)

# --- Multi+Language ---------------------------------------------------------------------------------------------------

class BaseMultiLangBone(BaseLangBone):
	boneFactory = BaseMultiBone

	@classmethod
	def checkFor(cls, _moduleName, boneName, boneStructure):
		return boneStructure[boneName].get("multiple") and isinstance(boneStructure[boneName].get("languages"), list)

# Register this Bone in the global queue as generic fallback.
boneSelector.insert(2, BaseMultiLangBone.checkFor, BaseMultiLangBone)
