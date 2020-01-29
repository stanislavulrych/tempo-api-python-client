from unittest import TestCase

import tempoapiclient

class TestModule(TestCase):
    def test_client_creation(self):
        from tempoapiclient import client

        tempo = tempoapiclient.client.Tempo(
            auth_token="<your_tempo_api_key>",
            base_url="https://api.tempo.io/core/3")

        self.assertTrue(isinstance(tempo, tempoapiclient.client.Tempo))