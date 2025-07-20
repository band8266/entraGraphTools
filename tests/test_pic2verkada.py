import importlib.util
import os
import unittest
from unittest.mock import patch, Mock

# Utility to import the module while injecting required globals

def import_pic_module():
    spec = importlib.util.spec_from_file_location("entraPic2Verkada", "entraPic2Verkada.py")
    module = importlib.util.module_from_spec(spec)
    module.os = os  # provide os, as file forgets to import it
    with patch.dict(os.environ, {
        "TENANT_ID": "t",
        "CLIENT_ID": "c",
        "CLIENT_SECRET": "s",
        "GROUP_ID": "g",
        "VERKADA_API_KEY": "k",
    }):
        spec.loader.exec_module(module)
    return module

pic_module = import_pic_module()
get_verkada_token = pic_module.get_verkada_token

class TestGetVerkadaToken(unittest.TestCase):
    def test_successful_token_retrieval(self):
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = {"token": "abc123"}
        with patch.object(pic_module.requests, 'post', return_value=mock_resp) as mock_post:
            token = get_verkada_token('my-key')
            self.assertEqual(token, 'abc123')
            mock_post.assert_called_once_with(
                'https://api.verkada.com/token',
                headers={'accept': 'application/json', 'x-api-key': 'my-key'}
            )

    def test_failure_returns_none(self):
        mock_resp = Mock(status_code=400, text='bad request')
        with patch.object(pic_module.requests, 'post', return_value=mock_resp):
            token = get_verkada_token('bad-key')
            self.assertIsNone(token)

if __name__ == '__main__':
    unittest.main()
