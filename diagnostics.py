import obd
import commands
from config import reconnect_attempts
obd.logger.removeHandler(obd.console_handler)
import time

class Vehicle():
    def __init__(self):
        self.watched_commands = [ obd.commands.PIDS_A, obd.commands.PIDS_B, obd.commands.PIDS_C ]
        self.supported_PIDs = []
        self.mutual_PIDS = []
        self.commands_we_support = commands.commands_we_support
        self.connected = False
        self.ELM_connected = False
        self.connection_count = 0
    def connect(self):
        # self.connection_count = self.connection_count + 1
        # if(self.connection_count <= reconnect_attempts):
        self.connection = obd.Async()
        connection_status = self.connection.status()

        self.ELM_connected = not connection_status == obd.OBDStatus.NOT_CONNECTED
        if not self.connection.is_connected():
            # self.connect()
            self.connected = False
            print("OBD connection failed.")
            return False
        else:
            self.connected = True
            self.watchCommand(obd.commands.PIDS_A)
            self.watchCommand(obd.commands.PIDS_B)
            self.watchCommand(obd.commands.PIDS_C)
            self.start()
            self.getSupportedCommands()
            return True
        # else:
        #     print("OBD connection failed.")
        #     return False
    def findMutualCommands(self):
        for supported_PID in self.supported_PIDs:
            if str(supported_PID) in self.commands_we_support:
                self.mutual_PIDS.append(supported_PID)

    def getSupportedCommands(self):
        time.sleep(2)
        command1 = obd.commands.PIDS_A
        response1 = self.query(command1)
        # print(self.connection.query())
        bit_array1 = list(response1.value)
        # print(commands)

        PIDS_A = commands.decode_bit_array(bit_array1)
        PIDS_A = commands.adjust_supported_bit_array(PIDS_A, 0x01)
        self.supported_PIDs = [ *PIDS_A ]

        PIDS_B_cmd = 32
        if PIDS_B_cmd in PIDS_A: #If it supports PID
            command2 = obd.commands.PIDS_B
            response2 = self.connection.query(command2)
            bit_array2 = list(response2.value)

            PIDS_B = commands.decode_bit_array(bit_array2)
            PIDS_B = commands.adjust_supported_bit_array(bit_array2, 0x21)
            self.supported_PIDs = [ *self.supported_PIDs, *PIDS_B ]

            PIDS_C_cmd = 64
            if PIDS_C_cmd in PIDS_B: #If it supports PID
                command3 = obd.commands.PIDS_C
                response3 = self.connection.query(command3)
                bit_array3 = list(response3.value)

                PIDS_C = commands.decode_bit_array(bit_array3)
                PIDS_C = commands.adjust_supported_bit_array(bit_array3, 0x40)
                self.supported_PIDs = [ *self.supported_PIDs, *PIDS_C ]
    def watchCommand(self, command: obd.OBDCommand):
        if command not in self.watched_commands:  # Avoid duplicates
            self.watched_commands.append(command) 
        if self.connection.running:
            self.connection.stop()
        self.connection.watch(command)
    def start(self):
        self.connection.start()
    def query(self, command):
        if command in self.watched_commands:
            result = self.connection.query(command)
            return result