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
        dag_id='example',
        default_args=default_args,
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['example1'],
    ) as dag:
        log.info("testing")

        task_without_template = PythonOperator(
            task_id="task_without_template",
            python_callable=print_stuff,
            executor_config={
                "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(labels={"release": "stable"})),
            },
        )
        # [START task_with_template]
        task_with_template = PythonOperator(
            task_id="task_with_template",
            python_callable=print_stuff,
            executor_config={
                "pod_template_file": os.path.join("/opt/airflow/dags/repo/airflow/dags", "pod_templates/basic_template.yaml"),
                "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(labels={"release": "stable"})),
            },
        )
        # [END task_with_template]

        task_without_template >> task_with_template
except ImportError as e:
    log.warning("Could not import DAGs in example_kubernetes_executor_config.py: %s", str(e))
    log.warning("Install kubernetes dependencies with: pip install apache-airflow['cncf.kubernetes']")
