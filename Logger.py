"""
Containes the logger system for the game.
"""

from queue import Queue
import datetime
import os

class LogEntry:
    """
    Container for holding a log entry to be logged.
    
    Note:
    The latest logger instance will be used automatically through the LogEntry class.
    """
    
    __slots__ = ["system", "level", "description"]
    
    LOG_QUEUE : Queue | None = None
        
    LEVELS = {
        0 : "INFO",
        1 : "WARNING",
        2 : "ERROR"
    }
    
    def __init__(self, system : str, level : int, description : str):
        self.system = system
        self.level = self.LEVELS[level]
        self.description = description
    
    def push_to_queue(self) -> None:
        """
        Pushes the log into the log queue to be logged.
        LOG_QUEUE class variable must be set to the queue.
        """
        
        if self.LOG_QUEUE is None:
            raise RuntimeError("Logger not initialized before logging.")
        self.LOG_QUEUE.put(self)

class Logger:
    def __init__(self, logs_dir : str):
        self.verify_or_initialize_logs_dir(logs_dir)
        self.file = open(os.path.join(logs_dir, f"{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")}.txt"), "w")
        self.log_queue = Queue()
        LogEntry.LOG_QUEUE = self.log_queue # Intended.
        LogEntry("LOGGER", 0, f"Logger has been successfully initialized.").push_to_queue()
    
    def verify_or_initialize_logs_dir(self, logs_dir : str) -> None:
        """
        Verifies logs_dir exists, if not creates it.
        """
        
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)
    
    def push_log(self) -> None:
        """
        Writes one log from log_queue to the file.
        """
        
        if self.log_queue.empty():
            return
        log_entry : LogEntry = self.log_queue.get()
        self.file.write(f"<{log_entry.level}> [{log_entry.system}] : {log_entry.description}\n")
        if log_entry.level == "ERROR":
            self.flush()
    
    def push_logs(self, no_of_logs : int = 5) -> None:
        """
        Writes the given no_of_logs from the log_queue to the file.
        Absolute value of no_of_logs is used.
        """
        
        no_of_logs = abs(no_of_logs)
        
        while not self.log_queue.empty() and no_of_logs > 0:
            self.push_log()
            no_of_logs -= 1
    
    def flush(self) -> None:
        """
        Flushes all logs from the log_queue to the file.
        """
        
        while not self.log_queue.empty():
            self.push_log()
        self.file.flush()
    
    def log(self, log : LogEntry) -> None:
        """
        Adds log to log_queue.
        """
        
        log.push_to_queue()
    
    def close(self) -> None:
        """
        Closes log file.
        """
        
        self.flush()
        self.file.close()