#-*- coding: utf-8 -*-
import html5
from config import conf
from i18n import translate
from priorityqueue import HandlerClassSelector
from network import DeferredCall

class Pane(html5.Li):
	"""
		Base class for Panes.

		A pane represents a entry in the left menu as well
		as a list of widgets associated with this pane.

		It is possible to stack panes on-top of each other.
		If a pane is active, _all_ its child widgets are visible
		(through they might overlap).
	"""
	def __init__(self, descr=None, iconURL=None, iconClasses=None,
				 	closeable=False, collapseable=True, focusable=True,
				 		path=None):
		super(Pane, self).__init__()

		self.parentPane = None
		self.sinkEvent("onClick")
		self.groupPrefix = None

		self.descr = descr
		self.iconURL = iconURL
		self.iconClasses = iconClasses
		self.collapseable = collapseable
		self.focusable = focusable
		self.path = path

		self.childPanes = []

		self.widgetsDomElm = html5.Div()
		self.widgetsDomElm["class"].append("has_no_child")
		self.childDomElem = None

		self.img = None
		self.label = html5.A()
		self.label["class"].append("button")
		self.appendChild(self.label)

		self.closeBtn = html5.ext.Button(translate("Close"), self.onBtnCloseReleased)
		self.closeBtn.addClass("closebtn")
		self.appendChild(self.closeBtn)

		if not closeable:
			self.closeBtn.hide()

		self.closeable = closeable
		self.isExpanded = False
		self.defaultImgSrc = self.iconURL

		DeferredCall(self.setText, _delay=250)

	def __setattr__(self, key, value):
		super(Pane, self).__setattr__(key, value)
		if key == "closeable":
			if value:
				self.closeBtn.show()
			else:
				self.closeBtn.hide()

	def lock(self):
		self.disable()

		if self.img:
			self.defaultImgSrc = self.img["src"]
			self.img["src"] = "icons/is_loading32.gif"

	def unlock(self):
		if self.img and self.defaultImgSrc:
			self.img["src"] = self.defaultImgSrc

		self.enable()

	def setText(self, descr = None, iconURL = None):
		self.label.removeAllChildren()

		if iconURL is None:
			iconURL = self.iconURL

		if iconURL is not None:
			self.img = html5.Img()
			self.img["src"] = iconURL
			self.label.appendChild(self.img)

		if self.iconClasses is not None:
			for cls in self.iconClasses:
				self.label.addClass(cls)

		if descr is None:
			descr = self.descr

		if descr is not None:
			h = html5.H3()
			h.appendChild(descr)
			self.label.appendChild(h)

	def onBtnCloseReleased(self, *args, **kwargs):
		conf["mainWindow"].removePane(self)

	def addChildPane(self, pane):
		"""
			Stack a pane under this one.
			It gets displayed as a subpane.
			:param pane: Another pane
			:type pane: pane
		"""
		assert pane != self, "A pane cannot be a child of itself"

		self.childPanes.append(pane)
		pane.parentPane = self

		if not self.childDomElem:
			self.childDomElem = html5.Ul()

			if self.collapseable and not pane.closeable:
				self.childDomElem.hide()
			else:
				self.childDomElem.show()

			self.appendChild(self.childDomElem)

			if self.closeable:
				self.closeBtn.hide()

		if pane.closeable and self.childDomElem.isHidden():
			self.childDomElem.show()

		self.childDomElem.appendChild(pane)

	def removeChildPane(self, pane):
		"""
			Removes a subpane.
			:param pane: The pane to remove. Must be a direct child of this pane
			:type pane: Pane
		"""
		assert pane in self.childPanes, "Cannot remove unknown child-pane %s from %s" % (str(pane),str(self))

		self.childPanes.remove(pane)
		self.childDomElem.removeChild(pane)

		pane.parentPane = None

		#DOM.removeChild( self.childDomElem, pane.getElement() )
		if not len(self.childPanes): #No more children, remove the UL element
			self.removeChild(self.childDomElem)
			self.childDomElem = None

			if self.closeable:
				self.closeBtn.show()

	def onDetach(self):
		#assert len(self.childPanes)==0, "Attempt to detach a pane which still has subpanes!"
		#Kill all remaining children
		for widget in self.widgetsDomElm.children():
			self.widgetsDomElm.removeChild(widget)

		super(Pane, self).onDetach()

	def addWidget(self, widget):
		"""
			Adds a widget to this pane.
			Note: all widgets of a pane are visible at the same time!
			:param widget: The widget to add
			:type widget: Widget

		"""
		div = html5.Div()
		div["class"].append("vi_operator")
		div.appendChild(widget)

		for w in self.widgetsDomElm._children[:]:
			w["disabled"] = True

		self.widgetsDomElm.appendChild( div )
		self.rebuildChildrenClassInfo()

	def rebuildChildrenClassInfo(self):
		if "has_no_child" in self.widgetsDomElm["class"]:
			self.widgetsDomElm["class"].remove("has_no_child")
		if "has_single_child" in self.widgetsDomElm["class"]:
			self.widgetsDomElm["class"].remove("has_single_child")
		if "has_multiple_children" in self.widgetsDomElm["class"]:
			self.widgetsDomElm["class"].remove("has_multiple_children")
		if len(self.widgetsDomElm._children)==0:
			self.widgetsDomElm["class"].append("has_no_child")
		elif len(self.widgetsDomElm._children)==1:
			self.widgetsDomElm["class"].append("has_single_child")
		else:
			self.widgetsDomElm["class"].append("has_multiple_children")

	def removeWidget(self, widget):
		"""
			Removes a widget.
			:param widget: The widget to remove. Must be a direct child of this pane.
			:type widget: Widget
		"""
		for c in self.widgetsDomElm._children:
			if widget in c._children:
				self.widgetsDomElm.removeChild( c )

				if self.closeable and len(self.widgetsDomElm._children)==0:
					conf["mainWindow"].removePane( self )

				for w in self.widgetsDomElm._children[:]:
					w["disabled"] = False

				self.rebuildChildrenClassInfo()
				return

		raise ValueError("Cannot remove unknown widget %s" % str(widget))

	def containsWidget(self, widget ):
		"""
			Tests wherever widget is a direct child of this pane.
			:returns: bool
		"""
		for c in self.widgetsDomElm._children:
			if widget in c._children:
				return( True )
		return( False )

	def onClick(self, event = None, *args, **kwargs ):
		self.focus()

		if event:
			event.stopPropagation()

	def expand(self):
		if self.childDomElem and self.collapseable and not self.isExpanded:
			self.childDomElem["style"]["display"] = "initial"
			self.isExpanded = True

	def collapse(self):
		if self.childDomElem and self.collapseable and self.isExpanded:
			self.childDomElem["style"]["display"] = "none"
			self.isExpanded = False

	def focus(self):
		conf["mainWindow"].focusPane(self)

