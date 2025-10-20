import obd

class Metric():
    def __init__(self, name, unit, calculation_function, commands, short, key):
        self.name = name #name of the metric
        self.unit = unit #unit it is measured in
        self.commands = commands #any commands to issue to the car to get values we want
        self.calculation_function = calculation_function # help us combine multiple values or do maths to get a useful number
        
        self.watching = False
        self.short = short
        self.key = key

    def setVehicle(self, vehicle):
        self.vehicle = vehicle
        if self.vehicle.connected:
            self.startWatching()

    def getValue(self):
        values = []
        for command in self.commands:
            response = self.vehicle.query(command) # get each metric we need from the car
            if response.is_null(): #if the car dosen't support it, set it to 0 so the true value is always 0.
                values.append(0)
            else:
                values.append(response.value.magnitude)

        if self.calculation_function:
            return self.calculation_function(values)
        else:
            return values[0]
        
    def startWatching(self):
        for command in self.commands:
            self.vehicle.watchCommand(command)
            print(self.vehicle.watched_commands)
        self.watching = True

    def getUnit(self):
        return self.unit
    
    def getName(self):
        return self.name
    
    def getShort(self):
        return self.short
    
    def getKey(self):
        return self.key

def convertSpeed(values):
    speed_kmh = values[0]
    speed_mph = speed_kmh / 1.609
    return speed_mph

def calculateBoost(values):
    intake_pressure = values[0]
    barometric_pressure = values[1]
    return intake_pressure - barometric_pressure

## TORQUE
def convertTorquePercent(messages): #handle bytes from car for torque % mode 01 pid 62
    d = messages[0].data
    d = d[2:]
    v = obd.utils.bytes_to_int(d)
    return (v - 125) * obd.Unit.PERCENT

def convertTorqueReference(messages): #handle bytes from car for torque reference mode 01 pid 63
    d = messages[0].data
    d = d[2:]
    v = obd.utils.bytes_to_int(d)
    return v * obd.Unit.NEWTON_METER

def calculateActualTorque(values):
    torque_percent = values[0]
    torque_reference = values[1]
    return (torque_percent / 100) * torque_reference

torquePercentCommand = obd.OBDCommand("Torque", "Actual Torque Percentage", b"0162", 3, convertTorquePercent)
torqueReferenceCommand = obd.OBDCommand("Torque", "Calculated Torque", b"0163", 4, convertTorqueReference)

## POWER

def calculatePower(values):
    torque_percent = values[0]
    torque_reference = values[1]
    torque = calculateActualTorque([ torque_percent, torque_reference])
    rpm = values[2]
    return (torque * rpm) / 9549  # Power = Torque * RPM / 9549

## METRICS

our_metrics = {
    "Engine_Load": Metric("Engine Load", "%", None, [obd.commands.ENGINE_LOAD], "Load", "Engine_Load"),
    "Coolant_Temp": Metric("Coolant Temp", "°C", None, [obd.commands.COOLANT_TEMP], "Cool temp", "Coolant_Temp"),
    "Fuel_Pressure": Metric("Fuel Pressure", "kPa", None, [obd.commands.FUEL_PRESSURE], "Fuel Pres", "Fuel_Pressure"),
    "Intake_Pressure": Metric("Intake Pressure", "kPa", None, [obd.commands.INTAKE_PRESSURE], "In Pres", "Intake_Pressure"),
    "RPM": Metric("RPM", "rpm", None, [obd.commands.RPM], "RPM", "RPM"),
    "Speed": Metric("Speed kmh", "km/h", None, [obd.commands.SPEED], "Speed", "Speed"),
    "Speed_mph": Metric("Speed mph", "mph", convertSpeed, [obd.commands.SPEED], "Speed", "Speed_mph"),
    "Intake_Temp": Metric("Intake Temp", "°C", None, [obd.commands.INTAKE_TEMP], "In Temp", "Intake_Temp"),
    "MAF": Metric("Mass Air Flow", "g/s", None, [obd.commands.MAF], "MAF", "MAF"),
    "Throttle_Pos": Metric("Throttle Position", "%", None, [obd.commands.THROTTLE_POS], "Throttle", "Throttle_Pos"),
    "Run_Time": Metric("Engine Run Time", "s", None, [obd.commands.RUN_TIME], "Run Time", "Run_Time"),
    "Distance_W_MIL": Metric("Distance with MIL", "km", None, [obd.commands.DISTANCE_W_MIL], "MIL Dist", "Distance_W_MIL"),
    "Fuel_Level": Metric("Fuel Level", "%", None, [obd.commands.FUEL_LEVEL], "Fuel Level", "Fuel_Level"),
    "Barometric_Pressure": Metric("Barometric Pressure", "kPa", None, [obd.commands.BAROMETRIC_PRESSURE], "Baro Pres", "Barometric_Pressure"),
    "Absolute_Load": Metric("Absolute Load", "%", None, [obd.commands.ABSOLUTE_LOAD], "Abs Load", "Absolute_Load"),
    "Relative_Throttle_Pos": Metric("Relative Throttle Position", "%", None, [obd.commands.RELATIVE_THROTTLE_POS], "Rel Throt", "Relative_Throttle_Pos"),
    "Ambient_Air_Temp": Metric("Ambient Air Temp", "°C", None, [obd.commands.AMBIANT_AIR_TEMP], "Amb Temp", "Ambient_Air_Temp"),
    "Fuel_Rail_Pressure_Abs": Metric("Fuel Rail Pressure", "kPa", None, [obd.commands.FUEL_RAIL_PRESSURE_ABS], "Fuel Rail Pres", "Fuel_Rail_Pressure_Abs"),
    "Relative_Accel_Pos": Metric("Relative Accel Position", "%", None, [obd.commands.RELATIVE_ACCEL_POS], "Rel Accel", "Relative_Accel_Pos"),
    "Hybrid_Battery_Remaining": Metric("Hybrid Battery Remaining", "%", None, [obd.commands.HYBRID_BATTERY_REMAINING], "Battery", "Hybrid_Battery_Remaining"),
    "Oil_Temp": Metric("Oil Temperature", "°C", None, [obd.commands.OIL_TEMP], "Oil Temp", "Oil_Temp"),
    "Fuel_Inject_Timing": Metric("Fuel Injection Timing", "°", None, [obd.commands.FUEL_INJECT_TIMING], "Inj time", "Fuel_Inject_Timing"),
    "Fuel_Rate": Metric("Fuel Rate", "L/h", None, [obd.commands.FUEL_RATE], "Fuel Rate", "Fuel_Rate"),
    "Boost": Metric("Boost", "kPa", calculateBoost, [ obd.commands.INTAKE_PRESSURE, obd.commands.BAROMETRIC_PRESSURE], "Boost", "Boost"),
    "Torque": Metric("Torque", "N/m", calculateActualTorque, [ torquePercentCommand, torqueReferenceCommand ], "Torque", "Torque"),
    "Power": Metric("Power", "kW", calculatePower, [ torquePercentCommand, torqueReferenceCommand, obd.commands.RPM ], "Power", "Power"), # Power = Torque * RPM / 9549
}
