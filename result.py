class result:
    def __init__(self):
        self._initial_path = []
        self._distance_adjust = 0
        self._season = ""
        self._target_percentage = 0
        self._threshold = 0
        self._model = 0

        self._travel_history = []
        self._trmax_history = []
        self._station_history = []
        self._ev_history = []
    
    # Getters and Setters for attributes
    @property
    def initial_path(self):
        """Gets the initial path."""
        return self._initial_path

    @initial_path.setter
    def initial_path(self, path):
        """Sets the initial path."""
        self._initial_path = path

    @property
    def distance_adjust(self):
        """Gets the distance adjustment."""
        return self._distance_adjust

    @distance_adjust.setter
    def distance_adjust(self, adjustment):
        """Sets the distance adjustment."""
        self._distance_adjust = adjustment

    @property
    def season(self):
        """Gets the season."""
        return self._season

    @season.setter
    def season(self, season):
        """Sets the season."""
        self._season = season

    @property
    def target_percentage(self):
        """Gets the target percentage."""
        return self._target_percentage

    @target_percentage.setter
    def target_percentage(self, percentage):
        """Sets the target percentage."""
        self._target_percentage = percentage

    @property
    def threshold(self):
        """Gets the threshold."""
        return self._threshold

    @threshold.setter
    def threshold(self, threshold):
        """Sets the threshold."""
        self._threshold = threshold

    @property
    def model(self):
        """Gets the model."""
        return self._model

    @model.setter
    def model(self, model):
        """Sets the model."""
        self._model = model

    @property
    def travel_history(self):
        """Gets the travel history."""
        return self._travel_history

    def add_travel_history(self, travel_data):
        """Adds a travel history entry."""
        self._travel_history.append(travel_data)

    @property
    def trmax_history(self):
        """Gets the TRmax history."""
        return self._trmax_history

    def add_trmax_history(self, trmax_data):
        """Adds a TRmax history entry."""
        self._trmax_history.append(trmax_data)

    @property
    def station_history(self):
        """Gets the station history."""
        return self._station_history

    def add_station_history(self, station_data):
        """Adds a station history entry."""
        self._station_history.append(station_data)

    @property
    def ev_history(self):
        """Gets the EV history."""
        return self._ev_history

    def add_ev_history(self, ev_data):
        """Adds an EV history entry."""
        self._ev_history.append(ev_data)

    def summarize(self):
        """Prints a summary of the current results in a readable format."""
        print(f"""
        Simulation Summary:
        -------------------
        Initial Path: {self._initial_path}
        Distance Adjustment Factor: {self._distance_adjust}
        Season: {self._season.capitalize()}
        Target SOC Percentage: {self._target_percentage}%
        SOC Threshold: {self._threshold}%
        Model Used: {"Original Paper" if self._model == 0 else "Proposed Method"}
        
        Travel History:
        {self._format_history(self._travel_history, "Travel")}
        
        TRmax History:
        {self._format_history(self._trmax_history, "TRmax")}
        
        Station History:
        {self._format_history(self._station_history, "Station")}
        
        EV History:
        {self._format_history(self._ev_history, "EV")}
        """.strip())

    def _format_history(self, history, title):
        """
        Helper method to format history lists for better readability.
        
        Parameters:
            history (list): The history list to format.
            title (str): The title of the history section.
        
        Returns:
            str: Formatted history section as a string.
        """
        if not history:
            return f"{title} history is empty."

        formatted = "\n".join([f"  - {item}" for item in history])
        return formatted