class GroupPane(Pane):
	"""
		This pane groups subpanes; it cannot have direct childrens
	"""

	def __init__(self, *args, **kwargs):
		super(GroupPane, self).__init__(*args, **kwargs)
		self.childDomElem = None

	def loadChildren(self):
		if self.groupPrefix in conf["vi.groupedModules"]:
			childs = conf["vi.groupedModules"][self.groupPrefix]
			childs.sort(key=lambda entry: "%d-%010d-%s" % (1 if entry[1].get("sortIndex") is None else 0, entry[1].get("sortIndex", 0), entry[1].get("name")))

			for module, info in childs:
				conf["modules"][module]["visibleName"] = conf["modules"][module]["name"].replace(self.groupPrefix, "")
				handlerCls = HandlerClassSelector.select(module, info)
				assert handlerCls is not None, "No handler available for module '%s'" % module
				handler = handlerCls(module, info)
				conf["mainWindow"].addPane(handler, self)

		self.unlock()

	def onClick(self, event = None, *args, **kwargs):
		if not self.childDomElem:
			self.childDomElem = html5.Ul()
			self.childDomElem["style"]["display"] = "none"
			self.appendChild(self.childDomElem)

		if not self.childPanes:
			self.lock()
			DeferredCall(self.loadChildren, _delay=100)

		if self.isExpanded:
			self.collapse()
		else:
			self.expand()

		if event:
			event.stopPropagation()

	def onFocus(self, event):
		if len(self.childPanes) > 0:
			conf["mainWindow"].focusPane(self.childPanes[0])
