import random

import vehicle

CHARGE_LEVEL = {
    2: {6.2},
    3: {50, 150}
}

class ChargingStationManager:
    def __init__(self, node, queue_time, expect_ev_rate, level):
        """
        Initialize a Charging Station Manager object.
        
        Parameters:
            id (int): Unique ID for the charging station.
            queue_time (float): Current queue time at the charging station in minutes.
            expect_ev_rate (float): Expected rate of EV arrivals (vehicles/hour).
            level (int): Charging station level (6.2, 50, 150) in kWh, numbers presumed according to google maps.
        """
        self._node = node
        self._queue_time = queue_time
        self._expect_ev_rate = expect_ev_rate
        self._level = level
        self._efficiency = random.choice(list(CHARGE_LEVEL[level]))
        self._occupy = random.choice([True, False])
        self._average_charge_time = 60/expect_ev_rate

    @property
    def node(self):
        """Unique ID for the charging station."""
        return self._node

    @property
    def queue_time(self):
        """Current queue time at the charging station in minutes."""
        return self._queue_time

    @property
    def expect_ev_rate(self):
        """Expected rate of EV arrivals (vehicles/hour)."""
        return self._expect_ev_rate

    @property
    def level(self):
        """Charging station level."""
        return self._level

    @property
    def occupy(self):
        return self._occupy

    def __repr__(self):
        """String representation of the Charging Station Manager."""
        return (
            f"CSM(node_id={self._node.id}, queue_time={self._queue_time} min, "
            f"expect_ev_rate={self._expect_ev_rate} vehicles/hour, level={self._level}"
        )
    
    def charge_time_check(self, car, target):
        """
        Calculates the charging time required to reach the target SOC, considering slower charging speed above 80%.

        Parameters:
            car (EVehicle): The electric vehicle object that needs charging.
            target (float): The target SOC percentage (0-100).

        Returns:
            float: The total charging time required in minutes.
        """
        # Prevent false charging
        if target <= car.SOC:
            return 0
        
        # Energy needed to reach 80% SOC (if target > 80%)
        if target > 80:
            energy_to_80 = car.capacity * (80 - car.SOC) / 100
            time_to_80 = energy_to_80 / self._efficiency * 60

            # Energy needed to charge from 80% to target will be charged slower
            energy_above_80 = car.capacity * (target - 80) / 100
            reduced_efficiency = self._efficiency * 0.5  # Assume 50% slower charging speed above 80%
            time_above_80 = energy_above_80 / reduced_efficiency * 60

            return time_to_80 + time_above_80
        else:
            # Energy needed to reach target SOC if target <= 80%
            energy_needed = car.capacity * (target - car.SOC) / 100
            return energy_needed / self._efficiency * 60

    
    def charge_car(self, car, target):
        car.charge(target)
        return
    
    def update(self, time):
        self._queue_time -= time
        if self._queue_time < 0:
            self._queue_time = 0
        vehicle_comes = random.randint(0, int(2 * self._expect_ev_rate * (time/60)))
        self._queue_time += self._average_charge_time * vehicle_comes
