from pygubu.widgets import tkscrollbarhelper, editabletreeview
from MAVProxy.modules.lib import mp_util
from tkparamGUI_util import *
import os.path
import tkinter as tk
import xml.etree.ElementTree

class ParamGUIFrame(tk.Frame):
    """ The main frame of the graphical parameter editor."""

    def __init__(self, state, mainwindow):
        self.state = state
        self.mainwindow = mainwindow
        self.sort_desc = False   # ascending
        self.last_height = -1

        self.status = [
            {"name": "new", "colour": "dodger blue"},
            {"name": "staged", "colour": "orange"},
            {"name": "updated", "colour": "green"},
            {"name": "failed", "colour": "orange red"}
        ]
        self.status_list = [status["name"] for status in self.status]

        # Build top level frame
        tk.Frame.__init__(self, master=self.mainwindow)
    	self.grid(row=0, column=0, sticky="nsew")
    	self.grid_rowconfigure(0, weight=1)
    	self.grid_columnconfigure(0, weight=1)
    	self.pack(side="top", fill="both", expand=True)

        self.__build_gui()
    	self.__build_data()

        # Bind filter and search controls to __update
        self.filter.trace_variable("w", lambda name, index, mode: self.__update())
        self.search.trace_variable("w", lambda name, index, mode: self.__update())

        self.__update()
        self.on_timer()   # start timer

    def __build_gui(self):
    	self.mainwindow.config(height=200, width=200)
    	self.mainwindow.minsize(600, 186)   # 5 rows

    	# Frames
        panedWindow1 = tk.PanedWindow(master=self, orient="horizontal", sashrelief="ridge")
        panedWindow1.pack(fill="both", expand=True)

        frameLPane = tk.Frame(master=panedWindow1)
    	frameLPane.grid(sticky="nsew")
    	frameLPane.grid_rowconfigure(1, weight=1)
    	frameLPane.grid_columnconfigure(0, minsize=100)
    	frameLPane.grid_columnconfigure(1, weight=1)
        frameLPane.bind("<Configure>", self.on_cell_window_resize)
        panedWindow1.add(frameLPane)

        frameRPane = self.__build_frame(panedWindow1, column=1)
        panedWindow1.add(frameRPane)

        self.frameFilter = tk.Frame(master=frameLPane)
        self.frameFilter.grid(rowspan=2, sticky="nsew", padx=10)
    	frameCtrl = self.__build_frame(frameLPane, column=1)

    	# Fetch and Send buttons
    	self.__build_button(frameCtrl, "Fetch", self.on_fetch_click)
    	self.__build_button(frameCtrl, "Send", self.on_send_click, column=1)

    	# Search box
    	self.search = tk.StringVar()
    	searchEntry = tk.Entry(master=frameCtrl, textvariable=self.search)
    	searchEntry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Treeview scrollbar
    	scrollbar = tkscrollbarhelper.TkScrollbarHelper(master=frameLPane, scrolltype="vertical")
    	scrollbar.grid(row=1, column=1, sticky="nsew")

    	# Treeview
    	self.etv = editabletreeview.EditableTreeview(master=scrollbar, height=20, columns=("name", "value"), selectmode="browse", show="headings")
        scrollbar.add_child(self.etv)
    	self.etv.bind("<<TreeviewCellEdited>>", self.on_cell_changed)
    	self.etv.bind("<Double-1>", self.on_cell_double_click)
    	self.etv.bind("<FocusOut>", self.on_cell_focus_out)
    	self.etv.bind("<Button-1>", self.on_cell_focus_out, add=True)
    	self.etv.bind("<<TreeviewSelect>>", self.on_cell_selected, add=True)
        self.__set_status_colours()

    	# Treeview columns
    	self.etv.heading("name", text=u"Parameter \u2227", command=self.on_sort_click, anchor="w")
    	self.etv.column("name", stretch=True, minwidth=20, width=160, anchor="w")
    	self.etv.heading("value", text="Value", anchor="w")
    	self.etv.column("value", stretch=True, minwidth=20, width=240, anchor="w")

    	# Documentation text area
    	self.textDocs = tk.Text(master=frameRPane, background="#d9d9d9", borderwidth=0, width=40, state="disabled")
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

    def __set_status_colours(self):
        for status in self.status:
            self.etv.tag_configure("status_"+status["name"], background=status["colour"])

    def __build_filter_list_button(self, master, text, value, ipadx=0, background="#d9d9d9"):
        b = tk.Radiobutton(master=master, text=text, value=value, variable=self.filter, indicatoron=False, background=background)
        b.pack(side="top", fill="x", ipadx=ipadx)
        b.bind("<Button-1>", self.on_cell_focus_out, add=True)

    def __build_filter_list(self, filters):
        self.filter = tk.StringVar()

        # Frames
        scrollFrame = ScrollableFrame(master=self.frameFilter, scrolltype="vertical")
        scrollFrame.pack(side="bottom", fill="both", expand=True)
        paddingFrame = tk.Frame(master=self.frameFilter, width=13)
        paddingFrame.pack(side="right", fill="y")

        # Radio buttons
        self.__build_filter_list_button(self.frameFilter, "None", "none")
        for status in self.status:
            self.__build_filter_list_button(self.frameFilter, status["name"].title(), status["name"], background=status["colour"])
        for fltr in filters:
            self.__build_filter_list_button(scrollFrame, fltr, fltr, ipadx=10)

        self.filter.set("none")

    def __build_data(self):
        xml_path = path = mp_util.dot_mavproxy("%s.xml" % self.state.vehicle_name)
        if not os.path.exists(xml_path):
            print("Please run 'param download' first (vehicle_name=%s)" % self.state.vehicle_name)
            return

        self.params = {}
        self.filters = {}
        self.docs = {}
        e = xml.etree.ElementTree.parse(xml_path).getroot()

        for parameters in e.iter("parameters"):
            fltr = parameters.attrib['name'].replace("_", "")
            self.filters[fltr] = []

            for param in parameters.iter("param"):
                name = param.attrib["name"].split(":")[-1].upper()
                self.filters[fltr].append(name)
                self.docs[name] = param

        filters = [fltr for fltr in self.filters]
        filters.remove(self.state.vehicle_name)
        filters.sort()

        self.__build_filter_list([self.state.vehicle_name] + filters)

    def __update(self):
        params = [(param_name, self.params[param_name]["id"]) for param_name in self.params]
        params.sort(reverse=self.sort_desc)

        for indx, item in enumerate(params):   # item: (item value, item_id)
    	    if self.__filter(item[0]) and self.__search(item[0]):
            	self.etv.move(item[1], '', indx)
    	    else:
        		self.etv.selection_remove(item[1])
        		self.etv.detach(item[1])

    def __filter(self, param_name):
        fltr = self.filter.get()
        if fltr == "none":
            return True
        if fltr in self.status_list:
            return fltr == self.params[param_name]["status"]
        return param_name in self.filters[fltr]

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
        param_name = self.etv.set(item, "name")
        doc_string = param_name + ":\n"

        if not param_name in self.docs:
            self.__set_docs_text(doc_string + "\nNo documentation available.")
            return

        docs = self.docs[param_name]
        doc_string += docs.attrib["humanName"] + "\n\n" + docs.attrib["documentation"] + "\n\n"
        if self.params[param_name]["status"] != "":
            doc_string += "Status: " + self.params[param_name]["status"] + "\n\n"
        for child in docs:
            if child.tag == "field":
                doc_string += child.attrib["name"] + ": " + child.text + "\n"
            elif child.tag == "values":
                doc_string += "Values:\n"
            for vchild in child:
                if vchild.tag == "value":
                    doc_string += "    " + vchild.attrib["code"] + ": " + vchild.text + "\n"
        self.__set_docs_text(doc_string)

    def on_cell_double_click(self, event):
    	item = self.__get_selection()
    	if item == None:
    	    return
        self.etv.inplace_entry("value", item)
    	self.etv._EditableTreeview__updateWnds()

    def on_cell_focus_out(self, event):
	       self.__remove_inline_entry()

    def on_cell_changed(self, event):
        item = self.__get_selection()
    	if item == None:
    	    return
        param_name = self.etv.set(item, "name")
        new_val = self.etv.set(item, "value")

        if new_val == "":
            # Parameter won't change instantly. So change after a small delay.
            self.mainwindow.after(1, lambda: self.etv.set(item, "value", self.params[param_name]["value"]))
            self.__clear_status_tag(param_name)
        elif new_val != self.params[param_name]["value"]:
            self.__set_status_tag(param_name, "staged")
        else:
            self.__clear_status_tag(param_name)
        self.__update()

    def on_fetch_click(self, event):
        self.state.pipe_gui.send(ParamFetch())
        self.__clear_status_tags()

    def on_send_click(self, event):
        sendList = []
        for param_name in self.params:
            if self.params[param_name]["status"] == "staged":
                sendList.append(Param(param_name, self.etv.set(self.params[param_name]["id"], "value")))
        self.state.pipe_gui.send(ParamSendList(sendList))

    def on_cell_window_resize(self, event):
    	if event.height != self.last_height:
    	    self.last_height = event.height
    	    self.textDocs.config(height=(event.height-86)/14)

    def on_timer(self):
        '''Main Loop.'''
        # Check if module has been unloaded
        if self.state.close_event.wait(0.001):
            self.mainwindow.destroy()   # close GUI
            return

        # Get messages
        while self.state.pipe_gui.poll():
            obj = self.state.pipe_gui.recv()
            if isinstance(obj, ParamUpdateList):
                for param in obj.params:
                    self.__update_param(param)
                self.__update()
        self.mainwindow.after(100, self.on_timer)

    def __update_param(self, param):
        if param.name in self.params:
            if param.value != self.params[param.name]["value"]:
                self.__set_status_tag(param.name, "new")
                self.params[param.name]["value"] = str(param.value)
                self.etv.set(self.params[param.name]["id"], "value", param.value)
        else:
            self.__new_param(param.name, param.value)

    def __new_param(self, name, value):
        param_id = self.etv.insert("", "end", values=(name, value))
        self.params[name] = {
            "value": str(value),   # stores the last value received from the module
            "id": param_id,
            "status": ""
        }

    # Must call self.__update() after using
    def __set_status_tag(self, param_name, status):
        self.etv.item(self.params[param_name]["id"], tags=("status_"+status,))
        self.params[param_name]["status"] = status

    # Must call self.__update() after using
    def __clear_status_tag(self, param_name):
        self.etv.item(self.params[param_name]["id"], tags=())
        self.params[param_name]["status"] = ""

    def __clear_status_tags(self):
        for param_name in self.params:
            self.__clear_status_tag(param_name)
        self.__update()
