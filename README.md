<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B站链接预览插件 · AstrBot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e9edf3 100%);
            color: #1e2b3c;
            line-height: 1.6;
            padding: 2rem 1.5rem;
            display: flex;
            justify-content: center;
        }

        .container {
            max-width: 1000px;
            width: 100%;
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            padding: 2.5rem;
            border: 1px solid rgba(255,255,255,0.5);
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(145deg, #1e6f9f, #0a2942);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .badge {
            display: inline-block;
            background: #1e6f9f;
            color: white;
            font-size: 0.8rem;
            padding: 0.3rem 1rem;
            border-radius: 30px;
            font-weight: 500;
            letter-spacing: 0.3px;
            background: linear-gradient(145deg, #1e6f9f, #154b6b);
            box-shadow: 0 4px 8px rgba(0,40,80,0.2);
        }

        .subtitle {
            font-size: 1.2rem;
            color: #2c3e50;
            margin-bottom: 2rem;
            border-left: 5px solid #1e6f9f;
            padding-left: 1.2rem;
            background: #f0f6fc;
            border-radius: 0 1rem 1rem 0;
            line-height: 1.4;
        }

        .section {
            margin: 2.5rem 0;
        }

        .section h2 {
            font-size: 1.8rem;
            font-weight: 600;
            color: #0a2942;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section h2:after {
            content: '';
            flex: 1;
            height: 2px;
            background: linear-gradient(90deg, #1e6f9f 0%, transparent 100%);
            margin-left: 15px;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }

        .feature-card {
            background: white;
            border-radius: 1.5rem;
            padding: 1.5rem 1.2rem;
            box-shadow: 0 8px 20px rgba(0,30,60,0.08);
            border: 1px solid rgba(30,111,159,0.15);
            transition: all 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(30,111,159,0.15);
            border-color: #1e6f9f40;
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.8rem;
        }

        .feature-card h3 {
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
            color: #0a2942;
        }

        .feature-card p {
            color: #2d4b65;
            font-size: 0.95rem;
        }

        .code-block {
            background: #0b1b2a;
            color: #e3eaf0;
            padding: 1.2rem 1.5rem;
            border-radius: 1.2rem;
            overflow-x: auto;
            font-family: 'Fira Code', 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            margin: 1.2rem 0;
            border: 1px solid #2d4b65;
        }

        .inline-code {
            background: #e3eaf0;
            color: #0a2942;
            padding: 0.2rem 0.5rem;
            border-radius: 0.5rem;
            font-family: monospace;
            font-size: 0.9rem;
            border: 1px solid #a0c0d0;
        }

        .table-wrap {
            overflow-x: auto;
            margin: 1.5rem 0;
            border-radius: 1rem;
            border: 1px solid #cbd5e1;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th {
            background: #1e6f9f;
            color: white;
            font-weight: 600;
            padding: 0.8rem 1rem;
            text-align: left;
        }

        td {
            padding: 0.8rem 1rem;
            border-bottom: 1px solid #dde7f0;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .note {
            background: #e6f3ff;
            border-left: 6px solid #1e6f9f;
            padding: 1.2rem 1.8rem;
            border-radius: 1rem;
            margin: 1.5rem 0;
            color: #1a405b;
        }

        .step-list {
            list-style: none;
            counter-reset: step-counter;
        }

        .step-list li {
            counter-increment: step-counter;
            margin-bottom: 1rem;
            padding-left: 2.5rem;
            position: relative;
            font-weight: 500;
        }

        .step-list li::before {
            content: counter(step-counter);
            background: #1e6f9f;
            color: white;
            font-size: 0.8rem;
            font-weight: bold;
            width: 1.8rem;
            height: 1.8rem;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            left: 0;
            top: 0;
        }

        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, #1e6f9f 20%, #cbd5e1 90%);
            margin: 2rem 0;
        }

        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #5d7184;
            font-size: 0.9rem;
            margin-top: 2rem;
        }

        .license {
            background: #f0f4f9;
            padding: 0.3rem 1rem;
            border-radius: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            📺 Bilibili Preview
            <span class="badge">v1.0.0</span>
        </h1>
        <div class="subtitle">
            🚀 为 AstrBot 打造的 B站视频链接预览插件 —— 自动解析 BV号/AV号/短链接，支持 QQ 小程序分享，图文并茂，带缓存。
        </div>

        <!-- 特性区 -->
        <div class="section">
            <h2>✨ 核心特性</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">🔗</div>
                    <h3>多格式识别</h3>
                    <p>BV号、AV号、b23.tv 短链接，通通拿下。</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3>QQ 小程序解析</h3>
                    <p>直接识别 QQ 转发的 B站卡片，不再错过分享。</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3>智能缓存</h3>
                    <p>内存缓存视频信息，避免重复请求，节省资源。</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🖼️</div>
                    <h3>图文预览</h3>
                    <p>支持文本+封面图，图片本地缓存，减少流量。</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>数据格式化</h3>
                    <p>播放/弹幕/点赞自动转为「万/亿」，时长 mm:ss / hh:mm:ss。</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚙️</div>
                    <h3>可配置</h3>
                    <p>通过 metadata.yaml 灵活开关功能，适应你的需求。</p>
                </div>
            </div>
        </div>

        <!-- 安装 -->
        <div class="section">
            <h2>📦 安装插件</h2>
            <ul class="step-list">
                <li>进入 AstrBot 插件目录 <span class="inline-code">data/plugins/</span></li>
                <li>创建文件夹 <span class="inline-code">astrbot_plugin_bilibili_preview</span> 并将 <span class="inline-code">main.py</span> 与 <span class="inline-code">metadata.yaml</span> 放入其中</li>
                <li>安装依赖：<span class="inline-code">pip install aiohttp</span></li>
                <li>在 AstrBot WebUI 插件管理页面，点击「重载插件」</li>
            </ul>
            <div class="note">
                💡 提示：你也可以直接 <code>git clone</code> 本仓库到 plugins 目录下。
            </div>
        </div>

        <!-- 配置 -->
        <div class="section">
            <h2>⚙️ 配置项 (metadata.yaml)</h2>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>参数</th><th>类型</th><th>默认值</th><th>说明</th></tr></thead>
                    <tbody>
                        <tr><td>cache_enabled</td><td>bool</td><td>true</td><td>启用缓存，减少重复请求B站API</td></tr>
                        <tr><td>cache_ttl</td><td>int</td><td>3600</td><td>缓存有效时间（秒）</td></tr>
                        <tr><td>enable_image_preview</td><td>bool</td><td>true</td><td>是否返回封面图片（图文混排）</td></tr>
                    </tbody>
                </table>
            </div>
            <p>修改配置后需重载插件生效。</p>
        </div>

        <!-- 使用方法 -->
        <div class="section">
            <h2>🚀 快速使用</h2>
            <p>在群里发送以下任意格式的内容，机器人会自动回复预览信息：</p>
            <div class="code-block">
                # 纯文本链接<br>
                https://www.bilibili.com/video/BV1xx411c7mD<br>
                b23.tv/abc123<br>
                BV1xx411c7mD<br>
                av123456<br><br>
                # 小程序分享（QQ转发）<br>
                [直接转发B站视频卡片即可]
            </div>
            <p>示例输出：</p>
            <div class="code-block" style="background:#f0f4fc; color:#0a2942;">
                🎬 【全自动B站预览插件开发教程】<br>
                👤 UP主：技术宅<br>
                📊 播放：12.3万  💬 弹幕：245  ❤️ 点赞：1.2万<br>
                ⏱️ 时长：15:30  📁 分区：科技<br>
                📝 简介：本期视频手把手教你写AstrBot插件...<br>
                🔗 https://www.bilibili.com/video/BV1xx411c7mD
                [图片：封面]
            </div>
        </div>

        <!-- 项目结构/源码说明 -->
        <div class="section">
            <h2>📂 插件源码结构</h2>
            <div class="code-block">
                📁 astrbot_plugin_bilibili_preview/<br>
                ├── main.py                 # 主逻辑（消息监听、API调用、缓存、图文发送）<br>
                ├── metadata.yaml           # 插件元数据及配置声明<br>
                └── images/                  # 自动生成的封面缓存目录（首次运行后出现）
            </div>
        </div>

        <!-- 注意事项 -->
        <div class="note">
            ⚠️ 注意：B站API有频率限制，建议开启缓存（默认开启）；如果图片无法显示，检查网络或关闭图片预览。
        </div>

        <!-- 开发者与许可证 -->
        <hr>
        <div class="footer">
            <span>👤 作者：AlienStar · 为 <a href="https://github.com/Soulter/AstrBot" style="color:#1e6f9f; text-decoration: none;">AstrBot</a> 打造</span>
            <span class="license">📜 MIT License</span>
        </div>
        <div style="text-align: center; margin-top: 1.5rem; color: #7f8c8d; font-size: 0.8rem;">
            ✨ 如果觉得好用，欢迎给仓库点个 Star ~
        </div>
    </div>
</body>
</html>
