class GridNode:
    def __init__(self, node_id, node_type, max_capacity):
        self.node_id = node_id
        self.node_type = node_type
        self.max_capacity = max_capacity
        self.current_output = 0.0  # Positive for generation, negative for load

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "max_capacity": self.max_capacity,
            "current_output": self.current_output
        }


class BatteryNode(GridNode):
    def __init__(self, node_id, max_capacity, max_power=50.0, initial_soc=0.5):
        super().__init__(node_id, "battery", max_capacity)
        self.max_power = max_power  # Max charge/discharge rate (kW/MW)
        self.soc = initial_soc  # State of charge (0.0 to 1.0)
        self.efficiency = 0.90  # 90% charge/discharge efficiency

    def charge(self, power):
        # power is positive: we are storing energy (charging)
        # Cap by max charging power
        actual_charge_power = min(power, self.max_power)
        # Cap by remaining capacity
        available_room = (1.0 - self.soc) * self.max_capacity
        actual_charge_power = min(actual_charge_power, available_room / self.efficiency)
        
        if actual_charge_power > 0:
            self.soc += (actual_charge_power * self.efficiency) / self.max_capacity
            self.current_output = -actual_charge_power  # Consuming power from grid
        else:
            self.current_output = 0.0
        return actual_charge_power

    def discharge(self, power):
        # power is positive: we are releasing energy (discharging)
        # Cap by max discharging power
        actual_discharge_power = min(power, self.max_power)
        # Cap by available energy
        available_energy = self.soc * self.max_capacity
        actual_discharge_power = min(actual_discharge_power, available_energy)
        
        if actual_discharge_power > 0:
            self.soc -= actual_discharge_power / self.max_capacity
            self.current_output = actual_discharge_power  # Generating power to grid
        else:
            self.current_output = 0.0
        return actual_discharge_power

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "soc": round(self.soc, 3),
            "max_power": self.max_power,
            "charge_level_mwh": round(self.soc * self.max_capacity, 2)
        })
        return d


