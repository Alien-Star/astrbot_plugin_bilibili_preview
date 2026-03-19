import re
import time
import json
import aiohttp
from typing import Optional, Dict, Any
from collections import OrderedDict
from pathlib import Path

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Plain, Image

@register("bilibili_preview", "AlienStar", "B站链接预览插件，支持图文混排和缓存", "1.0.0")
class BilibiliPreviewPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 获取插件配置（需在 metadata.yaml 中定义）
        self.config = context.get_config()
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 默认1小时
        self.enable_image = self.config.get("enable_image_preview", True)
        
        # 初始化缓存
        self._cache = OrderedDict()
        
        # 图片缓存目录
        self.image_cache_dir = Path("data/plugins/astrbot_plugin_bilibili_preview/images")
        self.image_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # B站API请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com"
        }

    async def initialize(self):
        logger.info("BilibiliPreviewPlugin 初始化完成")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_message(self, event: AstrMessageEvent):
        """处理所有消息，提取B站视频链接"""
        message_str = event.message_str
        if not message_str:
            return

        # 1.先从纯文本中尝试匹配
        bvid, aid, short_code = self._extract_video_id(message_str)

        # 2. 如果没有匹配到，尝试查找小程序卡片中的视频链接
        if not (bvid or aid or short_code):
            for segment in event.message:
                # 处理 OneBot 的 app 类型(小程序卡片)
                if segment.type == "app":
                    try:
                        # app 类型的 data 可能是 JSON 字符串
                        app_data = json.loads(segment.data.get("data", "{}"))
                        # 尝试从常见字段中提取链接
                        meta = app_data.get("meta", {})
                        for key in meta:
                            if "url" in meta[key]:
                                url = meta[key]["url"]
                                bvid, aid, short_code = self._extract_video_id(url)
                                if bvid or aid or short_code:
                                    break
                        if bvid or aid or short_code:
                            break
                    except Exception as e:
                        logger.error(f"解析 app 消息段失败: {e}")
                # 处理 QQ 官方协议的 ark 类型（分享卡片）
                elif segment.type == "ark":
                    try:
                        ark_data = json.loads(segment.data.get("data", "{}"))
                        # ark 的链接可能在 raw_data 或其它字段中，简单查找所有字符串
                        raw_data = ark_data.get("raw_data", "")
                        if raw_data:
                            bvid, aid, short_code = self._extract_video_id(raw_data)
                            if bvid or aid or short_code:
                                break
                    except Exception as e:
                        logger.error(f"解析 ark 消息段失败: {e}")

        if not (bvid or aid or short_code):
            return
            
        try:
            # 如果是短链接，解析为BV号
            if short_code:
                bvid = await self._resolve_short_url(short_code)
                if not bvid:
                    yield event.plain_result("❌ 无法解析B站短链接")
                    return

            # 生成缓存键
            cache_key = bvid or aid

            # 检查缓存
            if self.cache_enabled:
                cached = self._get_cache(cache_key)
                if cached:
                    logger.info(f"使用缓存: {cache_key}")
                    async for result in self._send_preview(event, cached):
                        yield result
                    return

            # 获取视频信息
            video_info = await self._fetch_video_info(bvid=bvid, aid=aid)
            if not video_info:
                yield event.plain_result("❌ 获取视频信息失败，请稍后重试")
                return

            # 存入缓存
            if self.cache_enabled:
                self._set_cache(cache_key, video_info)

            # 发送预览
            async for result in self._send_preview(event, video_info):
                yield result

        except Exception as e:
            logger.error(f"处理B站链接异常: {e}")
            yield event.plain_result("❌ 处理请求时发生错误")

    def _extract_video_id(self, text: str):
        """从文本中提取BV号、AV号或短链接代码"""
        # BV号：BV开头，后面10位字母数字（捕获完整BV号）
        bv_match = re.search(r'(BV[0-9a-zA-Z]{10,12})', text)
        # AV号：av后面跟数字
        av_match = re.search(r'av(\d+)', text, re.IGNORECASE)
        # 短链接：b23.tv/xxx
        short_match = re.search(r'b23\.tv[/:]([a-zA-Z0-9]+)', text, re.IGNORECASE)

        bvid = bv_match.group(1) if bv_match else None
        aid = av_match.group(1) if av_match else None
        short_code = short_match.group(1) if short_match else None

        return bvid, aid, short_code

    async def _resolve_short_url(self, short_code: str) -> Optional[str]:
        """解析短链接，获取重定向后的BV号"""
        url = f"https://b23.tv/{short_code}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, allow_redirects=True) as resp:
                    final_url = str(resp.url)
                    match = re.search(r'/video/(BV[a-zA-Z0-9]+)', final_url)
                    return match.group(1) if match else None
        except Exception as e:
            logger.error(f"解析短链接失败: {e}")
            return None

    async def _fetch_video_info(self, bvid: str = None, aid: str = None) -> Optional[Dict[str, Any]]:
        """调用B站API获取视频信息"""
        if not bvid and not aid:
            return None

        # 构建API URL
        if bvid:
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        else:
            api_url = f"https://api.bilibili.com/x/web-interface/view?aid={aid}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.headers, timeout=10) as resp:
                    if resp.status != 200:
                        logger.error(f"B站API HTTP {resp.status}")
                        return None
                    data = await resp.json()
                    if data.get("code") != 0:
                        logger.error(f"B站API错误: {data.get('message')}")
                        return None

                    info = data["data"]
                    # 下载封面到本地（如果启用图片预览）
                    pic_local = None
                    if self.enable_image:
                        pic_local = await self._download_image(info["pic"], info["bvid"])

                    return {
                        "bvid": info["bvid"],
                        "title": info["title"],
                        "owner": info["owner"]["name"],
                        "desc": info["desc"].strip() or "暂无简介",
                        "pic_url": info["pic"],
                        "pic_local": pic_local,
                        "view": self._format_number(info["stat"]["view"]),
                        "danmaku": self._format_number(info["stat"]["danmaku"]),
                        "like": self._format_number(info["stat"]["like"]),
                        "pubdate": self._format_time(info["pubdate"]),
                        "duration": self._format_duration(info["duration"]),
                        "tname": info.get("tname", "未知分区")
                    }
        except Exception as e:
            logger.error(f"获取视频信息异常: {e}")
            return None

    async def _download_image(self, url: str, bvid: str) -> Optional[str]:
        """下载封面图片到本地缓存"""
        try:
            # 生成文件名
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                ext = 'jpg'
            filename = f"{bvid}_{int(time.time())}.{ext}"
            filepath = self.image_cache_dir / filename

            # 如果文件已存在，直接返回
            if filepath.exists():
                return str(filepath)

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        logger.info(f"封面已缓存: {filepath}")
                        return str(filepath)
        except Exception as e:
            logger.error(f"下载封面失败: {e}")
        return None

    async def _send_preview(self, event: AstrMessageEvent, info: Dict):
        """发送预览信息（支持图文混排）"""
        # 构造文本部分
        text = (
            f"🎬 【{info['title']}】\n"
            f"👤 UP主：{info['owner']}\n"
            f"📊 播放：{info['view']}  💬 弹幕：{info['danmaku']}  ❤️ 点赞：{info['like']}\n"
            f"⏱️ 时长：{info['duration']}  📁 分区：{info['tname']}\n"
            f"📝 简介：{info['desc'][:100]}{'...' if len(info['desc']) > 100 else ''}\n"
            f"🔗 https://www.bilibili.com/video/{info['bvid']}"
        )

        # 如果启用图片预览且有本地图片，发送图文消息
        if self.enable_image and info.get('pic_local'):
            yield event.chain_result([
                Plain(text=text),
                Image.fromFileSystem(info['pic_local'])
            ])
        elif self.enable_image and info.get('pic_url'):
            # 没有本地缓存但允许图片，用URL
            yield event.chain_result([
                Plain(text=text),
                Image.fromURL(info['pic_url'])
            ])
        else:
            # 纯文本
            yield event.plain_result(text)

    def _get_cache(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        if key in self._cache:
            data, ts = self._cache[key]
            if time.time() - ts < self.cache_ttl:
                return data
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Dict):
        """设置缓存"""
        self._cache[key] = (data, time.time())
        # 限制缓存大小
        if len(self._cache) > 100:
            self._cache.popitem(last=False)

    def _format_number(self, num: int) -> str:
        """格式化数字（万/亿）"""
        if num >= 100000000:
            return f"{num/100000000:.1f}亿"
        elif num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)

    def _format_time(self, timestamp: int) -> str:
        """格式化时间戳为日期"""
        import datetime
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

    def _format_duration(self, seconds: int) -> str:
        """格式化视频时长"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    async def terminate(self):
        """插件卸载时清理资源"""
        logger.info("BilibiliPreviewPlugin 正在清理...")
        # 清理过期图片（7天以上）
        try:
            now = time.time()
            for file in self.image_cache_dir.glob("*"):
                if file.is_file() and now - file.stat().st_mtime > 7*86400:
                    file.unlink()
                    logger.info(f"已清理过期图片: {file}")
        except Exception as e:
            logger.error(f"清理图片失败: {e}")
