import Tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
  
class DummyPlotWidget:
    def __init__(self, master):
        self.i = 0
        
        self.frame = tk.Frame( master )
        self.frame.pack( fill=tk.BOTH, expand=1 )
        
        tk.Label( master=self.frame, text="Plot..." ).pack()
        
        fig = plt.Figure(figsize=(1,1), dpi=100)
          
        self.x = np.arange(0, 2*np.pi, 0.01)        # x-array
        
        ax = fig.add_subplot(111)
        ax.set_yticks([])
        ax.set_xticks([])
        self.line, = ax.plot(self.x, np.sin(self.x))
    
        self.canvas = FigureCanvasTkAgg( fig, master=self.frame )
        self.canvas.show()
        self.canvas.get_tk_widget().pack( side=tk.TOP, fill=tk.BOTH, expand=1 )
        
    def show( self ):
        self.line.set_ydata(np.sin(self.x+self.i/10.0))  # update the data
        self.i = self.i + 1
        self.canvas.show()
    