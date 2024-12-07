from map_graph import *
from navigation import *

GEOTAB_data = {
    "spring": {40: 98.2, 70: 84.8, 100: 68.4},
    "summer": {40: 78.5, 70: 75.5, 100: 64.0},
    "fall": {40: 78.5, 70: 75.5, 100: 64.0},
    "winter": {40: 60.5, 70: 64.8, 100: 52.8}
}
# Data retrived from GEOTAB's "Impact of temperature and speed on EV range" model
# https://www.geotab.com/blog/ev-range-impact-of-speed-and-temperature/

class EVehicle:
    def __init__(self, start_id, dest_id, capacity, SOC, efficiency):
        """
        Initialize an Electric Vehicle (EV) object.
        
        Parameters:
            start_id (int): Starting node ID.
            dest_id (int): Destination node ID.
            cur_id (int): Current reaching node ID.
            to_cur (float): Distance traveled to the current node in km.
            capacity (float): Battery capacity in kWh.
            SOC (float): State of Charge of the battery in percentage (0-100).
            efficiency (float): Energy efficiency of the EV in kWh per km.
        """
        self._start_id = start_id
        self._dest_id = dest_id
        self._cur_id = -1
        self._to_cur = -1.0
        self._capacity = capacity
        self._SOC = SOC
        self._efficiency = efficiency

    @property
    def start_id(self):
        """Starting node ID."""
        return self._start_id

    @property
    def dest_id(self):
        """Destination node ID."""
        return self._dest_id

    @property
    def cur_id(self):
        """Current node ID."""
        return self._cur_id

    @property
    def to_cur(self):
        """Distance traveled to the current node in km."""
        return self._to_cur

    @property
    def capacity(self):
        """Battery capacity in kWh."""
        return self._capacity

    @property
    def SOC(self):
        """State of Charge of the battery in percentage (0-100)."""
        return self._SOC

    @property
    def efficiency(self):
        """Energy efficiency of the EV in kWh per km."""
        return self._efficiency

    def drive(self, distance, season, speed):
        """
        Simulates the EV driving a certain distance and updates its state of charge (SOC).
        If the vehicle reaches an intersection, stop driving.
        
        Parameters:
            distance (float): Distance traveled in kilometers.
            season (str): Season affecting energy consumption.
            speed (int): Speed of the vehicle in km/h.

        Updates:
            - Decreases `to_cur` by the traveled distance.
            - Updates `SOC` based on energy consumption, which is influenced by the season and speed.

        Returns: 
            exceed (float): The remaining driving distance.
        """
        if self._to_cur > distance:
            self._to_cur -= distance

            exceed = 0
        else:
            self._to_cur = 0
            exceed = distance - self._to_cur

        impact_index = GEOTAB_data[season][speed]
        consumption = distance * self._efficiency * impact_index
        self._SOC = (self._SOC * self._capacity - consumption) / self.capacity
        return exceed
    
    def redirect(self, next_node, distance):
        """
        Updates the vehicle's current location and distance to the next node.
        
        This method is used when the vehicle is redirected to a new node or intersection, 
        updating its current location and the distance to the next target node. 
        
        Parameters:
            next_node (int): The ID of the next node the vehicle is heading towards.
            distance (float): The distance to the next node in kilometers.
        
        Updates:
            - `cur_id` to reflect the new current node.
            - `to_cur` to store the distance to the next node.
        
        Returns:
            int: The updated current node ID.
        """
        self._cur_id = next_node
        self._to_cur = distance
        return self._cur_id
    
    def check_reachable(self, season, nodes, dest, roads, t):
        # Prevent battery from instant shut off
        if t < 5:
            t = 5
            
        cur_SOC = self._SOC

        path = fastest_path(nodes, nodes.get_node(self.cur_id), dest)

        for i in range(len(path) - 1):
            road = select_road(path[i], path[i+1], roads)
            impact_index = GEOTAB_data[season][road.speed_limit]
            consumption = road.distance * self._efficiency * impact_index
            cur_SOC = (cur_SOC * self._capacity - consumption) / self.capacity
            if cur_SOC < t:
                return 0

        return 1
    
    def charge(self, target):
        self._SOC = target
        return
    
    
    def optimal_SOC(self, season, nodes, dest, roads, t):
        target = self.SOC + t

        path = fastest_path(nodes, nodes.get_node(self.cur_id), dest)

        for i in range(len(path) - 1):
            road = select_road(path[i], path[i+1], roads)
            impact_index = GEOTAB_data[season][road.speed_limit]
            consumption = road.distance * self._efficiency * impact_index
            target = (target * self._capacity + consumption) / self.capacity

        # Prevent battery from instant shut off by giving it 5% extra
        return target + 5