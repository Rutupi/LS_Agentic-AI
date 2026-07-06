from langchain_core.messages import AIMessage
from grid_balancer.state import AgentState

def optimizer_agent(state: AgentState):
    """
    Optimizer Agent node.
    Calculates control adjustments to balance supply and demand based on telemetry and predictions.
    """
    telemetry = state.get("telemetry", {})
    forecast = state.get("forecast", {})
    
    # Extract node data from telemetry
    nodes = telemetry.get("nodes", {})
    
    # Target imbalance to solve is predicted_imbalance
    # If predicted_imbalance is negative, it's a deficit (demand > supply).
    # If positive, it's a surplus (supply > demand).
    imbalance = forecast.get("predicted_imbalance", 0.0)
    
    recommendations = {
        "Fossil_Fuel_Plant_E": 0.0,
        "Battery_Storage_F": 0.0,
        "Solar_Farm_A": 0.0,
        "Wind_Farm_B": 0.0,
        "Residential_Area_C": 0.0,
        "Industrial_Zone_D": 0.0
    }
    
    actions_taken = []
    
    # Battery Node metadata
    bat = nodes.get("Battery_Storage_F", {})
    bat_soc = bat.get("soc", 0.5)
    bat_max_cap = bat.get("max_capacity", 200.0)
    bat_max_power = bat.get("max_power", 60.0)
    bat_energy = bat_soc * bat_max_cap
    
    # Fossil Node metadata
    fossil = nodes.get("Fossil_Fuel_Plant_E", {})
    fossil_curr = fossil.get("current_output", 30.0)
    fossil_max = fossil.get("max_capacity", 150.0)
    fossil_min = 10.0  # Minimum stable generation
    
    if imbalance < 0:
        # DEFICIT: Ramping up supply or shedding load
        deficit = abs(imbalance)
        
        # 1. Ramped Fossil Fuel Generation
        fossil_room = fossil_max - fossil_curr
        if fossil_room > 0 and deficit > 0:
            fossil_ramp = min(deficit, fossil_room)
            recommendations["Fossil_Fuel_Plant_E"] = round(fossil_ramp, 2)
            deficit -= fossil_ramp
            actions_taken.append(f"Ramped up Fossil Fuel Plant by +{round(fossil_ramp, 1)} MW (Output: {round(fossil_curr + fossil_ramp, 1)}/{fossil_max} MW)")
            
        # 2. Discharge Battery Storage
        if deficit > 0 and bat_energy > 0:
            # We can discharge up to max battery power or available battery energy
            bat_discharge = min(deficit, bat_max_power, bat_energy)
            recommendations["Battery_Storage_F"] = round(bat_discharge, 2)
            deficit -= bat_discharge
            actions_taken.append(f"Discharged battery by +{round(bat_discharge, 1)} MW (SoC: {round((bat_energy - bat_discharge)/bat_max_cap*100, 1)}%)")
            
        # 3. Load Shedding (last resort)
        if deficit > 0:
            # Shed Industrial load first
            ind = nodes.get("Industrial_Zone_D", {})
            ind_load = abs(ind.get("current_output", 0.0))
            if ind_load > 0:
                ind_shed = min(deficit, ind_load)
                recommendations["Industrial_Zone_D"] = round(ind_shed, 2)
                deficit -= ind_shed
                actions_taken.append(f"CRITICAL: Shed Industrial load by {round(ind_shed, 1)} MW")
                
            # Shed Residential load if still deficit
            if deficit > 0:
                res = nodes.get("Residential_Area_C", {})
                res_load = abs(res.get("current_output", 0.0))
                if res_load > 0:
                    res_shed = min(deficit, res_load)
                    recommendations["Residential_Area_C"] = round(res_shed, 2)
                    deficit -= res_shed
                    actions_taken.append(f"CRITICAL: Shed Residential load by {round(res_shed, 1)} MW")
                    
    elif imbalance > 0:
        # SURPLUS: Absorbing, curtailing, or ramping down fossil fuel
        surplus = imbalance
        
        # 1. Charge Battery Storage
        bat_room = (1.0 - bat_soc) * bat_max_cap
        if surplus > 0 and bat_room > 0:
            # We can charge up to max power or available room
            bat_charge = min(surplus, bat_max_power, bat_room)
            # Charging is negative adjustment (consuming power)
            recommendations["Battery_Storage_F"] = -round(bat_charge, 2)
            surplus -= bat_charge
            actions_taken.append(f"Charged battery by {round(bat_charge, 1)} MW (SoC: {round((bat_energy + bat_charge)/bat_max_cap*100, 1)}%)")
            
        # 2. Ramp Down Fossil Fuel Generation
        fossil_excess = fossil_curr - fossil_min
        if surplus > 0 and fossil_excess > 0:
            fossil_cut = min(surplus, fossil_excess)
            recommendations["Fossil_Fuel_Plant_E"] = -round(fossil_cut, 2)
            surplus -= fossil_cut
            actions_taken.append(f"Ramped down Fossil Fuel Plant by -{round(fossil_cut, 1)} MW (Output: {round(fossil_curr - fossil_cut, 1)} MW)")
            
        # 3. Curtail Variable Generation (prevent grid frequency spikes)
        if surplus > 0:
            solar = nodes.get("Solar_Farm_A", {})
            solar_out = solar.get("current_output", 0.0)
            wind = nodes.get("Wind_Farm_B", {})
            wind_out = wind.get("current_output", 0.0)
            total_var = solar_out + wind_out
            
            if total_var > 0:
                solar_curtail = min(solar_out, surplus * (solar_out / total_var))
                wind_curtail = min(wind_out, surplus * (wind_out / total_var))
                
                recommendations["Solar_Farm_A"] = -round(solar_curtail, 2)
                recommendations["Wind_Farm_B"] = -round(wind_curtail, 2)
                surplus -= (solar_curtail + wind_curtail)
                
                actions_taken.append(f"Curtailed Solar by -{round(solar_curtail, 1)} MW and Wind by -{round(wind_curtail, 1)} MW")

    # Combine recommendations and actions
    actions_summary = "; ".join(actions_taken) if actions_taken else "Grid already balanced. No action taken."
    reasoning = (
        f"Optimizer finalized balancing recommendations:\n"
        f"  - Summary: {actions_summary}\n"
        f"  - Remaining Unbalanced Load: {round(deficit if imbalance < 0 else surplus, 2)} MW"
    )
    
    print(f"[Optimizer Agent]: {reasoning}")
    
    new_messages = list(state.get("messages", []))
    new_messages.append(AIMessage(content=reasoning, name="Optimizer"))
    
    return {
        "messages": new_messages,
        "recommendations": recommendations
    }
