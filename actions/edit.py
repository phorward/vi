# -*- coding: utf-8 -*-
from vi import html5

from vi.priorityqueue import actionDelegateSelector
from vi.i18n import translate
from vi.framework.components.button import Button
from vi.config import conf

class SaveContinue(Button):
	def __init__(self, *args, **kwargs):
		super( SaveContinue, self ).__init__( translate("Save-Continue"), icon="icons-save-file", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--save-continue"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return( actionName=="save.continue" )

	def onClick(self, sender=None):
		self[ "disabled" ] = True
		self["class"].append("is-loading")
		self["icon"] = "icons-loader"
		self.parent().parent().doSave(closeOnSuccess=False)

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self["class"].remove("is-loading")
			self[ "disabled" ] = False
			self.resetIcon()

actionDelegateSelector.insert( 1, SaveContinue.isSuitableFor, SaveContinue )

class SaveSingleton(Button):
	def __init__(self, *args, **kwargs):
		super(SaveSingleton, self).__init__(translate("Save"), icon="icons-save-file", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "save.singleton" and module != "_tasks"

	def onClick(self, sender=None):
		self[ "disabled" ] = True
		self["class"].append("is-loading")
		self["icon"] =  "icons-loader"
		self.parent().parent().doSave(closeOnSuccess=False)

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self["class"].remove("is-loading")
			self[ "disabled" ] = False
			self.resetIcon()

actionDelegateSelector.insert(1, SaveSingleton.isSuitableFor, SaveSingleton)

class ExecuteSingleton(Button):
	def __init__(self, *args, **kwargs):
		super(ExecuteSingleton, self).__init__(translate("Execute"), icon="icons-save-file", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "save.singleton" and module == "_tasks"

	def onClick(self, sender=None):
		self[ "disabled" ] = True
		self["class"].append("is-loading")
		self["icon"] =  "icons-loader"
		self.parent().parent().doSave(closeOnSuccess=True)

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self["class"].remove("is-loading")
			self[ "disabled" ] = False
			self.resetIcon()

actionDelegateSelector.insert(1, ExecuteSingleton.isSuitableFor, ExecuteSingleton)

class SaveClose(Button):
	def __init__(self, *args, **kwargs):
		super( SaveClose, self ).__init__( translate("Save-Close"), icon="icons-save-file", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return( actionName=="save.close" )

	def onClick(self, sender=None):
		self[ "disabled" ] = True
		self.addClass("is-loading")
		self["icon"] =  "icons-loader"
		self.parent().parent().doSave(closeOnSuccess=True)

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")
			self[ "disabled" ] = False
			self.resetIcon()

actionDelegateSelector.insert( 1, SaveClose.isSuitableFor, SaveClose )


class Refresh(Button):
	def __init__(self, *args, **kwargs):
		super(Refresh, self).__init__(translate("Reload"), icon="icons-reload", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--reload"

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "refresh"

	def onClick(self, sender=None):
		if self.parent().parent().modified:
			html5.ext.YesNoDialog(translate("vi.action.edit.refresh.question"),
		                            translate("vi.action.edit.refresh.title"),
		                            yesCallback=self.performReload)
		else:
			self.performReload()

	def performReload(self, sender=None):
		self.addClass("is-loading")
		self.parent().parent().reloadData()

	def resetLoadingState(self):
		self.removeClass("is-loading")


actionDelegateSelector.insert(1, Refresh.isSuitableFor, Refresh)

class CancelClose(Button):
	def __init__(self, *args, **kwargs):
		super( CancelClose, self ).__init__( translate("Cancel"), icon="icons-save-file", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--danger btn--cancel"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return( actionName=="cancel.close" )

	def onClick(self, sender=None):
		self.addClass("is-loading")
		self[ "disabled" ] = True
		currentPane = conf["mainWindow"].containsWidget(self.parent().parent())
		conf[ "mainWindow" ].removePane( currentPane )

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")
			self[ "disabled" ] = False


actionDelegateSelector.insert( 1, CancelClose.isSuitableFor, CancelClose )
