
from series.series_download import SeriesRetriever
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

sg = SeriesRetriever()

job = ('Supernatural', 'http://www.tv.com/supernatural/show/30144/summary.html')

# put serie to look for in the in_queue
sg.in_queue.put(job)

# start service and wait for finish
print "Press Ctrl-C to terminate retrieving"

sg.start()

while 1:
    if not sg.out_queue.empty():
        logging.info('Retrieving result from SeriesRetriever')
        item = sg.out_queue.get()
        sg.out_queue.task_done()
        
        if not item[1]:
            logging.info("Error retrieving item '%s' with message '%s'" % (item[0], item[2]))
        
    else:
        time.sleep(1)

