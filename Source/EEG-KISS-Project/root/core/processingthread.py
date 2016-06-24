from time       import sleep
from functools  import partial

import threading

class ProcessingThread:
    """
    Abstract class such that a subclass can continuously perform specific task.
    The task must be implemented as process_step() in the subclass.
    The interval between executions of the task can be specified.
    start() must be called before this thread does anything.
    """
    
    def __init__(self):
        self._running = False
        self._name = "no_name"
        self._thread = None
    
    def process_step(self):
        """
        This method must be implemented in a subclass and should implement a repetitive task
        """
        raise NotImplementedError("Implement process_step(self) in subclass")
    
    def _process( self, interval ):
        """
        @param interval
            the time between executions of the specified task
        """
        while self._running:
            self.process_step()
            sleep( interval / 1000. )

        self._thread = None
    
    def start(self, interval=10, name='no_name' ):  # in ms
        """
        Start the new thread for repetitive execution of a specified task.
         
        @param interval
            the time between executions of the specified task
        @param name
            the name of the thread
        """
        if self._thread is None:
            if not self._running:
                #print "Start thread %s with interval: %d" % (name, interval)
                self._running = True
                self._thread = threading.Thread( target=partial(self._process, interval), name=name )
                self._thread.daemon = True
                self._thread.start()
                self._name = name
        else:
            # NOTE: Now this message is printed each time reinit of selected visualization is called.
            #       This should be refactored somehow in a way that this message is not printed when thread was already started.
            if self._running:
                print 'Thread was already started (%s)' % self._name
            else:
                print "ERROR: Thread cannot be started from itself! (%s)" % self._name
    
    def stop(self):
        if self._running:
            #print 'Stop thread:', self._name
            self._running = False
#             while self._thread != None:
#                 pass

    def isIdle(self):
        return self._running == False and self._thread == None
    
    def getName(self):
        return self._name
