# -*- coding: utf-8 -*-

from loguru import logger

class Logging():

    def __init__(self):
        logger.add('logs.log', format='log time - {time:YYYY-MM-DD HH:mm:ss} | log level - {level} | {process.name} - {function} | module name: {module} - line: {line} | message - {message}', level='INFO', enqueue=True, backtrace=True)

if __name__ == "__main__":
    logger.add('logs.log', format='log time - {time:YYYY-MM-DD HH:mm:ss} | log level - {level} | {process.name} - {function} | module name: {module} - line: {line} | message - {message}', level='INFO', enqueue=True, backtrace=True)
    logger.info('Hello World!')