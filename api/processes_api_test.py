# -*- coding: utf-8 -*-
# Copyright 2022 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import testing_config  # Must be imported before the module under test.

import flask

from api import processes_api
from framework import ramcache
from internals import models
from internals import processes

test_app = flask.Flask(__name__)


class ProcessesAPITest(testing_config.CustomTestCase):

  def setUp(self):
    self.feature_1 = models.Feature(
        name='feature one', summary='sum', category=1, visibility=1,
        standardization=1, web_dev_views=1, impl_status_chrome=1)
    self.feature_1.put()
    self.feature_id = self.feature_1.key.integer_id()
    
    self.handler = processes_api.ProcessesAPI()
    self.request_path = f'/api/v0/features/{self.feature_id}/process'

  def tearDown(self):
    self.feature_1.key.delete()
    ramcache.flush_all()
    ramcache.check_for_distributed_invalidation()

  def test_get__default_feature_type(self):
    """We can get process for features with the default feature type (New feature incubation)."""
    with test_app.test_request_context(self.request_path):
      actual = self.handler.do_get(self.feature_id)
    expected = processes.process_to_dict(processes.BLINK_LAUNCH_PROCESS)
    self.assertEqual(expected, actual)

  def test_get__feature_type_0(self):
    """We can get process for features with feature type 0 (New feature incubation)."""
    self.feature_1.feature_type = 0
    with test_app.test_request_context(self.request_path):
      actual = self.handler.do_get(self.feature_id)
    expected = processes.process_to_dict(processes.BLINK_LAUNCH_PROCESS)
    self.assertEqual(expected, actual)

  def test_get__feature_type_1(self):
    """We can get process for features with feature type 1 (Existing feature implementation)."""
    self.feature_1.feature_type = 1
    with test_app.test_request_context(self.request_path):
      actual = self.handler.do_get(self.feature_id)
    expected = processes.process_to_dict(processes.BLINK_FAST_TRACK_PROCESS)
    self.assertEqual(expected, actual)

  def test_get__feature_type_2(self):
    """We can get process for features with feature type 2 (Web developer facing change to existing code)."""
    self.feature_1.feature_type = 2
    with test_app.test_request_context(self.request_path):
      actual = self.handler.do_get(self.feature_id)
    expected = processes.process_to_dict(processes.PSA_ONLY_PROCESS)
    self.assertEqual(expected, actual)

  def test_get__feature_type_3(self):
    """We can get process for features with feature type 3 (Feature deprecation)."""
    self.feature_1.feature_type = 3
    with test_app.test_request_context(self.request_path):
      actual = self.handler.do_get(self.feature_id)
    expected = processes.process_to_dict(processes.DEPRECATION_PROCESS)
    self.assertEqual(expected, actual)
