# 日记压缩存储方案

## 一、方案概述

针对日记支持视频后的存储需求，特别是**时间轴组件（itinerary）**的验收重点，本方案采用**多层压缩策略**：文本内容用 gzip，视频用 FFmpeg 转码，时间轴与内容合并压缩。

---

## 二、算法选择

### 1. 文本/JSON 数据：gzip
- **选择理由**：时间轴是 JSON 数组（文本格式），gzip 对 JSON 压缩率可达 60%-80%
- **复用现有**：`algorithms/core.py` 中已有 `compress_diary`/`decompress_diary` 函数
- **压缩率**：文本压缩率约 70%，时间轴 JSON 压缩率约 60%

### 2. 视频文件：H.265 (HEVC) 转码
- **选择理由**：视频本身是二进制压缩格式，gzip 无效；需转码压缩
- **压缩率**：H.265 比 H.264 体积小 30%-50%，画质相当
- **工具**：ffmpeg-python（Python 封装 FFmpeg）

### 3. 图片文件：WebP 转换
- **选择理由**：图片也是二进制格式，需转换压缩格式
- **压缩率**：WebP 比 JPEG 小 25%-35%，支持透明度
- **工具**：Pillow 库

---

## 三、数据流设计

### 创建日记时
```
content + itinerary → 合并为字典 → gzip 压缩 → 存储到 content_compressed
videos → FFmpeg 转码为 H.265 → 存储到 videos/
images → 转换为 WebP → 存储到 uploads/
```

### 读取日记时
```
content_compressed → gzip 解压 → 分离 content + itinerary
videos → 直接读取 URL（浏览器解码）
images → 直接读取 URL（浏览器解码）
```

---

## 四、具体实现步骤

### 4.1 修改压缩逻辑（合并 content + itinerary）

#### 后端修改（diary.py）

**create_diary 函数**：
```python
if request.compress:
    data_to_compress = {}
    if request.content:
        data_to_compress["content"] = request.content
    if request.itinerary:
        data_to_compress["itinerary"] = request.itinerary
    if data_to_compress:
        content_compressed = compress_diary(data_to_compress)
        compression_algorithm = "gzip"
```

**get_diary 函数**：
```python
content = diary.content
itinerary = diary.itinerary
if diary.content_compressed:
    try:
        decompressed = decompress_diary(diary.content_compressed)
        content = decompressed.get('content', content)
        itinerary = decompressed.get('itinerary', itinerary)
    except Exception:
        pass
```

**list_diaries 函数**：同理修改解压逻辑

**update_diary 函数**：同理修改压缩逻辑

### 4.2 视频压缩（FFmpeg 转码）

#### 依赖安装
```bash
pip install ffmpeg-python
```

#### 转码函数（新建 utils/video_compressor.py）
```python
import ffmpeg
import os
import uuid

def compress_video(input_path: str, output_dir: str = None) -> dict:
    """
    视频转码压缩（H.264 → H.265）
    
    Args:
        input_path: 原始视频路径
        output_dir: 输出目录，默认与输入同目录
    
    Returns:
        {'success': bool, 'output_path': str, 'original_size': int, 'compressed_size': int, 'compression_ratio': float}
    """
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    original_size = os.path.getsize(input_path)
    
    # 生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_compressed.mp4")
    
    try:
        # FFmpeg 转码为 H.265，CRF 28（平衡画质和体积）
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx265',
            crf=28,
            acodec='aac',
            ab='128k',
            preset='fast'
        )
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        compressed_size = os.path.getsize(output_path)
        
        return {
            'success': True,
            'output_path': output_path,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compressed_size / original_size if original_size > 0 else 1.0
        }
    except Exception as e:
        print(f"视频压缩失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

### 4.3 图片压缩（WebP 转换）

#### 依赖安装
```bash
pip install Pillow
```

#### 转换函数（新建 utils/image_compressor.py）
```python
from PIL import Image
import os

