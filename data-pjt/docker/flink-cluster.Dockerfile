FROM flink:2.0.0-scala_2.12
RUN rm -f /opt/flink/lib/kafka-clients-*.jar
COPY jargroup/flink-connector-kafka-4.0.0-2.0.jar /opt/flink/lib/
COPY config.yaml /opt/flink/conf/config.yaml