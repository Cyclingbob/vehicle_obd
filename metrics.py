import obd

class Metric():
    def __init__(self, name, unit, calculation_function, commands):
        self.name = name #name of the metric
        self.unit = unit #unit it is measured in
        self.commands = commands #any commands to issue to the car to get values we want
        self.calculation_function = calculation_function # help us combine multiple values or do maths to get a useful number
        
        self.watching = False

    def setVehicle(self, vehicle):
        self.vehicle = vehicle
        if self.vehicle.connected:
            self.startWatching()

    def getValue(self):
        values = []
        for command in self.commands:
            response = self.vehicle.query(command) # get each metric we need from the car
            print(response)
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

# class Metric2():
#     def __init__(self, name, unit, calculation_function, commands):
#         self.name = name #name of the metric
#         self.unit = unit #unit it is measured in
#         self.commands = commands #any commands to issue to the car to get values we want
#         self.calculation_function = calculation_function # help us combine multiple values or do maths to get a useful number

#     def setup(self):
#         global connection
#         for command in self.commands:
#             connection.watch(command)

#     def getValue(self):
#         values = []
#         for command in self.commands:
#             response = connection.query(command) # subscribe to each metric we need from the car
#             if response.is_null(): #if the car dosen't support it, set it to 0 so the true value is always 0.
#                 values.append(0)
#             else:
#                 values.append(response.value.magnitude)

#         if self.calculation_function:
#             return self.calculation_function(values)
#         else:
#             return values[0]

#     def printValue(self):
#         return str(self.getValue()) + self.unit

def convertSpeed(values):
    speed_kmh = values[0]
    speed_mph = speed_kmh / 1.609
    return speed_mph

def calculateBoost(values):
    intake_pressure = values[0]
    barometric_pressure = values[1]
    return intake_pressure - barometric_pressure

our_metrics = {
    "Engine_Load": Metric("Engine Load", "%", None, [obd.commands.ENGINE_LOAD]),
    "Coolant_Temp": Metric("Coolant Temp", "°C", None, [obd.commands.COOLANT_TEMP]),
    "Fuel_Pressure": Metric("Fuel Pressure", "kPa", None, [obd.commands.FUEL_PRESSURE]),
    "Intake_Pressure": Metric("Intake Pressure", "kPa", None, [obd.commands.INTAKE_PRESSURE]),
    "RPM": Metric("RPM", "rpm", None, [obd.commands.RPM]),
    "Speed": Metric("Speed kmh", "km/h", None, [obd.commands.SPEED]),
    "Speed_mph": Metric("Speed mph", "mph", convertSpeed, [obd.commands.SPEED]),
    "Intake_Temp": Metric("Intake Temp", "°C", None, [obd.commands.INTAKE_TEMP]),
    "MAF": Metric("Mass Air Flow", "g/s", None, [obd.commands.MAF]),
    "Throttle_Pos": Metric("Throttle Position", "%", None, [obd.commands.THROTTLE_POS]),
    "Run_Time": Metric("Engine Run Time", "s", None, [obd.commands.RUN_TIME]),
    "Distance_W_MIL": Metric("Distance with MIL", "km", None, [obd.commands.DISTANCE_W_MIL]),
    "Fuel_Level": Metric("Fuel Level", "%", None, [obd.commands.FUEL_LEVEL]),
    "Barometric_Pressure": Metric("Barometric Pressure", "kPa", None, [obd.commands.BAROMETRIC_PRESSURE]),
    "Absolute_Load": Metric("Absolute Load", "%", None, [obd.commands.ABSOLUTE_LOAD]),
    "Relative_Throttle_Pos": Metric("Relative Throttle Position", "%", None, [obd.commands.RELATIVE_THROTTLE_POS]),
    "Ambient_Air_Temp": Metric("Ambient Air Temp", "°C", None, [obd.commands.AMBIANT_AIR_TEMP]),
    "Fuel_Rail_Pressure_Abs": Metric("Fuel Rail Pressure", "kPa", None, [obd.commands.FUEL_RAIL_PRESSURE_ABS]),
    "Relative_Accel_Pos": Metric("Relative Accel Position", "%", None, [obd.commands.RELATIVE_ACCEL_POS]),
    "Hybrid_Battery_Remaining": Metric("Hybrid Battery Remaining", "%", None, [obd.commands.HYBRID_BATTERY_REMAINING]),
    "Oil_Temp": Metric("Oil Temperature", "°C", None, [obd.commands.OIL_TEMP]),
    "Fuel_Inject_Timing": Metric("Fuel Injection Timing", "°", None, [obd.commands.FUEL_INJECT_TIMING]),
    "Fuel_Rate": Metric("Fuel Rate", "L/h", None, [obd.commands.FUEL_RATE]),
    "Boost": Metric("Boost", "kPa", calculateBoost, [ obd.commands.INTAKE_PRESSURE, obd.commands.BAROMETRIC_PRESSURE]),
}
