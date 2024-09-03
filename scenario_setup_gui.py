import tkinter as tk
from tkinter import ttk

from setup_carla import *
# Initialize the main window
root = tk.Tk()
root.title("ScenarioInfoManager")
root.geometry("600x500")  # Set the window size

# Default values for each field
default_values = {
    "road_type": "Motorway",
    "ego_vehicle_position": "Traffic Lane",
    "emv_position": "Same Road",
    "emv_direction": "Approaches from Behind",
    "weather_condition": "Clear",
    "time_of_day": "Day time",
    "safety_distance": "0",
}

# Dictionary to store previous values of comboboxes and spinbox
scenario_info = default_values.copy()

# Define the options for each combobox
road_type_options = ["Motorway", "Expressway"]
ego_vehicle_position_options = ["Traffic Lane", "Approaching Intersection"]
emv_position_options = ["Same Road", "Parallel Road", "Opposite Road", "Cross Road"]
emv_direction_options = ["Approaches from Behind", "As Lead Vehicle", "Approaches from Right Lane", "Approaches from Left Lane", "Approaches on Opposite Lane", 
                         "Approaches Intersection"]
weather_options = ["Clear", "Cloudy", "Light Rain", "Moderate Rain", "Heavy Rain"]
time_of_day_options = ["Day time", "Night time"]
    
def map_scenario_for_motorway_same_lane_and_parallel_lane(scenario_info):
    if scenario_info["road_type"] == "Motorway" and scenario_info["ego_vehicle_position"] == "Traffic Lane":
            if  scenario_info["emv_position"] == "Same Road":
                if  scenario_info["emv_direction"] == "Approaches from Behind":
                    change_emv_vehicle_spawn_point(231)
                elif  scenario_info["emv_direction"] == "As Lead Vehicle":
                    change_emv_vehicle_spawn_point(37)
            elif scenario_info["emv_position"] == "Parallel Road":
                if  scenario_info["emv_direction"] == "Approaches from Behind":
                    change_emv_vehicle_spawn_point(230)
                elif  scenario_info["emv_direction"] == "As Lead Vehicle":
                    change_emv_vehicle_spawn_point(38)
        

# Function to handle the Start Simulation button click
def start_simulation():
    
    connect_to_carla()
    
    spawn_ego_vehicle()
    
    spawn_emergency_vehicle()
    
    set_spectator()
            
def clean_up_environment():
    destroy_ego_vehicle()
    destroy_emv_vehicle()
    road_type_cb.set(default_values["road_type"])
    ego_vehicle_position_cb.set(default_values["ego_vehicle_position"])
    emv_position_cb.set(default_values["emv_position"])
    emv_direction_cb.set(default_values["emv_direction"])

# Function to handle value changes in comboboxes
def on_combobox_road_type_change(event, combobox_name):
    current_value = event.widget.get()  
    if current_value != scenario_info[combobox_name]:
        print(f"{combobox_name} changed to {current_value}")
        scenario_info[combobox_name] = current_value 
        
# Function to handle value changes in comboboxes
def on_combobox_ego_position_change(event, combobox_name):
    current_value = event.widget.get()  
    if current_value != scenario_info[combobox_name]:
        print(f"{combobox_name} changed to {current_value}")
        scenario_info[combobox_name] = current_value
        
        if scenario_info["road_type"] == "Motorway":
            if scenario_info[combobox_name] == "Traffic Lane":
                change_ego_vehicle_spawn_point(41)
            elif  scenario_info[combobox_name] == "Approaching Intersection":
                change_ego_vehicle_spawn_point(38)
        
# Function to handle value changes in comboboxes
def on_combobox_emv_position_change(event, combobox_name):
    current_value = event.widget.get()  
    if current_value != scenario_info[combobox_name]:
        print(f"{combobox_name} changed to {current_value}")
        scenario_info[combobox_name] = current_value
        # emv_direction_cb.set("Approaches from Behind")
        # scenario_info["emv_direction"] = "Approaches from Behind"
        
        map_scenario_for_motorway_same_lane_and_parallel_lane(scenario_info)
            
                    
# Function to handle value changes in comboboxes
def on_combobox_emv_direction_change(event, combobox_name):
    current_value = event.widget.get()
    print("scenario_info[combobox_name]", scenario_info[combobox_name])
    if current_value != scenario_info[combobox_name]:
        print(f"{combobox_name} changed to {current_value}")
        scenario_info[combobox_name] = current_value
        
        map_scenario_for_motorway_same_lane_and_parallel_lane(scenario_info)
        

# Define a larger font
large_font = ("Helvetica", 14)

# Create and place the widgets
ttk.Label(root, text="Road Type", font=large_font).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
road_type_cb = ttk.Combobox(root, values=road_type_options, state="readonly", font=large_font)
road_type_cb.set(default_values["road_type"])
road_type_cb.grid(row=0, column=1, padx=20, pady=10)
road_type_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_road_type_change(event, "road_type"))

ttk.Label(root, text="Ego Vehicle Position", font=large_font).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
ego_vehicle_position_cb = ttk.Combobox(root, values=ego_vehicle_position_options, state="readonly", font=large_font)
ego_vehicle_position_cb.set(default_values["ego_vehicle_position"])
ego_vehicle_position_cb.grid(row=1, column=1, padx=20, pady=10)
ego_vehicle_position_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_ego_position_change(event, "ego_vehicle_position"))

ttk.Label(root, text="Emergency Vehicle Position", font=large_font).grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
emv_position_cb = ttk.Combobox(root, values=emv_position_options, state="readonly", font=large_font)
emv_position_cb.set(default_values["emv_position"])
emv_position_cb.grid(row=2, column=1, padx=20, pady=10)
emv_position_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_emv_position_change(event, "emv_position"))

ttk.Label(root, text="EMV Travel Direction", font=large_font).grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
emv_direction_cb = ttk.Combobox(root, values=emv_direction_options, state="readonly", font=large_font)
emv_direction_cb.set(default_values["emv_direction"])
emv_direction_cb.grid(row=3, column=1, padx=20, pady=10)
emv_direction_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_emv_direction_change(event, "emv_direction"))

ttk.Label(root, text="Weather Condition", font=large_font).grid(row=4, column=0, padx=20, pady=10, sticky=tk.W)
weather_cb = ttk.Combobox(root, values=weather_options, state="readonly", font=large_font)
weather_cb.set(default_values["weather_condition"])
weather_cb.grid(row=4, column=1, padx=20, pady=10)
weather_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_weather_change(event, "weather_condition"))

ttk.Label(root, text="Time of Day", font=large_font).grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)
time_of_day_cb = ttk.Combobox(root, values=time_of_day_options, state="readonly", font=large_font)
time_of_day_cb.set(default_values["time_of_day"])
time_of_day_cb.grid(row=5, column=1, padx=20, pady=10)
time_of_day_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_day_time_change(event, "time_of_day"))

ttk.Label(root, text="Safety Distance (m)", font=large_font).grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)
safety_distance_sb = tk.Spinbox(root, from_=0, to=100, increment=1, font=large_font)
safety_distance_sb.grid(row=6, column=1, padx=20, pady=10)

start_button = ttk.Button(root, text="Start Simulation", command=start_simulation, style='TButton')
start_button.grid(row=7, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

setup_button = ttk.Button(root, text="Clean Up Environment", command=clean_up_environment, style='TButton')
setup_button.grid(row=8, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)

# Start the main event loop
root.mainloop()
