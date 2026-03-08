import unittest
import json
import io
from api.controllers import app

class TestSessionAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_full_session_flow(self):
        # 1. Start Session
        response = self.app.post('/session/start', 
                                 data=json.dumps({'user_id': 'test_user'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        session_id = response.get_json()['session_id']
        self.assertIsNotNone(session_id)

        # 2. Post Text
        response = self.app.post('/session/text',
                                 data=json.dumps({'session_id': session_id, 'text': 'How are my tomatoes?'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # 3. Upload Image
        img_buffer = io.BytesIO()
        from PIL import Image as PILImage
        PILImage.new('RGB', (10, 10), color='red').save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        response = self.app.post('/session/image',
                                 data={'session_id': session_id, 'image': (img_buffer, 'test.jpg')},
                                 content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', response.get_json())

        # 4. Post Voice
        response = self.app.post('/session/voice',
                                 data={'session_id': session_id, 'voice': (io.BytesIO(b"fake voice data"), 'test.wav')},
                                 content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('transcription', response.get_json())

        # 5. Post Location
        response = self.app.post('/session/location',
                                 data=json.dumps({'session_id': session_id, 'latitude': 18.5204, 'longitude': 73.8567}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # 6. End Session
        response = self.app.post('/session/end',
                                 data=json.dumps({'session_id': session_id}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'completed')
        self.assertIn('response', data)
        self.assertIn('summary_context', data)
        
        # Verify context contents
        context = data['summary_context']
        self.assertEqual(len(context['messages']), 3)
        self.assertEqual(context['messages'][0]['type'], 'text')
        
        # Verify image message (no analysis)
        self.assertEqual(context['messages'][1]['type'], 'image')
        self.assertIn('url', context['messages'][1])
        self.assertIn('filename', context['messages'][1])
        self.assertNotIn('analysis', context['messages'][1])
        
        # Verify voice message (no transcription)
        self.assertEqual(context['messages'][2]['type'], 'voice')
        self.assertIn('url', context['messages'][2])
        self.assertIn('filename', context['messages'][2])
        self.assertNotIn('transcription', context['messages'][2])
        
        self.assertEqual(context['location']['lat'], 18.5204)
        self.assertIn('weather', context)
        # Verify weather contains either data or an error (since we might not have a key in test env)
        self.assertTrue(any(k in context['weather'] for k in ['main', 'error', 'weather']))

if __name__ == '__main__':
    unittest.main()
