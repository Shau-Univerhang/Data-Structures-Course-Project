"""
视频压缩工具模块

使用 FFmpeg 将 H.264 视频转码为 H.265 (HEVC)，实现 30%-50% 的体积压缩。
"""

import os
import time
import subprocess
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CompressionResult:
    """压缩结果"""
    success: bool
    output_path: Optional[str] = None
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 1.0
    duration_seconds: float = 0.0
    error: Optional[str] = None
    video_info: Optional[Dict[str, Any]] = None


class VideoCompressor:
    """视频压缩处理器（基于 FFmpeg）"""
    
    # H.265 压缩配置
    DEFAULT_CONFIG = {
        "vcodec": "libx265",           # H.265 视频编码器
        "crf": 28,                     # 恒定质量因子（18=高质量, 28=平衡, 35=小体积）
        "preset": "fast",              # 编码速度（ultrafast/fast/medium/slow/veryslow）
        "acodec": "aac",               # 音频编码器
        "ab": "128k",                  # 音频比特率
        "pix_fmt": "yuv420p",          # 像素格式（最大兼容性）
        "threads": 0,                  # 线程数（0=自动）
        "movflags": "+faststart"       # 优化 Web 播放
    }
    
    # 支持的输入格式
    SUPPORTED_FORMATS = {'.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.wmv'}
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化视频压缩器
        
        Args:
            config: 自定义压缩配置，会覆盖默认配置
        """
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
    
    def compress(self, input_path: str, output_dir: str = None) -> CompressionResult:
        """
        执行视频压缩
        
        Args:
            input_path: 原始视频文件路径
            output_dir: 输出目录，默认与输入文件同目录
        
        Returns:
            CompressionResult: 压缩结果
        """
        start_time = time.time()
        
        # 1. 验证输入文件
        if not os.path.exists(input_path):
            return CompressionResult(
                success=False,
                error=f"输入文件不存在: {input_path}"
            )
        
        ext = os.path.splitext(input_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            return CompressionResult(
                success=False,
                error=f"不支持的视频格式: {ext}"
            )
        
        original_size = os.path.getsize(input_path)
        
        # 2. 设置输出路径
        if output_dir is None:
            output_dir = os.path.dirname(input_path)
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_compressed.mp4")
        
        # 3. 获取视频信息
        video_info = self._get_video_info(input_path)
        
        # 4. 构建 FFmpeg 命令
        cmd = self._build_ffmpeg_command(input_path, output_path)
        
        # 5. 执行压缩
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            if process.returncode != 0:
                return CompressionResult(
                    success=False,
                    error=f"FFmpeg 执行失败: {process.stderr}",
                    video_info=video_info
                )
            
            # 6. 验证输出
            if not os.path.exists(output_path):
                return CompressionResult(
                    success=False,
                    error="输出文件未生成",
                    video_info=video_info
                )
            
            compressed_size = os.path.getsize(output_path)
            duration = time.time() - start_time
            
            return CompressionResult(
                success=True,
                output_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compressed_size / original_size if original_size > 0 else 1.0,
                duration_seconds=duration,
                video_info=video_info
            )
            
        except subprocess.TimeoutExpired:
            return CompressionResult(
                success=False,
                error="压缩超时",
                video_info=video_info
            )
        except Exception as e:
            return CompressionResult(
                success=False,
                error=str(e),
                video_info=video_info
            )
    
    def _build_ffmpeg_command(self, input_path: str, output_path: str) -> list:
        """构建 FFmpeg 命令"""
        cmd = [
            "ffmpeg",
            "-y",                      # 覆盖输出文件
            "-i", input_path,          # 输入文件
            "-c:v", self.config["vcodec"],  # 视频编码器
            "-crf", str(self.config["crf"]),  # 质量因子
            "-preset", self.config["preset"], # 编码速度
            "-c:a", self.config["acodec"],    # 音频编码器
            "-b:a", self.config["ab"],        # 音频比特率
            "-pix_fmt", self.config["pix_fmt"], # 像素格式
        ]
        
        # 添加线程设置
        if self.config.get("threads", 0) > 0:
            cmd.extend(["-threads", str(self.config["threads"])])
        
        # 添加 movflags
        if self.config.get("movflags"):
            cmd.extend(["-movflags", self.config["movflags"]])
        
        cmd.append(output_path)
        return cmd
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"获取视频信息失败: {e}")
        
        return {}
    
    def get_supported_formats(self) -> set:
        """获取支持的视频格式"""
        return self.SUPPORTED_FORMATS


# 便捷函数
def compress_video(input_path: str, output_dir: str = None, config: Dict = None) -> CompressionResult:
    """
    快捷视频压缩函数
    
    Args:
        input_path: 输入视频路径
        output_dir: 输出目录
        config: 自定义配置
    
    Returns:
        CompressionResult: 压缩结果
    """
    compressor = VideoCompressor(config)
    return compressor.compress(input_path, output_dir)


if __name__ == "__main__":
    # 测试示例
    print("视频压缩工具 - 使用说明:")
    print("1. 确保已安装 FFmpeg: https://ffmpeg.org/download.html")
    print("2. 使用示例:")
    print('   from utils.video_compressor import compress_video')
    print('   result = compress_video("input.mp4", "./output")')
    print(f'   print(f"压缩率: {result.compression_ratio:.1%}")')