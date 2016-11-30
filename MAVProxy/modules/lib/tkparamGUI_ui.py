from MAVProxy.modules.lib import mp_util
from tkparamGUI_util import *
import tkinter as tk
import xml.etree.ElementTree

class ParamGUIFrame(tk.Frame):
    """ The main frame of the graphical parameter editor."""

    def __init__(self, state, mainwindow):
        self.state = state
        self.mainwindow = mainwindow

        tk.Frame.__init__(self, master=self.mainwindow)
    	self.grid(row=0, column=0, sticky="nsew")
    	self.grid_rowconfigure(0, weight=1)
    	self.grid_columnconfigure(0, weight=1)
    	self.pack(side="top", fill="both", expand=True)
        self.__build_gui()

    	self.last_height = -1

    	# Add data to tree
    	self.docs = {}
        xml_path = mp_util.dot_mavproxy("ArduPlane.xml")
    	e = xml.etree.ElementTree.parse(xml_path).getroot()
    	for param in e.iter('param'):
    	    name = param.attrib['name'].split(':')[-1].upper()
    	    self.docs[name] = param
    	    data = (name, param.attrib['humanName'])
            self.etv.insert('', "end", values=data)

    	# Sort and update tree
    	self.etv_items = self.etv.get_children('')
    	self.sort_desc = False   # ascending
    	self.__update()

        self.on_timer() # start timer

    def __build_gui(self):
    	from pygubu.widgets import tkscrollbarhelper, editabletreeview

    	self.mainwindow.config(height=200, width=200)
    	self.mainwindow.minsize(600, 186)   # 5 rows

    	# Frames
    	frame1 = self.__build_frame(self, sticky="nsew")
    	frame1.bind("<Configure>", self.on_window_resize)
    	frame2 = self.__build_frame(frame1)
    	frame3 = self.__build_frame(frame2)
    	frame4 = self.__build_frame(self, column=1, sticky="ns")

    	# Fetch and Send buttons
    	self.__build_button(frame3, "Fetch", self.on_fetch_click)
    	self.__build_button(frame3, "Send", self.on_send_click, column=1)

    	# Search box
    	self.search = tk.StringVar()
    	searchEntry = tk.Entry(master=frame2, textvariable=self.search)
    	searchEntry.grid(row=1, column=0, sticky="ew", pady=5)
    	searchEntry.bind("<KeyRelease>", self.on_search_key)

    	# Treeview
    	self.etv = editabletreeview.EditableTreeview(height=20, columns=("name", "val"), selectmode="browse", show="headings")
    	self.etv.bind("<<TreeviewCellEdited>>", self.on_cell_changed)
    	self.etv.bind("<Double-1>", self.on_cell_double_click)
    	self.etv.bind("<FocusOut>", self.on_cell_focus_out)
    	self.etv.bind("<Button-1>", self.on_cell_focus_out, add=True)
    	self.etv.bind("<<TreeviewSelect>>", self.on_cell_selected, add=True)

    	# Treeview columns
    	self.etv.heading("name", text=u"Parameter \u2227", command=self.on_sort_click, anchor="w")
    	self.etv.column("name", stretch=True, minwidth=20, width=160, anchor="w")
    	self.etv.heading("val", text="Value", anchor="w")
    	self.etv.column("val", stretch=True, minwidth=20, width=240, anchor="w")

    	# Treeview scrollbar
    	scrollbar = tkscrollbarhelper.TkScrollbarHelper(master=frame1, scrolltype="vertical")
    	scrollbar.grid(row=1, column=0, sticky="nsew")
    	scrollbar.add_child(self.etv)

    	# Documentation text area
    	self.textDocs = tk.Text(master=frame4, background="#d9d9d9", borderwidth=0, width=40, state="disabled")
    	self.textDocs.pack(side="bottom", anchor="s", fill="x", expand=True, padx=20)

    def __build_frame(self, master, row=0, column=0, sticky=""):
    	frame = tk.Frame(master=master)
    	frame.grid(row=row, column=column, sticky=sticky)
    	frame.grid_rowconfigure(0, weight=1)
    	frame.grid_columnconfigure(0, weight=1)
    	return frame

    def __build_button(self, master, text, callback, row=0, column=0):
    	btn = tk.Button(master=master, text=text)
    	btn.grid(row=row, column=column, ipadx=10, padx=20, pady=5)
    	btn.bind("<Button-1>", self.on_cell_focus_out)
    	btn.bind("<ButtonRelease-1>", callback)

    def __update(self):
        params = [(self.etv.set(item_id, "name"), item_id) for item_id in self.etv_items]
        params.sort(reverse=self.sort_desc)

        for indx, item in enumerate(params):   # item: (item value, item_id)
	    if self.__search(item[0]):
        	self.etv.move(item[1], '', indx)
	    else:
    		self.etv.selection_remove(item[1])
    		self.etv.detach(item[1])

    def __search(self, item):
    	search_terms = self.search.get().upper().split(' ')
    	for search in search_terms:
    	    if not search in item:
                return False
    	return True

    def __get_selection(self):
    	items = self.etv.selection()
    	if len(items) == 0:
    	    return None
    	return items[0]

    def __remove_inline_entry(self):
        self.etv._EditableTreeview__clear_inplace_widgets()

    def __set_docs_text(self, text):
    	self.textDocs.config(state="normal")
    	self.textDocs.delete(1.0, "end")
    	self.textDocs.insert("end", text)
    	self.textDocs.config(state="disabled")

    def on_sort_click(self):
    	self.__remove_inline_entry()

    	self.sort_desc = not self.sort_desc
    	if self.sort_desc:
    	    self.etv.heading("name", text=u"Parameter \u2228")   # down arrow
    	else:
    	    self.etv.heading("name", text=u"Parameter \u2227")   # up arrow

    	self.__update()

    def on_cell_selected(self, event):
        item = self.__get_selection()
        if item == None:
            self.__set_docs_text("")
            return
        param = self.etv.set(item, "name")

        docs = self.docs[param]
        doc_string = param + ":\n" + docs.attrib['humanName'] + "\n\n" + docs.attrib['documentation'] + "\n\n"
        for child in docs:
            if child.tag == "field":
                doc_string += child.attrib['name'] + ": " + child.text + "\n"
            elif child.tag == "values":
                doc_string += "Values:\n"
            for vchild in child:
                if vchild.tag == "value":
                    doc_string += "    " + vchild.attrib['code'] + ": " + vchild.text + "\n"
        self.__set_docs_text(doc_string)

    def on_cell_double_click(self, event):
    	item = self.__get_selection()
    	if item == None:
    	    return
        self.etv.inplace_entry('val', item)
    	self.etv._EditableTreeview__updateWnds()

    def on_cell_focus_out(self, event):
	       self.__remove_inline_entry()

    def on_cell_changed(self, event):
        item = self.__get_selection()
    	if item == None:
    	    return
        print 'Item {0} was changed to {1}'.format(item, self.etv.set(item, "val"))

    def on_fetch_click(self, event):
        self.state.pipe_gui.send(ParamFetch())

    def on_send_click(self, event):
        item = self.__get_selection()
    	if item == None:
    	    return
        param = Param(self.etv.set(item, "name"), self.etv.set(item, "val"))
        self.state.pipe_gui.send(ParamSendList([param]))

    def on_search_key(self, event):
        self.__update()

    def on_window_resize(self, event):
    	if event.height != self.last_height:
    	    self.last_height = event.height
    	    self.etv.config(height=(event.height-86)/20)
    	    self.textDocs.config(height=(event.height-86)/14)

    def on_timer(self):
        '''Main Loop.'''
        if self.state.close_event.wait(0.001):
            self.mainwindow.destroy()
            return
        # Get messages
        while self.state.pipe_gui.poll():
            obj = self.state.pipe_gui.recv()
            if isinstance(obj, ParamUpdateList):
                for param in obj.params:
                    self.__parse_param(param)
        self.mainwindow.after(100, self.on_timer)

    def __parse_param(self, param):
        print "Update '{0}' to '{1}'.".format(param.name, param.value)
