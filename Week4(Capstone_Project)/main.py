import sys
import os
import time

# Ensure current directory is on sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_store import RAGStore
from grid_balancer.simulator import GridSimulator
from grid_balancer.graph import create_grid_balancer_graph

def print_telemetry_table(title, telemetry):
    """Prints a beautiful summary table of grid telemetry in the terminal."""
    print("=" * 70)
    print(f" {title.upper()} ")
    print("=" * 70)
    print(f" Status:        {telemetry['status']:<15} | Frequency:    {telemetry['frequency_hz']} Hz")
    print(f" Generation:    {telemetry['generation']:<15} MW | Demand:       {telemetry['demand']} MW")
    print(f" Net Imbalance: {telemetry['net_imbalance']:<15} MW")
    print("-" * 70)
    print(f" Nodes Detail:")
    for name, node in telemetry["nodes"].items():
        type_str = f"({node['node_type']})"
        output_val = node["current_output"]
        cap_val = node["max_capacity"]
        
        # Format batteries with state of charge
        extra = ""
        if node["node_type"] == "battery":
            extra = f" | SoC: {int(node['soc']*100)}% ({node['charge_level_mwh']} MWh)"
            
        print(f"  - {name:<20} {type_str:<22} : {output_val:>6} / {cap_val} MW{extra}")
    print("=" * 70)


def run_aegb_simulation():
    print("\n" + "#" * 80)
    print("       AUTONOMOUS ENERGY GRID BALANCER (AEGB) - MULTI-AGENT SIMULATION")
    print("#" * 80 + "\n")
    
    # 1. Initialize local Case-Based RAG store
    rag = RAGStore()
    if not rag.scenarios:
        rag.seed_default_scenarios()
    else:
        print(f"Loaded {len(rag.scenarios)} historical cases from RAG store.")

    # 2. Initialize Simulator & Graph
    simulator = GridSimulator()
    graph = create_grid_balancer_graph()
    
    # 3. Simulate a 12-hour sequence with changing weather and loads
    # Hour, Temperature, Weather conditions
    simulation_schedule = [
        # (Hour, Temperature, Weather)
        (8,  14.0, "cloudy"),  # Morning startup, cloudy
        (9,  16.0, "sunny"),   # Solar starts kicking in
        (10, 20.0, "sunny"),   # Sunny morning
        (11, 24.0, "sunny"),   # Sunny midday
        (12, 28.0, "sunny"),   # Noon peak temperature
        (13, 31.0, "sunny"),   # Early afternoon hot sunny
        (14, 34.0, "sunny"),   # Hot summer peak demand
        (15, 33.0, "sunny"),   # Still hot
        (16, 29.0, "cloudy"),  # Clouds roll in, solar drops
        (17, 26.0, "windy"),   # Wind picks up
        (18, 22.0, "windy"),   # Evening residential surge begins
        (19, 18.0, "stormy"),  # Evening storm hits, peak demand
    ]
    
    for idx, (hour, temp, weather) in enumerate(simulation_schedule):
        print(f"\n\n>>> TIME STEP {idx + 1}/12: {hour:02d}:00 | TEMP: {temp}°C | WEATHER: {weather.upper()}")
        
        # A. Get initial unbalanced telemetry
        initial_telemetry = simulator.get_telemetry(hour, temp, weather)
        print_telemetry_table("Telemetry Before Rebalancing", initial_telemetry)
        
        # B. Retrieve historical analogues (RAG)
        # Find 2 historical cases with closest environmental and demand parameters
        historical_cases = rag.similarity_search(hour, temp, weather, k=2)
        
        # C. Formulate initial AgentState
        initial_state = {
            "telemetry": initial_telemetry,
            "historical_cases": historical_cases,
            "forecast": {},
            "recommendations": {},
            "messages": [],
            "next_agent": ""
        }
        
        # D. Run the Supervisor agent Graph
        print("=== MULTI-AGENT REBALANCING WORKFLOW ACTIVATED ===")
        final_state = graph.invoke(initial_state)
        
        # E. Extract optimizer adjustments and apply them
        recommendations = final_state.get("recommendations", {})
        balanced_telemetry = simulator.apply_balancing(recommendations)
        
        # F. Print balanced telemetry
        print_telemetry_table("Telemetry After Rebalancing", balanced_telemetry)
        
        # Short pause between steps to simulate real-time operations
        time.sleep(1.0)
        
    print("\n" + "=" * 80)
    print("                      SIMULATION SEQUENCE COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_aegb_simulation()
