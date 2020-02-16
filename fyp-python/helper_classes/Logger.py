from datetime import datetime

class Logger():

    def __init__(self, log_path=None):
        if (log_path is None):
            self.log_path = "log.txt"
        else:
            self.log_path = log_path

    def writeToLog(self, log_line, include_datetime):
        try:
            with open("log.txt", "a", encoding="utf-8") as log_file:
                if (include_datetime):
                    now = datetime.now() # current date and time
                    current_time = now.strftime("%d/%m/%Y, %H:%M:%S")
                    log_line += current_time
                log_line += "\n"
                log_file.write(log_line)
        except:
                print("Writing to log file failed")