class GridSimulator:
    def __init__(self):
        self.nodes = {
            "Solar_Farm_A": GridNode("Solar_Farm_A", "solar", 100.0),
            "Wind_Farm_B": GridNode("Wind_Farm_B", "wind", 80.0),
            "Residential_Area_C": GridNode("Residential_Area_C", "residential_consumer", 120.0),
            "Industrial_Zone_D": GridNode("Industrial_Zone_D", "industrial_consumer", 150.0),
            "Fossil_Fuel_Plant_E": GridNode("Fossil_Fuel_Plant_E", "fossil_generation", 150.0),
            "Battery_Storage_F": BatteryNode("Battery_Storage_F", max_capacity=200.0, max_power=60.0, initial_soc=0.5)
        }
        self.grid_frequency = 50.0  # Hz
        self.base_load_scale = 1.0

    def get_telemetry(self, hour, temperature, weather):
        """
        Calculates active power values before rebalancing to simulate environmental impact.
        - hour: 0 to 23
        - temperature: in Celsius
        - weather: "sunny", "cloudy", "windy", "rainy", "stormy"
        """
        # 1. Solar Generation
        solar = self.nodes["Solar_Farm_A"]
        if 6 <= hour <= 18:
            # Solar peak at noon (hour 12)
            solar_factor = 1.0 - abs(hour - 12) / 6.0
            solar_factor = max(0.0, solar_factor)
            weather_mult = 1.0 if weather == "sunny" else (0.3 if weather in ["cloudy", "rainy"] else 0.1)
            solar.current_output = round(solar.max_capacity * solar_factor * weather_mult, 2)
        else:
            solar.current_output = 0.0

        # 2. Wind Generation
        wind = self.nodes["Wind_Farm_B"]
        wind_mult = 0.2
        if weather == "windy":
            wind_mult = 0.95
        elif weather == "stormy":
            wind_mult = 0.70  # Curtailed slightly for safety during extreme storms
        elif weather == "sunny":
            wind_mult = 0.3
        elif weather == "cloudy":
            wind_mult = 0.4
        wind.current_output = round(wind.max_capacity * wind_mult, 2)

        # 3. Residential Demand
        res = self.nodes["Residential_Area_C"]
        # Residential load peaks around 7-9 AM and 6-9 PM
        if 7 <= hour <= 9:
            res_factor = 0.75
        elif 18 <= hour <= 21:
            res_factor = 0.90
        elif 22 <= hour or hour <= 5:
            res_factor = 0.30
        else:
            res_factor = 0.50
        
        # Temperature effect (heating/cooling load)
        temp_mult = 1.0
        if temperature > 30:  # AC load
            temp_mult += (temperature - 30) * 0.03
        elif temperature < 10:  # Heating load
            temp_mult += (10 - temperature) * 0.04
        
        # Load is negative current_output
        res.current_output = -round(res.max_capacity * res_factor * temp_mult, 2)

        # 4. Industrial Demand
        ind = self.nodes["Industrial_Zone_D"]
        # Constant load during shift hours (8 AM - 6 PM), lower at night
        if 8 <= hour <= 18:
            ind_factor = 0.85
        else:
            ind_factor = 0.40
        ind.current_output = -round(ind.max_capacity * ind_factor, 2)

        # 5. Fossil Fuel Generation (default backup generation at minimum level)
        fossil = self.nodes["Fossil_Fuel_Plant_E"]
        fossil.current_output = 30.0  # Minimum stable generation before balancing

        # 6. Battery Storage (initially idle)
        battery = self.nodes["Battery_Storage_F"]
        battery.current_output = 0.0

        # Compute initial grid status
        telemetry = self.compute_status()
        telemetry.update({
            "hour": hour,
            "temperature": temperature,
            "weather": weather
        })
        return telemetry

    def compute_status(self):
        total_gen = 0.0
        total_load = 0.0
        
        for name, node in self.nodes.items():
            if node.current_output >= 0:
                total_gen += node.current_output
            else:
                total_load += abs(node.current_output)

        # Calculate grid frequency (ideal: 50.0 Hz)
        # If generation matches demand, frequency is 50.0 Hz
        # If demand exceeds supply, frequency drops (kinetic energy of turbines is drawn)
        # If supply exceeds demand, frequency rises
        imbalance = total_gen - total_load
        
        # Base load capacity divisor (scale of the grid)
        capacity_base = 250.0
        # Formula for frequency: drops if generation < load, increases if generation > load
        freq_change = (imbalance / capacity_base) * 0.5
        self.grid_frequency = round(50.0 + freq_change, 3)
        # Clamp frequency between safety shutdown values
        self.grid_frequency = max(45.0, min(self.grid_frequency, 55.0))

        # Check safety
        status = "STABLE"
        if 49.8 <= self.grid_frequency <= 50.2:
            status = "OPTIMAL"
        elif 49.5 <= self.grid_frequency <= 50.5:
            status = "STABLE"
        elif 48.5 <= self.grid_frequency < 49.5 or 50.5 < self.grid_frequency <= 51.5:
            status = "WARNING"
        else:
            status = "CRITICAL"

        return {
            "timestamp": f"{len(self.nodes)} Nodes Active",
            "generation": round(total_gen, 2),
            "demand": round(total_load, 2),
            "net_imbalance": round(imbalance, 2),
            "frequency_hz": self.grid_frequency,
            "status": status,
            "nodes": {name: node.to_dict() for name, node in self.nodes.items()}
        }

    def apply_balancing(self, recommendations):
        """
        Applies power output updates recommended by the Optimizer agent
        recommendations: dict of {node_id: power_adjustment}
        """
        # Apply fossil fuel adjustments
        if "Fossil_Fuel_Plant_E" in recommendations:
            fossil_adj = recommendations["Fossil_Fuel_Plant_E"]
            fossil = self.nodes["Fossil_Fuel_Plant_E"]
            fossil.current_output = max(10.0, min(fossil.max_capacity, fossil.current_output + fossil_adj))
            fossil.current_output = round(fossil.current_output, 2)

        # Apply battery adjustments (charging/discharging)
        if "Battery_Storage_F" in recommendations:
            bat_adj = recommendations["Battery_Storage_F"]
            battery = self.nodes["Battery_Storage_F"]
            if bat_adj > 0:
                # Discharge (generate power to grid)
                battery.discharge(bat_adj)
            elif bat_adj < 0:
                # Charge (consume power from grid)
                battery.charge(abs(bat_adj))
            else:
                battery.current_output = 0.0

        # Apply solar/wind curtailments if recommended
        if "Solar_Farm_A" in recommendations:
            curtail_adj = recommendations["Solar_Farm_A"]
            solar = self.nodes["Solar_Farm_A"]
            solar.current_output = max(0.0, solar.current_output + curtail_adj)
            solar.current_output = round(solar.current_output, 2)

        if "Wind_Farm_B" in recommendations:
            curtail_adj = recommendations["Wind_Farm_B"]
            wind = self.nodes["Wind_Farm_B"]
            wind.current_output = max(0.0, wind.current_output + curtail_adj)
            wind.current_output = round(wind.current_output, 2)

        # Apply load shedding if recommended (residential/industrial)
        if "Residential_Area_C" in recommendations:
            shed_adj = recommendations["Residential_Area_C"]
            res = self.nodes["Residential_Area_C"]
            # load is negative, adding positive value reduces magnitude of load
            res.current_output = min(0.0, res.current_output + shed_adj)
            res.current_output = round(res.current_output, 2)

        if "Industrial_Zone_D" in recommendations:
            shed_adj = recommendations["Industrial_Zone_D"]
            ind = self.nodes["Industrial_Zone_D"]
            ind.current_output = min(0.0, ind.current_output + shed_adj)
            ind.current_output = round(ind.current_output, 2)

        return self.compute_status()
