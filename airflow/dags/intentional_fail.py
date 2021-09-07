#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example dag for using a Kubernetes Executor Configuration.
"""
import logging
import os
import sys

from airflow import DAG
from airflow.example_dags.libs.helper import print_stuff
from airflow.operators.python import PythonOperator
from airflow.settings import AIRFLOW_HOME
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
}

log = logging.getLogger(__name__)

try:
    from kubernetes.client import models as k8s

    with DAG(
        dag_id='intentional_failure_test',
        default_args=default_args,
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['intentional', 'test'],
    ) as dag:

        def training():
            """
            Training
            """
            import os
            import sys
            return_code = os.system("cat /test/pass.txt")
            if return_code != 0:
                raise ValueError(f"Error when checking volume mount. Return code {return_code}")

        start_task = PythonOperator(
            task_id="start_task",
            python_callable=print_stuff,
            executor_config={
                "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(annotations={"stage": "start"})),
            },
        )

        training_task = PythonOperator(
            task_id="training_task",
            python_callable=training,
            executor_config={
                "pod_override": k8s.V1Pod(
                    spec=k8s.V1PodSpec(
			            metadata=k8s.V1ObjectMeta(annotations={"stage": "train"}),
                        containers=[
                            k8s.V1Container(
                                name="base",
                                volume_mounts=[
                                    k8s.V1VolumeMount(
                                        mount_path="/test/", name="test-volume"
                                    )
                                ],
                            )
                        ],
                        volumes=[
                            k8s.V1Volume(
                                name="test-volume",
                                host_path=k8s.V1HostPathVolumeSource(path="/tmp/"),
                            )
                        ],
                    )
                ),
            },
        )

        end_task = PythonOperator(
            task_id="training_task",
            python_callable=print_stuff,
            executor_config={
                "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(annotations={"stage": "end"})),
            },
        )
        start_task >> training_task >> end_task
except ImportError as e:
    log.warning("Could not import DAGs in summary_training_dag.py: %s", str(e))
    log.warning("Install kubernetes dependencies with: pip install apache-airflow['cncf.kubernetes']")
