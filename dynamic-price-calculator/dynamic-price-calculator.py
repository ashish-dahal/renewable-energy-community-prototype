from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import time
import random
import matplotlib.dates as mdates


class DynamicPriceCalculator:
    '''A class to calculate the optimal price for a electricity using the Nash Bargaining Solution.'''

    def __init__(self):

        # initialize the mqtt client
        self.client = mqtt.Client()

        # initialize the consumption and production of each consumer and producer
        self.consumer_consumption = None
        self.producer_production = None

        # initialize  the total consumption and production
        self.total_consumption = None
        self.total_production = None

        # initialize the price with the Nash Bargaining Solution
        self.price = 0

    def get_optimal_price(self, consumer_consumption, producer_production):
        '''Calculate the optimal price for a electricity using the Nash Bargaining Solution.

        Parameters:
            consumer_consumption (list): the consumption of each consumer in kWh
            producer_production (list): the production of each producer in kWh

        Returns: the optimal price in euros
        '''
        # set  the consumption and production of each consumer and producer
        self.consumer_consumption = consumer_consumption
        self.producer_production = producer_production

        # calculate the total consumption and production
        self.total_consumption = sum(consumer_consumption)
        self.total_production = sum(producer_production)

        # set the price with the Nash Bargaining Solution
        self.price = (self.total_consumption +
                      self.total_production) / (len(consumer_consumption) + len(producer_production))

        # iterate until convergence is reached (the price does not change anymore)
        while True:
            # calculate the utility for each consumer and producer
            consumer_utility = [consumption -
                                self.price for consumption in self.consumer_consumption]
            producer_utility = [
                self.price - production for production in self.producer_production]

            # calculate the maximum utility for each consumer and producer
            max_consumer_utility = max(consumer_utility)
            max_producer_utility = max(producer_utility)

            # calculate the new price using the Nash Bargaining Solution
            new_price = (max_consumer_utility + max_producer_utility) / 2

            # check for convergence
            if abs(new_price - self.price) < 1e-6:  # 1e-6 is the tolerance for convergence
                break

            # update the price
            self.price = new_price

            # check if the new price is negative
        if self.price < 0:
            self.price = 2
        # return the optimal price in euros
        return self.price/10

    # function to subscribe to get the consumption and production of each consumer and producer
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("consumption")
        client.subscribe("production")

    # function to receive the consumption and production of each consumer and producer
    def on_message(self, client, userdata, msg):
        print(msg.topic+": "+str(msg.payload))
        if msg.topic == "consumption":
            self.consumer_consumption = msg.payload
        elif msg.topic == "production":
            self.producer_production = msg.payload

        if self.consumer_consumption is not None and self.producer_production is not None:
            # calculate the optimal price
            self.get_optimal_price(
                self.consumer_consumption, self.producer_production)
            # publish the optimal price
            self.publish_price()

    # function to publish the optimal price
    def publish_price(self):
        self.client.publish("price", self.price)

    def start(self):
        # set the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # connect to the broker
        self.client.connect("mqtt_broker", 1883, 60)
        self.client.loop_forever()


def simulate_electricity_consumption(consumption_rate, generation_rate, consumption_fluctuation, generation_fluctuation, interval):
    # Set the initial electricity consumption in kWh
    electricity_consumed = 0

    consumption_data = []

    for i in range(366):
        # Calculate the daily electricity consumption
        electricity_consumed = consumption_rate + \
            random.uniform(0, consumption_fluctuation)
        consumption_data.append(electricity_consumed)

    return consumption_data


def get_datetime_range(interval: timedelta) -> list:
    # get the current datetime
    now = datetime.now()

    # calculate the datetime one year ago
    one_year_ago = now - timedelta(days=365)

    # initialize the result list with the datetime one year ago
    result = [one_year_ago]

    # initialize a variable to keep track of the current datetime
    current = one_year_ago

    # loop until the current datetime is the same as the current datetime
    while current < now:
        # add the interval to the current datetime
        current += interval

        # append the current datetime to the result list
        result.append(current)

    return result


if __name__ == "__main__":
    # create an instance of the class
    dynamic_price_calculator = DynamicPriceCalculator()

    # initialize the list of prices
    prices = []

    # get the timestamps for the last year
    timestamps = get_datetime_range(timedelta(days=1))

    # start the dynamic price calculator
    for i in range(366):
        # simulate the consumption and production of each consumer and producer
        con = simulate_electricity_consumption(4, 3, 0.5, 0.5, 1)
        prod = simulate_electricity_consumption(4, 3, 0.5, 0.5, 1)

        # calculate the optimal price
        prices.append(dynamic_price_calculator.get_optimal_price(con, prod))

    # print prices on matplotlib
    # import matplotlib.pyplot as plt
    # import pandas as pd

    # Create a figure and a set of subplots
    # fig, ax = plt.subplots()

    # create a line chart for each data series
    # ax.plot(timestamps, pd.Series(prices).rolling(90).mean() /
    #         pd.Series(prices).rolling(90).mean().min(), color='red')
    # ax.plot(timestamps, pd.Series(con).rolling(90).mean() /
    #         pd.Series(con).rolling(90).mean().min(), color='green')
    # ax.plot(timestamps, pd.Series(prod).rolling(90).mean() /
    #         pd.Series(prod).rolling(90).mean().min(), color='blue')

    # Show the plot
    # plt.show()
