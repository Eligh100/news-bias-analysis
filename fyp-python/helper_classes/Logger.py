from datetime import datetime

class Logger():
    """Enables logging of exceptions, outputting to .txt file

    Keyword Arguments:
        log_path {None/string} -- Specify path for log file, or use default (default: "log.txt")
    """

    def __init__(self, log_path=None):
        if (log_path is None):
            self.log_path = "log.txt"
        else:
            self.log_path = log_path

    def writeToLog(self, log_line, include_datetime):
        """Write user-specified line to the log file
        
        Arguments:
            log_line {string} -- string line to be written
            include_datetime {bool} -- flag of whether to append current time to log_line
        """

        try:
            with open(self.log_path, "a", encoding="utf-8") as log_file:
                if (include_datetime):
                    now = datetime.now() # current date and time
                    current_time = now.strftime("%d/%m/%Y, %H:%M:%S")
                    log_line += current_time
                log_line += "\n"
                log_file.write(log_line)
        except:
                print("Writing to log file failed - THIS IS BAD!")


