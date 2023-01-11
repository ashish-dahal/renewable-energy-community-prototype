import paho.mqtt.client as mqtt
import json


class DynamicPriceCalculator:
    '''
    A class to calculate the optimal price for a electricity using the Nash Bargaining Solution.

    Parameters:
        min_price (float): minimum price for the electricity
        broker_name (string): address for mqtt broker
    '''

    def __init__(self, min_price, broker_name):

        # initialize the mqtt client
        self.client = mqtt.Client()
        self.client.connect(broker_name, 1883)

        # initialize the consumption and production of each consumer and producer
        self.consumer_consumption = None
        self.producer_production = None

        # initialize  the total consumption and production
        self.total_consumption = None
        self.total_production = None

        # set minimum price
        self.min_price = min_price

        # initialize the price with the Nash Bargaining Solution
        self.price = 0

    def get_optimal_price(self, consumer_consumption, producer_production):
        '''
        Calculate the optimal price for a electricity using the Nash Bargaining Solution.

        Parameters:
            consumer_consumption (list): the consumption of each consumer in kWh
            producer_production (list): the production of each producer in kWh

        Returns: (float) the optimal price in euros
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

        # set the minimum price
        if self.price < self.min_price:
            self.price = self.min_price * 10

        # return the optimal price in euros
        return self.price/10

    # function to subscribe to get the consumption and production of each consumer and producer
    def on_connect(self, client, userdata, flags, rc):
        '''The callback for when the client receives a CONNACK response from the server.'''
        print("Connected with result code "+str(rc))
        client.subscribe("energy/aggregate/consumption")
        client.subscribe("energy/aggregate/production")

    # function to receive the consumption and production of each consumer and producer
    def on_message(self, client, userdata, msg):
        '''The callback for when a PUBLISH message is received from the server.'''

        print("topic: " + msg.topic+"\n")
        if msg.topic == "energy/aggregate/consumption":
            self.consumer_consumption = json.loads(msg.payload)
            print(self.consumer_consumption)
        elif msg.topic == "energy/aggregate/production":
            self.producer_production = json.loads(msg.payload)
            print(self.producer_production)

        if self.consumer_consumption is not None and self.producer_production is not None:
            # calculate the optimal price
            self.get_optimal_price(
                self.consumer_consumption, self.producer_production)
            # publish the optimal price
            self.publish_price()
            print("price:", self.price)

    # function to publish the optimal price
    def publish_price(self):
        '''Publish the optimal price.'''
        self.client.publish(
            "energy/price", json.dumps({"price": self.price}))

    def start(self):
        '''Start the dynamic price calculator.'''
        # set the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.loop_forever()


if __name__ == "__main__":
    # create an instance of the class
    dynamic_price_calculator = DynamicPriceCalculator(
        min_price=2, broker_name="mqtt_broker")

    # start the dynamic price calculator
    dynamic_price_calculator.start()
