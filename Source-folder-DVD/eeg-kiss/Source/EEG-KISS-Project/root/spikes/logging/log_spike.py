from random import randint
import logging
import time

if __name__ == '__main__':
    
    logger = logging.getLogger()

    DATE = time.strftime('%y%m%d_%H%M%S')   # Every second a new file
    DATE = time.strftime('%y%m%d')          # Every day e new logfile
    logging.basicConfig(level=logging.INFO, filename='example_%s.log'%(DATE), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter =logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # logging.getLogger().addHandler(logging.StreamHandler())

    print "Hi there..."
    
    l = []
    for _ in range(1000000):
        l.append(randint(0,64000))
        if l[-1] > 63900:
            logging.info('%d is a pretty big number' % l[-1])
            
        if l[-1] > 63995:
            logging.warning('%d is a VERY big number' % l[-1])
  
