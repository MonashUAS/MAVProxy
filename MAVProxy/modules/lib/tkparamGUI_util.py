try:
    import tkinter as tk
except:
    import Tkinter as tk

##### Message Types #####

class ParamUpdateList():
    '''List of parameters to be updated. Sent from module to GUI.'''
    def __init__(self, params):
        self.params = params

class ParamSendList():
    '''List of parameters to be sent to the aircraft. Sent from GUI to module.'''
    def __init__(self, params):
        self.params = params

class ParamSendReturn():
    '''Parameter containing the return value after being sent to the aircraft. Sent from module to GUI.'''
    def __init__(self, param):
        self.param = param

class ParamSendFail():
    '''Parameter was unsuccessfully sent to the aircraft. Sent from module to GUI.'''
    def __init__(self, param_name):
        self.param_name = param_name

class ParamFetch():
    '''Message to initiate a parameter fetch. Sent from GUI to module.'''
    pass

class Param():
    '''A Parameter. Not to be sent down pipe by itself (use an above class). Value must be a float.'''
    def __init__(self, name, value):
        self.name = name
        self.value = value


##### GUI Elements #####

class ScrollableFrame(tk.Frame):
    '''A tk frame whose child elements can be scrolled.'''

    def __init__(self, master, scrolltype="both", scrollrate=1, *args, **kw):
    	self.__scroll_rate = scrollrate
    	self.__scroll_tag = "ScrollableFrame_scroll"

    	# Outer frame
    	self.__frameOuter = tk.Frame(master=master, *args, **kw)

    	# Canvas
    	self.__canvas = tk.Canvas(master=self.__frameOuter, bd=0, highlightthickness=0)

    	# Scrollbars
    	if scrolltype == "vertical" or scrolltype == "both":
    	    vscrollbar = tk.Scrollbar(master=self.__frameOuter, orient="vertical", command=self.__canvas.yview)
            vscrollbar.pack(fill="y", side="right")
    	    self.__canvas.config(yscrollcommand=vscrollbar.set)

    	if scrolltype == "horizontal" or scrolltype == "both":
    	    hscrollbar = tk.Scrollbar(master=self.__frameOuter, orient="horizontal", command=self.__canvas.xview)
            hscrollbar.pack(fill="x", side="bottom")
    	    self.__canvas.config(xscrollcommand=hscrollbar.set)

        # Initialize canvas
    	self.__canvas.pack(side="left", fill="y", expand=True)
        self.__canvas.xview_moveto(0)
        self.__canvas.yview_moveto(0)

    	# Inner frame
    	tk.Frame.__init__(self, master=self.__canvas)
    	self.bind("<Configure>", self.__configure_interior)
    	self.__canvas.create_window(0, 0, window=self, anchor="nw")

    	# Passthrough basic geometry manager methods
    	self.pack = self.__frameOuter.pack
    	self.pack_configure = self.__frameOuter.pack_configure
    	self.pack_forget = self.__frameOuter.pack_forget

    	self.grid = self.__frameOuter.grid
    	self.grid_configure = self.__frameOuter.grid_configure
    	self.grid_forget = self.__frameOuter.grid_forget
    	self.grid_remove = self.__frameOuter.grid_remove

    	self.place = self.__frameOuter.place
    	self.place_configure = self.__frameOuter.place_configure
    	self.place_forget = self.__frameOuter.place_forget

    # Track changes to the canvas and frame width and sync them as well as updating the scrollbar
    def __configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        self.__canvas.config(scrollregion=(0, 0, max(self.winfo_reqwidth(), self.__canvas.winfo_width()), max(self.winfo_reqheight(), self.__canvas.winfo_height())))
        if self.winfo_reqwidth() != self.__canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.__canvas.config(width=self.winfo_reqwidth())

        # Event maybe as a result of adding a new child widget.
        # Therefore bind any new child elements to the scrollwheel.
        self.__bind_scrollwheel()

    def __on_scrollwheel_up(self, event):
        self.__canvas.yview_scroll(-1*self.__scroll_rate, "units")

    def __on_scrollwheel_down(self, event):
        self.__canvas.yview_scroll(self.__scroll_rate, "units")

    def __tag_widget(self, widget):
    	bindtags = widget.bindtags()
    	if not self.__scroll_tag in bindtags:
    	    widget.bindtags((self.__scroll_tag,) + bindtags)

    	for child in widget.winfo_children():
    	    self.__tag_widget(child)

    # Must be run when the contents of the inner frame is changed
    def __bind_scrollwheel(self):
    	self.__tag_widget(self.__canvas)
    	self.__frameOuter.bind_class(self.__scroll_tag, "<Button-4>", self.__on_scrollwheel_up)
    	self.__frameOuter.bind_class(self.__scroll_tag, "<Button-5>", self.__on_scrollwheel_down)
