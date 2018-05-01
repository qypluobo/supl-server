import logging

class Logger:
    def __init__(self):
        self.lg = logging.getLogger("SUPLServer")
        self.lg.setLevel(logging.DEBUG)

        #Output to screen
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        #Output to file
        fh = logging.FileHandler("supl.log")
        fh.setLevel(logging.DEBUG)

        fomatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        ch.setFormatter(fomatter)
        fh.setFormatter(fomatter)

        self.lg.addHandler(ch)
        self.lg.addHandler(fh)

    def debug(self, message):
        self.lg.debug(message)

    def info(self, message):
        self.lg.info(message)

    def warning(self, message):
        self.lg.warning(message)

    def error(self, message):
        self.lg.error(message)

logger = Logger()