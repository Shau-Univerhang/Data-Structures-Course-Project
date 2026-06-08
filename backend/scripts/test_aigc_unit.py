"""
AIGC 动画模块单元测试
=====================
测试不依赖外部 API，只测试本地逻辑
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAIGCAnimation(unittest.TestCase):
    """AIGC 动画模块单元测试"""
    
    def test_travel_prompts_exist(self):
        """测试固定提示词模板"""
        from services.aigc_animation import TRAVEL_ANIMATION_PROMPTS
        
        self.assertIsInstance(TRAVEL_ANIMATION_PROMPTS, list)
        self.assertGreaterEqual(len(TRAVEL_ANIMATION_PROMPTS), 4)
        
        # 每个提示词都应该包含旅游相关的关键词
        for prompt in TRAVEL_ANIMATION_PROMPTS:
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 20)
            # 检查包含电影/旅游相关关键词
            has_travel_keyword = any(kw in prompt.lower() for kw in [
                'travel', 'cinematic', 'landscape', 'camera', 'vlog'
            ])
            self.assertTrue(has_travel_keyword, f"提示词缺少旅游关键词: {prompt[:50]}")
    
    @patch('services.aigc_animation.ZHIPU_API_KEY', "test_key_12345")
    def test_get_token(self):
        """测试 Token 获取"""
        from services import aigc_animation
        token = aigc_animation.get_zhipu_token()
        self.assertEqual(token, "test_key_12345")
    
    def test_get_token_missing_key(self):
        """测试缺少 API Key 时抛出异常"""
        import services.aigc_animation as mod
        original_key = mod.ZHIPU_API_KEY
        mod.ZHIPU_API_KEY = ""
        
        try:
            with self.assertRaises(ValueError) as context:
                mod.get_zhipu_token()
            self.assertIn("未配置", str(context.exception))
        finally:
            mod.ZHIPU_API_KEY = original_key
    
    @patch('services.aigc_animation.requests.get')
    def test_encode_url_image(self, mock_get):
        """测试 URL 图片编码"""
        import base64
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        from services.aigc_animation import _encode_image
        
        result = _encode_image("https://example.com/test.jpg")
        
        expected = base64.b64encode(b"fake_image_data").decode("utf-8")
        self.assertEqual(result["base64"], expected)
        self.assertEqual(result["mime_type"], "image/png")
        mock_get.assert_called_once()

    def test_encode_data_url_image(self):
        """测试前端上传的 data URL 图片编码"""
        import base64
        from services.aigc_animation import _encode_image

        raw_bytes = b"fake_image_data"
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{encoded}"

        result = _encode_image(data_url)

        self.assertEqual(result["base64"], encoded)
        self.assertEqual(result["mime_type"], "image/jpeg")
    
    @patch('services.aigc_animation._encode_image')
    @patch('services.aigc_animation._create_cogvideo_task')
    @patch('services.aigc_animation._poll_task_status')
    def test_image_to_video_success(self, mock_poll, mock_create, mock_encode):
        """测试完整的图生视频流程 - 成功"""
        mock_encode.return_value = {"base64": "base64_data", "mime_type": "image/jpeg"}
        mock_create.return_value = "task_123"
        mock_poll.return_value = "https://video.url/test.mp4"
        
        from services.aigc_animation import image_to_video
        
        result = image_to_video("https://test.jpg", prompt="test prompt")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["task_id"], "task_123")
        self.assertEqual(result["video_url"], "https://video.url/test.mp4")
        mock_encode.assert_called_once()
        mock_create.assert_called_once()
        mock_poll.assert_called_once()
    
    @patch('services.aigc_animation._encode_image')
    def test_image_to_video_encode_failed(self, mock_encode):
        """测试图片编码失败"""
        mock_encode.return_value = None
        
        from services.aigc_animation import image_to_video
        
        result = image_to_video("https://test.jpg")
        
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["message"], "无法读取图片")
    
    @patch('services.aigc_animation._encode_image')
    @patch('services.aigc_animation._create_cogvideo_task')
    def test_image_to_video_task_failed(self, mock_create, mock_encode):
        """测试任务创建失败"""
        mock_encode.return_value = {"base64": "base64_data", "mime_type": "image/jpeg"}
        mock_create.return_value = None
        
        from services.aigc_animation import image_to_video
        
        result = image_to_video("https://test.jpg")
        
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["message"], "创建视频任务失败")
    
    @patch('services.aigc_animation._encode_image')
    @patch('services.aigc_animation._create_cogvideo_task')
    @patch('services.aigc_animation._poll_task_status')
    def test_image_to_video_poll_timeout(self, mock_poll, mock_create, mock_encode):
        """测试轮询超时"""
        mock_encode.return_value = {"base64": "base64_data", "mime_type": "image/jpeg"}
        mock_create.return_value = "task_123"
        mock_poll.return_value = None
        
        from services.aigc_animation import image_to_video
        
        result = image_to_video("https://test.jpg")
        
        self.assertEqual(result["status"], "failed")
        self.assertIn("超时或失败", result["message"])
    
    @patch('services.aigc_animation.requests.post')
    @patch('services.aigc_animation.get_zhipu_token')
    def test_create_task_success(self, mock_token, mock_post):
        """测试创建任务成功"""
        mock_token.return_value = "test_token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task_456"}
        mock_post.return_value = mock_response
        
        from services.aigc_animation import _create_cogvideo_task
        
        result = _create_cogvideo_task("base64_data", "test prompt")
        
        self.assertEqual(result, "task_456")
        mock_post.assert_called_once()
        
        # 验证请求参数
        call_args = mock_post.call_args
        self.assertIn("cogvideox-2", call_args[1]["json"]["model"])
        self.assertEqual(call_args[1]["json"]["prompt"], "test prompt")
        self.assertIn("data:image/jpeg;base64,", call_args[1]["json"]["image_url"])
    
    @patch('services.aigc_animation.requests.get')
    @patch('services.aigc_animation.get_zhipu_token')
    def test_poll_task_success(self, mock_token, mock_get):
        """测试轮询任务成功"""
        mock_token.return_value = "test_token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_status": "SUCCESS",
            "video_result": [{"url": "https://video.url/test.mp4"}]
        }
        mock_get.return_value = mock_response
        
        from services.aigc_animation import _poll_task_status
        
        result = _poll_task_status("task_123", timeout=10)
        
        self.assertEqual(result, "https://video.url/test.mp4")
    
    @patch('services.aigc_animation.requests.get')
    @patch('services.aigc_animation.get_zhipu_token')
    def test_poll_task_failed(self, mock_token, mock_get):
        """测试任务失败"""
        mock_token.return_value = "test_token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_status": "FAILED",
            "message": "Invalid prompt"
        }
        mock_get.return_value = mock_response
        
        from services.aigc_animation import _poll_task_status
        
        result = _poll_task_status("task_123", timeout=10)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    print("=" * 60)
    print("AIGC 动画模块单元测试")
    print("=" * 60)
    print()
    
    unittest.main(verbosity=2)
