import logging
from collections import deque
import threading
import smtplib
from email.utils import formatdate


class ThresholdMailHandler(logging.Handler):
    """
    Buffer log messages and send them by email if flushLevel is reached or exceeded
    """


    def __init__(self, capacity, mailhost, fromAddr, toAddrs, mailSubject=None, flushLevel=logging.ERROR):
        """
        Args:
            capacity    (int): how many message records to hold in buffer
            mailhost    (tuple): (host_ip, host_port) of mail server
            fromAddr    (str): email from address
            toAddrs     (str|list): mail recipients as list of strings or single string
            mailSubject (str): subject of all emails sent by this logger
            flushLevel  (int): level from which this logger triggers, sending the emails
        """
        logging.Handler.__init__(self)
        self.flushLevel = flushLevel
        self.buffer = deque(maxlen=capacity)
        self.fromAddr = fromAddr
        self.mailSubject = mailSubject
        if isinstance(toAddrs, basestring):
            self.toAddrs = toAddrs
        else:
            self.toAddrs = ','.join(toAddrs)
        self.mailhost = mailhost
        self.flushReady = False 

        if mailSubject is None:
            import platform
            import os
            self.mailSubject = "%s:%s " % (platform.node(),os.path.abspath(__file__))
        else:
            self.mailSubject = mailSubject

    def shouldFlush(self, record):
        self.flushReady = (record.levelno >= self.flushLevel)
        return self.flushReady

    def emit(self, record):
        self.buffer.append(record)
        if self.shouldFlush(record):
            self.flush()

    def flush(self):
        if(self.flushReady==False):
            return
        tmp = [item for item in self.buffer]
        t = threading.Thread(target=self.doSend,args=(tmp,))
        # t.daemon = True
        t.start()
        self.buffer.clear()
        self.flushReady=False


    def doSend(self, buffer):
        print "launching doSend in thread ..."
        smtp = smtplib.SMTP(self.mailhost[0], self.mailhost[1])
        msg = "\n".join([self.format(record) for record in buffer])
        msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                        self.fromAddr,
                        self.toAddrs,
                        self.mailSubject,
                        formatdate(), msg)
        smtp.sendmail(self.fromAddr, self.toAddrs, msg)
        smtp.quit()



if __name__ == "__main__":

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    
    handler = ThresholdMailHandler(
        capacity=20, 
        mailhost=('91.212.254.3',25), 
        fromAddr='mliviu@infp.ro', 
        toAddrs='mlmarius@yahoo.com', 
        flushLevel=logging.WARNING, 
    )
    logger.addHandler(handler)

    for i in xrange(30):
        logger.debug('debug 1 debug 1')
    
    logger.error('error1 - should email here')



    for i in xrange(30):
        logger.debug('testing testing debug 2')
    
    logger.error('error2 - another mail now')

    print "main program finished ..."
