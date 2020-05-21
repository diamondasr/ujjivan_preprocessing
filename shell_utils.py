
import logging
from log_utils import setup_logger

def generic_shell(shell_command,log_file_name):
    """
        this defines a python function which can run any shell script command
        from python and route logs to log file 
    """
    try:
        #print(shell_command.split())
        process = subprocess.Popen(shell_command,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,shell=True)
        stdout, stderr = process.communicate()

        if stderr:

            shell_logger=setup_logger(log_file_name, log_file_name, level=logging.INFO)
            shell_logger.error(stderr)
    except:
        print("Exception during running generic shell with following command - ")
        shell_logger=setup_logger(log_file_name, log_file_name, level=logging.INFO)
        shell_logger.error(stderr)