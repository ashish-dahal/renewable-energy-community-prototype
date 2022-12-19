import random
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import json


class EnergyDataAggregator:
    '''
    A class to simulate the electricity consumption and generation of a household.

    Parameters:
        consumption_rate (float): the average electricity consumption in kWh
        production_rate (float): the average electricity generation in kWh
        consumption_fluctuation (float): the fluctuation of the electricity consumption in kWh
        production_fluctuation (float): the fluctuation of the electricity generation in kWh
        interval (timedelta): the interval between each measurement in days
    '''

    def __init__(self, consumption_rate, production_rate, consumption_fluctuation, production_fluctuation, interval):
        self.consumption_rate = consumption_rate
        self.production_rate = production_rate
        self.consumption_fluctuation = consumption_fluctuation
        self.production_fluctuation = production_fluctuation
        self.interval = interval
        # initialize the mqtt client
        self.client = mqtt.Client()

        # connect to the mqtt broker
        # self.client.connect('broker.hive.mq', 1883)

    def simulate_electricity_consumption(self):
        '''Simulate the total electricity consumption for past year.'''
        # Set the initial electricity consumption in kWh
        electricity_consumed = 0

        # Set the initial electricity generation in kWh
        consumption_data = []

        # Loop for 365 days
        for i in range(366):
            # Calculate the daily electricity consumption
            electricity_consumed = self.consumption_rate + \
                random.uniform(0, self.consumption_fluctuation)
            consumption_data.append(electricity_consumed)

        return consumption_data

    def simulate_electricity_production(self):
        '''Simulate the total electricity production for past year.'''
        # Set the initial electricity production in kWh
        electricity_produced = 0

        # Set the initial electricity generation in kWh
        production_data = []

        # Loop for 365 days
        for i in range(366):
            # Calculate the daily electricity production
            electricity_produced = self.production_rate + \
                random.uniform(0, self.production_fluctuation)
            production_data.append(electricity_produced)

        return production_data

    def get_datetime_range(self) -> list:
        '''Get a list of datetime objects for each interval in the last year.'''
        # get the current datetime
        now = datetime.now()

        # calculate the datetime one year ago
        one_year_ago = now - self.interval

        # initialize the result list with the datetime one year ago
        result = [one_year_ago]

        # initialize a variable to keep track of the current datetime
        current = one_year_ago

        # loop until the current datetime is the same as the current datetime
        while current < now:
            # add the interval to the current datetime
            current += self.interval

            # append the current datetime to the result list
            result.append(current)

        return result

    # publish to mqtt
    def publish_data(self, topic, message):
        '''Publish the aggregate electricity consumption and prodution to an MQTT broker.'''
        self.client.publish(topic, message)

    def start(self):
        '''Start the energy data aggregator'''
        for i in range(100):
            # get the timestamps for the last year
            timestamps = self.get_datetime_range()

            # simulate the electricity consumption
            consumption_data = self.simulate_electricity_consumption()

            # simulate the electricity production
            production_data = self.simulate_electricity_production()

            # create a dictionary with the timestamps and consumption data
            consumption_data = json.dumps({"timestamps": timestamps,
                                           "consumption": consumption_data})

            # create a dictionary with the timestamps and production data
            production_data = json.dumps({"timestamps": timestamps,
                                          "production": production_data})

            # # publish the consumption data to the mqtt broker
            # self.publish_data("energy/consumption", consumption_data)

            # # publish the production data to the mqtt broker
            # self.publish_data("energy/production", production_data)


if __name__ == "__main__":
    # create an instance of the class
    energy_data_aggregator = EnergyDataAggregator(
        consumption_rate=10,
        production_rate=5,
        consumption_fluctuation=2,
        production_fluctuation=1,
        interval=timedelta(days=1),
    )

    # start the energy data aggregator
    energy_data_aggregator.start()
