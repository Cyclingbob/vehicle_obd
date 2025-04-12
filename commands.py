import obd

commands_we_support = {
    "4": obd.commands.ENGINE_LOAD,
    "5": obd.commands.COOLANT_TEMP,
    "10": obd.commands.FUEL_PRESSURE,
    "11": obd.commands.INTAKE_PRESSURE,
    "12": obd.commands.RPM,
    "13": obd.commands.SPEED,
    "15": obd.commands.INTAKE_TEMP,
    "16": obd.commands.MAF,
    "17": obd.commands.THROTTLE_POS,
    "31": obd.commands.RUN_TIME,
    "33": obd.commands.DISTANCE_W_MIL,
    "47": obd.commands.FUEL_LEVEL,
    "51": obd.commands.BAROMETRIC_PRESSURE,
    "67": obd.commands.ABSOLUTE_LOAD,
    "69": obd.commands.RELATIVE_THROTTLE_POS,
    "70": obd.commands.AMBIANT_AIR_TEMP,
    "89": obd.commands.FUEL_RAIL_PRESSURE_ABS,
    "90": obd.commands.RELATIVE_ACCEL_POS,
    "91": obd.commands.HYBRID_BATTERY_REMAINING,
    "92": obd.commands.OIL_TEMP,
    "93": obd.commands.FUEL_INJECT_TIMING,
    "94": obd.commands.FUEL_RATE
}

def decode_bit_array(string: str) -> list: # returns indexes of supported commands
    supported_indexes = []
    count = 0
    for char in string:
        bit = int(char)
        if bit == True:
            supported_indexes.append(count)
        count = count + 1
    return supported_indexes

def adjust_supported_bit_array(array: list, lowest: hex) -> list:
    lowest = int(lowest)

    # adjusted_PIDs = []
    
    for index in range(0, len(array), 1):
        array[index] = array[index] + lowest
        # adjusted_PIDs.append(array[index] + 1)

    return array

# def get_supported_commands()