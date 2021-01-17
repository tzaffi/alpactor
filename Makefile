kafka-envs:
	ccloud environment list

kafka-clusters:
	ccloud kafka cluster list

kafka-topics:
	ccloud kafka topic list


# EG: $ make kafka-produce TOPIC=alpactor_dev
TOPIC = "test-topic"
kafka-produce:
	ccloud kafka topic produce $(TOPIC)

# EG: $ make kafka-consume TOPIC=alpactor_dev
kafka-consume-beginning-of-time:
	ccloud kafka topic consume -b $(TOPIC)
