import asyncio
import unittest
from unittest.mock import patch

import google_scholar_server as server


class AuthorInfoTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_results_return_error_without_async_callback_failure(self):
        callback_errors = []
        loop = asyncio.get_running_loop()
        original_handler = loop.get_exception_handler()
        loop.set_exception_handler(lambda loop, context: callback_errors.append(context))
        try:
            with patch.object(server.scholarly, 'search_author', return_value=iter([])), patch.object(server.scholarly, 'fill') as fill:
                try:
                    result = await asyncio.wait_for(server.get_author_info('Example Author'), timeout=0.5)
                except asyncio.TimeoutError:
                    self.fail('Empty author results caused the tool to hang')
                self.assertEqual(result['error_code'], 'AUTHOR_RESULTS_UNAVAILABLE')
                self.assertIn('sign-in', result['error'])
                fill.assert_not_called()
                self.assertEqual(callback_errors, [])
        finally:
            loop.set_exception_handler(original_handler)

    async def test_success_preserves_author_response(self):
        author = {'name': 'Example Author', 'citedby': 42, 'publications': []}
        with patch.object(server.scholarly, 'search_author', return_value=iter([author])), patch.object(server.scholarly, 'fill', return_value=author):
            result = await server.get_author_info('Example Author')
        self.assertEqual(result['name'], 'Example Author')
        self.assertEqual(result['citedby'], 42)
        self.assertNotIn('error', result)

    async def test_upstream_failure_returns_error(self):
        with patch.object(server.scholarly, 'search_author', side_effect=RuntimeError('upstream unavailable')):
            result = await server.get_author_info('Example Author')
        self.assertIn('upstream unavailable', result['error'])


if __name__ == '__main__':
    unittest.main()
