Four components for the system (as shown in figure 3) have been implemented for the protoype. The components are: 
- User Interface
- Dynamic Price Calculator
- Energy Data Aggregator
- Predictive Analytics Service. 

The components are implemented as seperate docker containers. The data exchange is done through MQTT. The docker containers used for the implementation are as follows:
* User Interface: `user-interface-grafana`
* Dynamic Price Calculator: `dynamic-price-calculator`
* Predictive Analytics Service: `predictive-analytics-service`
* Data exchange: `mqtt-broker`

#### To run the docker containers, from the terminal:
- From the root of the project, run `docker compose build`
- Run `docker compose up`
- The ML model for predictive-analytics-service can be downloaded from [here](https://drive.google.com/file/d/1BqNw37ZmCBRN_Y9FP4nulcVOi-4rikaN/view?usp=share_link). Place it on the predictive-analytics-service folder.

#### Containers Description:
- `mqtt-broker`: It allows publish-subscribe mechanism for data exchange through paho-mqtt python library. The mqtt topics are:
    * energy/aggregate/consumption
    * energy/aggregate/production
    * energy/aggregate/consumption_history
    * energy/aggregate/production_history
    * energy/household1/consumption
    * energy/household1/production
    * energy/price
- `user-interface-grafana`: It provides a dashboard for the user to see the energy data, price and credits. It can be accessed at http://localhost:3000/ on the browser. The login username and password for admin and user are "admin" "admin" and "user" "user" respectively.
- `dynamic-price-calculator`: It calculates the optimal price from the aggregate electricity data. It subscribes to topics a and b. and publishes to topic g.
- `energy-data-aggregator`: It simulates the individual and aggregate electricity production and consumption. It publishes to topics a, b, c, d, e, f.
- `predictive-analytics-service`: It predicts the future energy consumption and production of individual household.

Additionally, `mqtt-check` container has been implemented to check the mqtt topics. To see the data in the mqtt topics, following command can be executed from the terminal of `mqtt-check` container:
`mosquitto_sub -h mqtt_broker -p 1883 -t <topic>`
