"""
- Receive request from the user
	- Request should have the user information
- Fetch energy data for 1 year for that user from the Energy Data Aggregator
- Perform the forecast for the next 3 months (maximum)
- Calculate the cost/profit for the energy consumption/production
- Send a response with the estimated cost/profit to the user
"""
from datetime import date

import json
import paho.mqtt.client as mqtt
import pickle


class PredictiveAnalyticsService:
    """
    A class to forecast the individual electricity consumption and production.

    Parameters:
            broker_name (string): Address for MQTT broker.
            model_path (string): Path to the weights for the forecasting model.
    """

    def __init__(self, broker_name, model_path):
        # Initialize the MQTT Client
        self.client = mqtt.Client()
        self.client.connect(broker_name, 1883)

        self.consumption_data = None
        self.production_data = None

        self.consumption_forecast = None
        self.production_forecast = None

        # Loading the best model weights
        self.model_path = model_path

        with open(self.model_path, 'r') as f:
            self.model = pickle.load(f)

    def forecast_energy_consumption(self, consumption_data, start_date, end_date):
        # Set the energy consumption of the individual user
        self.consumption_data = consumption_data

        # Forecast energy consumption
        self.consumption_forecast = self.model.predict(
            start=start_date, end=end_date).to_frame()

        return self.consumption_forecast

    def forecast_energy_production(self, production_data, start_date, end_date):
        # Set the energy production of the individual user
        self.production_data = production_data

        # Forecast energy production
        self.production_forecast = self.model.predict(
            start=start_date, end=end_date).to_frame()

        return self.production_forecast

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        """The callback for when the client receives a CONNACK response from the server."""
        print("Connected with result code " + str(rc))

        client.subscribe("energy/aggregate/consumption_history")
        client.subscribe("energy/aggregate/production_history")

    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        print("Topic: " + msg.topic + "\n")

        if msg.topic == "energy/aggregate/consumption":
            self.consumption_data = json.loads(msg.payload)
            print(self.consumption_data)
        elif msg.topic == "energy/aggregate/production":
            self.production_data = json.loads(msg.payload)
            print(self.production_data)

        date_now = date.today()
        years_to_add = date_now.year + 1

        start_date = date_now.strftime("%Y-%m-%d")
        end_date = date_now.replace(year=years_to_add).strftime("%Y-%m-%d")

        if self.consumption_data is not None:
            self.forecast_energy_consumption(
                self.consumption_data, start_date, end_date)
            self.publish_consumption_forecast()

        if self.production_data is not None:
            self.forecast_energy_production(
                self.production_data, start_date, end_date)
            self.publish_production_forecast()

    def publish_consumption_forecast(self):
        """Publish the energy consumption forecast data."""
        self.client.publish("energy/household1/consumption",
                            json.dumps({"forecast": self.consumption_forecast}))

    def publish_production_forecast(self):
        """Publish the energy production forecast data."""
        self.client.publish("energy/household1/production",
                            json.dumps({"forecast": self.production_forecast}))

    def start(self):
        """Start the Predictive Analytics Service."""
        # Set the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.loop_forever()


if __name__ == "__main__":
    # Define the path to the best forecasting model weights
    MODEL_PATH = "./best_model.pkl"

    # Create an instance of the class
    predictive_analytics_service = PredictiveAnalyticsService(
        broker_name="mqtt_broker",
        model_path=MODEL_PATH
    )

    # Start the Predictive Analytics Service
    predictive_analytics_service.start()
