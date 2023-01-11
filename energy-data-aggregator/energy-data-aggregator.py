import random
from datetime import datetime, timedelta
from time import sleep
from dateutil.relativedelta import relativedelta
import paho.mqtt.client as mqtt
import json


class EnergyDataAggregator:
    '''
    A class to simulate the electricity consumption and production households in the community.

    Parameters:
        n_households (int): number of households in the community
        consumption_rate (float): the average electricity consumption in kWh
        production_rate (float): the average electricity production in kWh
        consumption_fluctuation (float): the fluctuation of the electricity consumption in kWh
        production_fluctuation (float): the fluctuation of the electricity production in kWh
        interval (timedelta): the interval between each measurement in days
        publish_frequency (int): the frequency of data publishing data to mqtt broker in seconds
        broker_address (string): thr address of the mqtt broker

    '''

    def __init__(self, n_households, consumption_fluctuation, production_fluctuation, interval, publish_frequency, broker_address):
        self.n_households = n_households
        self.consumption_fluctuation = random.uniform(
            0, consumption_fluctuation)
        self.production_fluctuation = random.uniform(
            0, production_fluctuation)
        self.interval = interval
        self.publish_frequency = publish_frequency

        # get the timestamps for the past year
        self.timestamps = self.get_timestamps()

        # simulate the electricity consumption for past year
        self.consumption_data = self.simulate_electricity_consumption()

        # simulate the electricity production for past year
        self.production_data = self.simulate_electricity_production()

        # simulate the aggregate electricity production for the past year
        self.aggregate_consumption_history = [
            self.__get_electricity_quantity()*self.n_households for i in range(366)]

        # simulate the aggregate electricity consumption for the past year
        self.aggregate_production_history = [
            self.__get_electricity_quantity()*self.n_households for i in range(366)]

        # initialize the mqtt client
        self.client = mqtt.Client()

        # connect to the mqtt broker
        self.client.connect(broker_address, 1883)

    def simulate_electricity_consumption(self):
        '''Simulate the electricity consumption for a single household the for a year'''
        # Set the initial electricity consumption in kWh
        electricity_consumed = 0

        # Set the initial electricity consumption in kWh
        consumption_data = []

        # Loop for 365 days
        for i in range(366):
            # Calculate the daily electricity consumption
            electricity_consumed = self.__get_electricity_quantity()
            consumption_data.append(electricity_consumed)

        return consumption_data

    def simulate_electricity_production(self):
        '''Simulate the electricity production for a single household the for a year'''
        # Set the initial electricity production in kWh
        electricity_produced = 0

        # Set the initial electricity production in kWh
        production_data = []

        # Loop for 365 days
        for i in range(366):
            # Calculate the daily electricity production
            electricity_produced = self.__get_electricity_quantity()
            production_data.append(electricity_produced)

        return production_data

    def __get_electricity_quantity(self):
        '''Get the electricity quantity for a single household'''
        return random.uniform(0, self.production_fluctuation)

    def get_timestamps(self) -> list:
        '''Get a list of datetime objects for each interval in the last year.'''
        # get the current datetime
        now = datetime.now()

        # calculate the datetime one year ago
        one_year_ago = now - relativedelta(years=1)

        # initialize the result list with the datetime one year ago
        result = [str(one_year_ago)]

        # initialize a variable to keep track of the current datetime
        current = one_year_ago

        # loop until the current datetime is the same as the current datetime
        while current < now:
            # add the interval to the current datetime
            current += self.interval

            # append the current datetime to the result list
            result.append(str(current))

        return result

    def simulate_aggregate_electricity_production(self):
        '''Simulate the aggregate electricity production for n_households'''
        # initialize the aggregate electricity production
        aggregate_electricity_production = []

        # loop over the number of households
        for i in range(self.n_households):
            # simulate the electricity production for a single household
            electricity_production = self.__get_electricity_quantity()

            # add the electricity production to the aggregate electricity production
            aggregate_electricity_production.append(electricity_production)

        return aggregate_electricity_production
    # simulate aggregate electricity consumption for n_households

    def simulate_aggregate_electricity_consumption(self):
        '''Simulate the aggregate electricity consumption for n_households'''
        # initialize the aggregate electricity consumption
        aggregate_electricity_consumption = []

        # loop over the number of households
        for i in range(self.n_households):
            # simulate the electricity consumption for a single household
            electricity_consumption = self.__get_electricity_quantity()

            # add the electricity consumption to the aggregate electricity consumption
            aggregate_electricity_consumption.append(electricity_consumption)

        return aggregate_electricity_consumption

    # publish to mqtt
    def publish_data(self, topic, message):
        '''Publish the aggregate electricity consumption and prodution to an MQTT broker.'''
        self.client.publish(topic, message)

    def start(self):
        '''Start the energy data aggregator'''
        while True:

            # create a dictionary with the timestamps and consumption data
            consumption_data = json.dumps({"timestamps": self.timestamps,
                                           "consumption": self.consumption_data})

            # create a dictionary with the timestamps and production data
            production_data = json.dumps({"timestamps": self.timestamps,
                                          "production": self.production_data})

            # create a dictionary with the timestamps and aggregate consumption history
            aggregate_consumption_history = json.dumps(
                {"timestamps": self.timestamps, "consumption": self.aggregate_consumption_history})

            # create a dictionary with the timestamps and aggregate consumption history
            aggregate_production_history = json.dumps(
                {"timestamps": self.timestamps, "production": self.aggregate_production_history})

            # simulate the aggregate electricity production and consumption
            aggregate_production = self.simulate_aggregate_electricity_production()
            aggregate_consumption = self.simulate_aggregate_electricity_consumption()

            # publish the consumption data to the mqtt broker
            self.publish_data(
                "energy/household1/consumption", consumption_data)

            # publish the production data to the mqtt broker
            self.publish_data("energy/household1/production",
                              production_data)

            # publish the aggregate consumption data to the mqtt broker
            self.publish_data("energy/aggregate/consumption",
                              json.dumps(aggregate_consumption))

            # publish the aggregate production data to the mqtt broker
            self.publish_data("energy/aggregate/production",
                              json.dumps(aggregate_production))

            # publish the aggregate consumption history data to the mqtt broker
            self.publish_data("energy/aggregate/consumption_history",
                              json.dumps(aggregate_consumption_history))

            # publish the aggregate production history data to the mqtt broker
            self.publish_data("energy/aggregate/production_history",
                              json.dumps(aggregate_production_history))

            # publish in certain frequency
            sleep(self.publish_frequency)

            # add the real time electricity production and consumption
            self.timestamps.append(str(datetime.now()))
            self.production_data.append(self.__get_electricity_quantity())
            self.consumption_data.append(self.__get_electricity_quantity())
            self.aggregate_consumption_history.append(
                sum(aggregate_consumption))
            self.aggregate_production_history.append(
                sum(aggregate_production))


if __name__ == "__main__":
    # create an instance of the class
    energy_data_aggregator = EnergyDataAggregator(
        n_households=100,
        consumption_fluctuation=50,
        production_fluctuation=50,
        interval=timedelta(days=1),
        publish_frequency=5,
        broker_address="mqtt_broker"
    )
    # start the energy data aggregator
    energy_data_aggregator.start()
