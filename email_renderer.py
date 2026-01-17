# email_renderer.py
import time
from config import UP_NAME
from logger_config import logger


class EmailRenderer:
    """邮件内容渲染类"""

    def __init__(self, color_config):
        self.color_config = color_config

    def render_email_content(self, dynamic_id, current_html, current_images, last_html, last_images, current_time=None):
        """渲染邮件内容 - 修复图片显示问题，将跳转按钮放在单独区域，并使用随机对比色渐变"""
        try:
            if current_time is None:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')

            # 获取随机对比色渐变
            primary_color, secondary_color = self.color_config.get_random_gradient()

            email_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{UP_NAME} 动态置顶评论更新通知</title>
                <style>
                    body {{
                        font-family: 'Microsoft YaHei', Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, {primary_color}, {secondary_color});
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                    }}
                    .header-gradient-bar {{
                        height: 5px;
                        background: linear-gradient(90deg, {primary_color}, {secondary_color});
                        margin-top: 10px;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .info-section {{
                        background-color: #f9f9f9;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        border-left: 4px solid {primary_color};
                        border-right: 4px solid {secondary_color};
                    }}
                    .comment-content {{
                        border: 1px solid #ddd;
                        padding: 15px;
                        border-radius: 5px;
                        white-space: pre-wrap;
                        word-break: break-all;
                        margin-top: 10px;
                        line-height: 1.5;
                    }}
                    .current-comment {{
                        background-color: #f0f8ff;
                        border-left: 4px solid {primary_color};
                        border-right: 4px solid {secondary_color};
                    }}
                    .previous-comment {{
                        background-color: #f0f0f0;
                        border-left: 4px solid {primary_color};
                        border-right: 4px solid {secondary_color};
                    }}
                    .images-container {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        margin-top: 10px;
                    }}
                    .image-item {{
                        max-width: 300px;
                        max-height: 300px;
                        object-fit: contain;
                        border-radius: 5px;
                        border: 1px solid #ddd;
                    }}
                    .btn {{
                        display: inline-block;
                        margin-top: 10px;
                        background: linear-gradient(135deg, {primary_color}, {secondary_color});
                        color: #fff;
                        padding: 12px 24px;
                        border-radius: 5px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: all 0.3s ease;
                        border: none;
                        cursor: pointer;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    }}
                    .btn:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    }}
                    .action-section {{
                        text-align: center;
                        padding: 25px;
                        background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
                        border-radius: 8px;
                        margin: 20px 0;
                        border: 2px solid transparent;
                        border-image: linear-gradient(135deg, {primary_color}, {secondary_color});
                        border-image-slice: 1;
                    }}
                    .action-section p {{
                        font-size: 16px;
                        margin-bottom: 15px;
                        color: #333;
                    }}
                    .footer {{
                        text-align: center;
                        color: #999;
                        font-size: 12px;
                        margin-top: 20px;
                        padding: 20px;
                        border-top: 1px solid #eee;
                    }}
                    .time-badge {{
                        display: inline-block;
                        background: linear-gradient(135deg, {primary_color}, {secondary_color});
                        color: white;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 12px;
                        margin-left: 5px;
                    }}
                    .key-badge {{
                        display: inline-block;
                        background: linear-gradient(135deg, {primary_color}, {secondary_color});
                        color: white;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 16px;
                        margin-left: 5px;
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{UP_NAME} 动态置顶评论更新通知</h1>
                        <div class="header-gradient-bar"></div>
                    </div>

                    <div class="content">
                        <div class="info-section">
                            <span class="time-badge">📱 监测动态：</span></p>
                            <a href="https://t.bilibili.com/{dynamic_id}">
                            https://t.bilibili.com/{dynamic_id}</a></p>
                            <p><strong><span class="time-badge">⏰ 检测时间：</span></p> </strong>{current_time}
                        </div>

                        <div class="info-section">
                            <span class="key-badge">✨ 新置顶评论： ✨</span></p>
                            <div class="comment-content current-comment">
                                {current_html if current_html else "无置顶评论"}
                            </div>
            """

            # ✅ 新置顶评论图片
            if current_images:
                email_body += '<div class="images-container">'
                for img_url in current_images:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith(('http://', 'https://')):
                        img_url = 'https:' + img_url
                    email_body += f'<img class="image-item" src="{img_url}" alt="评论图片">'
                email_body += '</div>'

            email_body += f"""
                        </div>

                        <div class="info-section">
                            <span class="key-badge">📄 原置顶评论： 📄</span></p>
                            <div class="comment-content previous-comment">
                                {last_html if last_html else "无原置顶评论"}
                            </div>
            """

            # ✅ 原置顶评论图片
            if last_images:
                email_body += '<div class="images-container">'
                for img_url in last_images:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith(('http://', 'https://')):
                        img_url = 'https:' + img_url
                    email_body += f'<img class="image-item" src="{img_url}" alt="原评论图片">'
                email_body += '</div>'

            email_body += f"""
                        </div>

                        <!-- 独立的按钮区域 -->
                        <div class="action-section">
                            <p>点击下方按钮查看最新动态：</p>
                            <a class="btn" href="https://t.bilibili.com/{dynamic_id}?comment_on=1" target="_blank">
                                🔍 前往B站查看动态
                            </a>
                        </div>
                    </div>

                    <div class="footer">
                        <p>此邮件由动态监控系统自动发送，请勿回复</p>
                        <p>检测时间: {current_time}</p>
                         <p>本次随机主题色: {primary_color} → {secondary_color}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            return email_body
        except Exception as e:
            logger.error(f"❌ 渲染邮件内容失败: {e}")
            return f"<html><body><h1>渲染邮件内容出错: {e}</h1></body></html>"