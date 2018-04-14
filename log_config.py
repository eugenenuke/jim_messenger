import logging
import logging.handlers

filename = 'jimm.log'
days = 1
backupCount = 31

# <дата-время> <уровень_важности> <имя_модуля> <имя_функции> <сообщение>
# log_format = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
log_format = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')

applog_handler = logging.handlers.TimedRotatingFileHandler(filename, 'D', days, backupCount, 'utf-8')
# NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
applog_handler.setLevel(logging.DEBUG)
applog_handler.setFormatter(log_format)

app_log = logging.getLogger('jimm')
app_log.setLevel(logging.DEBUG)
app_log.addHandler(applog_handler)