def compress_image_to_webp(input_path: str, quality: int = 75) -> dict:
    """
    图片转换为 WebP 格式
    
    Args:
        input_path: 原始图片路径
        quality: 压缩质量（0-100）
    
    Returns:
        {'success': bool, 'output_path': str, 'original_size': int, 'compressed_size': int, 'compression_ratio': float}
    """
    original_size = os.path.getsize(input_path)
    
    # 生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(os.path.dirname(input_path), f"{base_name}.webp")
    
    try:
        img = Image.open(input_path)
        
        # 转换 RGBA 为 RGB（WebP 支持 RGBA，但为了兼容性）
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        img.save(output_path, 'WEBP', quality=quality)
        
        compressed_size = os.path.getsize(output_path)
        
        return {
            'success': True,
            'output_path': output_path,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compressed_size / original_size if original_size > 0 else 1.0
        }
    except Exception as e:
        print(f"图片压缩失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 五、性能测试方案

### 5.1 测试数据生成

**文本内容**：
- 短日记：500 字
- 中日记：2000 字
- 长日记：5000 字

**时间轴数据**：
- 简单时间轴：1 天 3 个景点
- 中等时间轴：3 天 10 个景点
- 复杂时间轴：7 天 20 个景点

**视频文件**：
- 短视频：10MB（1080p H.264）
- 中视频：50MB（1080p H.264）
- 长视频：100MB（1080p H.264）

**图片文件**：
- 小图片：500KB（JPEG）
- 中图片：2MB（JPEG）
- 大图片：5MB（JPEG）

### 5.2 测试指标

1. **压缩率**：压缩后大小 / 原始大小
2. **压缩时间**：压缩耗时（毫秒）
3. **解压时间**：解压耗时（毫秒）
4. **质量损失**：主观评价 + 客观指标（PSNR/SSIM）
5. **存储节省**：总体存储节省百分比

---

## 六、预期效果

| 数据类型 | 原始大小 | 压缩后大小 | 压缩率 | 压缩时间 | 解压时间 |
|---------|---------|-----------|-------|---------|---------|
| 文本（500字） | 1KB | 0.3KB | 30% | <1ms | <1ms |
| 文本（2000字） | 4KB | 1.2KB | 30% | <1ms | <1ms |
| 文本（5000字） | 10KB | 3KB | 30% | <1ms | <1ms |
| 时间轴（简单） | 1KB | 0.4KB | 40% | <1ms | <1ms |
| 时间轴（中等） | 5KB | 2KB | 40% | <1ms | <1ms |
| 时间轴（复杂） | 10KB | 4KB | 40% | <1ms | <1ms |
| 视频（10MB） | 10MB | 6MB | 60% | 5-10s | N/A（浏览器解码） |
| 视频（50MB） | 50MB | 30MB | 60% | 20-30s | N/A（浏览器解码） |
| 视频（100MB） | 100MB | 60MB | 60% | 40-60s | N/A（浏览器解码） |
| 图片（500KB） | 500KB | 300KB | 60% | <100ms | N/A（浏览器解码） |
| 图片（2MB） | 2MB | 1.2MB | 60% | <200ms | N/A（浏览器解码） |
| 图片（5MB） | 5MB | 3MB | 60% | <500ms | N/A（浏览器解码） |

---

## 七、风险与应对

1. **FFmpeg 依赖**：
   - 风险：需安装 FFmpeg 二进制文件
   - 应对：提供安装指南，或使用预编译包

2. **视频转码时间**：
   - 风险：长视频转码耗时较长（影响用户体验）
   - 应对：异步处理（后台任务），上传时先返回 URL，转码完成后更新

3. **兼容性**：
   - 风险：H.265 在部分旧设备不支持
   - 应对：提供 H.264 备用选项，或检测客户端能力

4. **存储管理**：
   - 风险：压缩后需保留原始文件？
   - 应对：压缩成功即删除原始文件，或设置保留策略
