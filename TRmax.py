def TRmax(to_CS, queue_time, charge_time, to_dest):
    """
    The total estimated travel time (TRmax) to complete a route via a charging station.

    Parameters:
        to_CS (float): Travel time to the charging station (in minutes).
        queue_time (float): Time spent waiting in the queue at the charging station (in minutes).
        charge_time (float): Time required to charge the vehicle at the charging station (in minutes).
        to_dest (float): Travel time from the charging station to the destination (in minutes).

    Returns:
        float: Total estimated travel time (TRmax) in minutes.
    
    Formula:
        TRmax = to_CS + queue_time + charge_time + to_dest
    """
    TRmax = to_CS + queue_time + charge_time + to_dest
    return TRmax