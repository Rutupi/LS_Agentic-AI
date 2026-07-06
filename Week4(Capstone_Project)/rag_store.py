import json
import os
import math

class RAGStore:
    def __init__(self, filepath="historical_rag_data.json"):
        self.filepath = filepath
        self.scenarios = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.scenarios = json.load(f)
            except Exception as e:
                print(f"Error loading RAG data: {e}")
                self.scenarios = []
        else:
            self.scenarios = []

    def save_data(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.scenarios, f, indent=4)
        except Exception as e:
            print(f"Error saving RAG data: {e}")

    def add_scenario(self, scenario):
        self.scenarios.append(scenario)
        self.save_data()

    def seed_default_scenarios(self):
        """Seed default historical grid conditions for RAG retrieval."""
        default_data = [
            {
                "id": 1,
                "scenario_name": "Hot Summer Midday Peak",
                "hour": 13,
                "temperature": 36.0,
                "weather": "sunny",
                "solar_output": 95.0,
                "wind_output": 10.0,
                "residential_load": 110.0,
                "industrial_load": 140.0,
                "total_generation": 135.0,
                "total_demand": 250.0,
                "net_imbalance": -115.0,
                "rebalancing_action": "Discharged battery storage fully, ramped up Fossil Fuel Plant to 125MW to avoid rolling brownouts.",
                "description": "Typical peak-summer heatwave. Solar output is high, but cooling load from air conditioning pushes demand to extreme levels, creating a massive supply gap."
            },
            {
                "id": 2,
                "scenario_name": "Mild Spring Afternoon Surplus",
                "hour": 14,
                "temperature": 22.0,
                "weather": "sunny",
                "solar_output": 90.0,
                "wind_output": 35.0,
                "residential_load": 45.0,
                "industrial_load": 125.0,
                "total_generation": 155.0,
                "total_demand": 170.0,
                "net_imbalance": -15.0,
                "rebalancing_action": "Charged batteries at 15MW, ran fossil fuel plant at minimum stable generation of 30MW.",
                "description": "High solar generation combined with low residential demand due to mild temperatures. Grid is close to balanced with minimal backup support."
            },
            {
                "id": 3,
                "scenario_name": "Stormy Winter Evening Peak",
                "hour": 19,
                "temperature": 4.0,
                "weather": "stormy",
                "solar_output": 0.0,
                "wind_output": 65.0,
                "residential_load": 115.0,
                "industrial_load": 80.0,
                "total_generation": 95.0,
                "total_demand": 195.0,
                "net_imbalance": -100.0,
                "rebalancing_action": "Discharged battery storage at 40MW, ramped Fossil Fuel Plant to 90MW. Ramped wind back slightly to prevent grid over-voltage.",
                "description": "No solar generation. Severe wind generation from storm, but heating demand is extremely high due to freezing temperatures, causing a supply deficit."
            },
            {
                "id": 4,
                "scenario_name": "Overcast Windy Autumn Morning",
                "hour": 8,
                "temperature": 12.0,
                "weather": "cloudy",
                "solar_output": 15.0,
                "wind_output": 60.0,
                "residential_load": 85.0,
                "industrial_load": 130.0,
                "total_generation": 105.0,
                "total_demand": 215.0,
                "net_imbalance": -110.0,
                "rebalancing_action": "Ramped Fossil Fuel Plant to 110MW to cover the morning industrial startup surge. Kept batteries in reserve.",
                "description": "Morning industrial startup combined with residential breakfast peak. Overcast skies limit solar, making wind and fossil fuel the dominant generation sources."
            },
            {
                "id": 5,
                "scenario_name": "Calm Summer Night",
                "hour": 2,
                "temperature": 24.0,
                "weather": "sunny", # Night is clear
                "solar_output": 0.0,
                "wind_output": 5.0,
                "residential_load": 40.0,
                "industrial_load": 60.0,
                "total_generation": 35.0,
                "total_demand": 100.0,
                "net_imbalance": -65.0,
                "rebalancing_action": "Discharged battery storage at 35MW, ran Fossil Fuel Plant at minimum generation of 30MW.",
                "description": "Very low night-time load. Solar is zero and wind is calm. Low-cost battery storage meets the minor deficit, maintaining clean operation."
            },
            {
                "id": 6,
                "scenario_name": "Cold Winter Night Gale",
                "hour": 23,
                "temperature": 2.0,
                "weather": "windy",
                "solar_output": 0.0,
                "wind_output": 75.0,
                "residential_load": 55.0,
                "industrial_load": 60.0,
                "total_generation": 105.0,
                "total_demand": 115.0,
                "net_imbalance": -10.0,
                "rebalancing_action": "Charged batteries at 10MW to capture surplus wind. Kept Fossil Fuel at minimum stable level.",
                "description": "Late-night freezing weather increases heating demand, but a wind gale produces ample power. The surplus energy is captured by batteries."
            },
            {
                "id": 7,
                "scenario_name": "Hot Summer Evening Peak",
                "hour": 20,
                "temperature": 32.0,
                "weather": "cloudy",
                "solar_output": 0.0,
                "wind_output": 12.0,
                "residential_load": 120.0,
                "industrial_load": 75.0,
                "total_generation": 42.0,
                "total_demand": 195.0,
                "net_imbalance": -153.0,
                "rebalancing_action": "Discharged battery storage at 60MW, ramped Fossil Fuel Plant to 123MW. Performed minor load shedding of 10MW on Industrial node.",
                "description": "Peak evening load as residents return home. Temperatures are still hot, keeping AC demand high. Solar has dropped to zero, and wind is low, creating a critical shortage."
            }
        ]
        self.scenarios = default_data
        self.save_data()
        print(f"RAG Store seeded with {len(self.scenarios)} default scenarios.")

    def similarity_search(self, current_hour, current_temp, current_weather, k=2):
        """
        Calculates similarity using weighted multi-attribute distance metrics:
        - Hour difference (cyclic wrap-around 24h)
        - Temperature difference (absolute distance)
        - Weather match (categorical penalty)
        
        Returns the top k matching historical scenarios.
        """
        if not self.scenarios:
            return []

        scored_scenarios = []
        for s in self.scenarios:
            # 1. Hour distance with cyclic wrap-around (e.g. diff between 23 and 0 is 1 hour)
            h_diff = abs(current_hour - s["hour"])
            hour_dist = min(h_diff, 24 - h_diff)
            
            # 2. Temperature distance
            temp_dist = abs(current_temp - s["temperature"])
            
            # 3. Weather distance (categorical)
            weather_dist = 0.0 if current_weather == s["weather"] else 2.0
            
            # Weighted total distance (lower distance = higher similarity)
            # Weather and Hour have higher weights since they dictate solar/wind/base loads
            total_dist = (hour_dist * 0.6) + (temp_dist * 0.25) + (weather_dist * 1.5)
            
            scored_scenarios.append((total_dist, s))
        
        # Sort by distance ascending
        scored_scenarios.sort(key=lambda x: x[0])
        
        # Return top k scenarios
        return [s for _, s in scored_scenarios[:k]]
