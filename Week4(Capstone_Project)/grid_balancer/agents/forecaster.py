from langchain_core.messages import AIMessage
from grid_balancer.state import AgentState

def forecaster_agent(state: AgentState):
    """
    Forecaster Agent node.
    Uses current telemetry and retrieved historical RAG cases to predict power load and generation.
    """
    telemetry = state.get("telemetry", {})
    historical_cases = state.get("historical_cases", [])
    
    current_hour = telemetry.get("hour", 0)
    current_temp = telemetry.get("temperature", 20.0)
    current_weather = telemetry.get("weather", "sunny")
    
    # 1. Synthesize the RAG historical cases
    summary_scenarios = []
    avg_residential = 0.0
    avg_industrial = 0.0
    avg_solar = 0.0
    avg_wind = 0.0
    
    if historical_cases:
        for case in historical_cases:
            summary_scenarios.append(f"'{case['scenario_name']}' (Hour {case['hour']}, Temp {case['temperature']}°C, Weather '{case['weather']}')")
            # Accumulate values
            avg_residential += abs(case.get("residential_load", 0.0))
            avg_industrial += abs(case.get("industrial_load", 0.0))
            avg_solar += case.get("solar_output", 0.0)
            avg_wind += case.get("wind_output", 0.0)
            
        avg_residential /= len(historical_cases)
        avg_industrial /= len(historical_cases)
        avg_solar /= len(historical_cases)
        avg_wind /= len(historical_cases)
    else:
        # Fallback to simple heuristics based on current values if no RAG data exists
        nodes = telemetry.get("nodes", {})
        avg_residential = abs(nodes.get("Residential_Area_C", {}).get("current_output", 60.0))
        avg_industrial = abs(nodes.get("Industrial_Zone_D", {}).get("current_output", 80.0))
        avg_solar = nodes.get("Solar_Farm_A", {}).get("current_output", 0.0)
        avg_wind = nodes.get("Wind_Farm_B", {}).get("current_output", 0.0)

    # 2. Refine predictions based on current conditions
    # For example, if temperature increases, cooling load goes up relative to the historical average
    temp_adjust_factor = 1.0
    if current_temp > 30.0:
        temp_adjust_factor += (current_temp - 30.0) * 0.02
    elif current_temp < 10.0:
        temp_adjust_factor += (10.0 - current_temp) * 0.03
        
    predicted_res = round(avg_residential * temp_adjust_factor, 2)
    predicted_ind = round(avg_industrial, 2)
    predicted_solar = round(avg_solar, 2)
    predicted_wind = round(avg_wind, 2)
    
    predicted_demand = round(predicted_res + predicted_ind, 2)
    # Fossil plant minimum stable output is 30MW, which is our baseline generation
    predicted_generation = round(predicted_solar + predicted_wind + 30.0, 2)
    predicted_imbalance = round(predicted_generation - predicted_demand, 2)
    
    # 3. Write detailed agent reasoning
    scenarios_str = " | ".join(summary_scenarios)
    reasoning = (
        f"Forecaster prediction for next-hour based on RAG cases: [{scenarios_str}]:\n"
        f"  - Predicted Solar Output: {predicted_solar} MW\n"
        f"  - Predicted Wind Output: {predicted_wind} MW\n"
        f"  - Predicted Residential Demand: {predicted_res} MW\n"
        f"  - Predicted Industrial Demand: {predicted_ind} MW\n"
        f"  - Predicted Total Demand: {predicted_demand} MW | Predicted Base Generation: {predicted_generation} MW\n"
        f"  - Net Predicted Imbalance before optimization: {predicted_imbalance} MW (Deficit of {abs(predicted_imbalance)} MW)"
        if predicted_imbalance < 0 else
        f"  - Net Predicted Imbalance before optimization: {predicted_imbalance} MW (Surplus of {predicted_imbalance} MW)"
    )
    
    print(f"[Forecaster Agent]: {reasoning}")
    
    # Append AIMessage
    new_messages = list(state.get("messages", []))
    new_messages.append(AIMessage(content=reasoning, name="Forecaster"))
    
    forecast_data = {
        "predicted_solar": predicted_solar,
        "predicted_wind": predicted_wind,
        "predicted_residential_demand": predicted_res,
        "predicted_industrial_demand": predicted_ind,
        "predicted_demand": predicted_demand,
        "predicted_generation": predicted_generation,
        "predicted_imbalance": predicted_imbalance
    }
    
    return {
        "messages": new_messages,
        "forecast": forecast_data
    }
