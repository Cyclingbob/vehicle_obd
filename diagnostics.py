import obd
import commands
from config import reconnect_attempts
obd.logger.removeHandler(obd.console_handler)
import time
from metrics import our_metrics

class BitArray:
    """
    Class for representing bitarrays (inefficiently)

    There's a nice C-optimized lib for this: https://github.com/ilanschnell/bitarray
    but python-OBD doesn't use it enough to be worth adding the dependency.
    But, if this class starts getting used too much, we should switch to that lib.
    """

    def __init__(self, _bytearray):
        self.bits = ""
        for b in _bytearray:
            v = bin(b)[2:]
            self.bits += ("0" * (8 - len(v))) + v  # pad it with zeros

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= 0 and key < len(self.bits):
                return self.bits[key] == "1"
            else:
                return False
        elif isinstance(key, slice):
            bits = self.bits[key]
            if bits:
                return [b == "1" for b in bits]
            else:
                return []

    def num_set(self):
        return self.bits.count("1")

    def num_cleared(self):
        return self.bits.count("0")

    def value(self, start, stop):
        bits = self.bits[start:stop]
        if bits:
            return int(bits, 2)
        else:
            return 0

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return self.bits

    def __iter__(self):
        return [b == "1" for b in self.bits].__iter__()

def pid(messages):
    d = messages[0].data[2:]
    return BitArray(d)

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
    # def findMutualCommands(self):
    #     for supported_PID in self.supported_PIDs:
    #         if str(supported_PID) in self.commands_we_support:
    #             self.mutual_PIDS.append(supported_PID)

    def findMutualMetrics(self):
        supported_commands = set(self.mutual_PIDS)
        mutual_metrics = []
        for metric_name, metric_obj in our_metrics.items():
            # Check if all commands for this metric are supported
            if all(cmd in supported_commands for cmd in metric_obj.commands):
                mutual_metrics.append(metric_name)
        return mutual_metrics

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
                PIDS_C = commands.adjust_supported_bit_array(bit_array3, 0x41)
                self.supported_PIDs = [ *self.supported_PIDs, *PIDS_C ]

                PIDS_D_cmd = 96
                if PIDS_D_cmd in PIDS_C: #If it supports PID
                    command4 = obd.OBDCommand("PIDS_D", "Supported PIDs D", b"0160", 6, pid)
                    response4 = self.connection.query(command4)
                    bit_array4 = list(response4.value)

                    PIDS_D = commands.decode_bit_array(bit_array4)
                    PIDS_D = commands.adjust_supported_bit_array(bit_array4, 0x61)
                    self.supported_PIDs = [ *self.supported_PIDs, *PIDS_D ]

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