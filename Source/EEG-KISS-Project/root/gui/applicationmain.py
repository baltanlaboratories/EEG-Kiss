from root.gui.applicationcontroller     import ApplicationController
from root.gui.applicationmodel          import ApplicationModel
from root.gui.applicationview           import ApplicationView

import logging
import time

def __main__():  
    """
    Initializes the windows and starts the application
    """ 
    logger = logging.getLogger()

    #DATE = time.strftime('%y%m%d_%H%M%S')   # Every second a new file
    DATE = time.strftime('%y%m%d')          # Every day e new logfile
    logging.basicConfig(level=logging.INFO, filename='logging_%s.log'%(DATE), format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.NOTSET)
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # Initialize the application components
    # First create view, tk instance must exist before you can create a object in the model (ex. IntVar())
    view        = ApplicationView()
    model       = ApplicationModel()
    controller  = ApplicationController( model, view )
    controller.update_gui_forever()
    
if __name__ == '__main__':
    __main__()
