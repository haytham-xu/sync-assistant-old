
import logging, time

logging.basicConfig(filename='./logs/' + time.strftime("%Y%m%d", time.localtime()) +'.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)
