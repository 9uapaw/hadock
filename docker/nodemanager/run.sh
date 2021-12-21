#!/bin/bash

if [[ -z "{NODEMANAGER_DEBUG}" ]]; then
  echo "Debugging is disabled for NodeManager"
else
  echo "Debugging is enabled for NodeManager"
  export HADOOP_OPTS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=9999"
fi

bash /config-set.sh
$HADOOP_HOME/bin/yarn --config $HADOOP_CONF_DIR nodemanager
