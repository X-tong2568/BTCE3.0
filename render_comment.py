# comment_renderer.py
import time
import asyncio
from bs4 import BeautifulSoup
from config import UP_NAME
from logger_config import logger
from datetime import datetime


class CommentRenderer:
    """评论渲染和变化检测类"""

    @staticmethod
    def extract_text_from_html(html_content: str) -> str:
        """从HTML提取纯文字"""
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(strip=True)

    async def get_pinned_comment(self, page, dynamic_id):
        """
        抓取置顶评论：
        - pinned_comment_html: 评论 HTML（含文字+表情）
        - comment_images: 评论区上传的图片 URL 列表
        """
        await page.goto(f"https://t.bilibili.com/{dynamic_id}")

        try:
            await page.wait_for_selector("bili-comment-thread-renderer", timeout=15000)
        except:
            return "未找到置顶评论", []

        # 模拟滚动加载更多评论
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        pinned_comment_html = None
        comment_images = []

        comment_items = await page.query_selector_all("bili-comment-thread-renderer")
        for item in comment_items:
            top_tag = await item.query_selector("i#top")
            if top_tag:
                # 文字+表情 HTML
                content_element = await item.query_selector("bili-rich-text p#contents")
                if content_element:
                    pinned_comment_html = await content_element.inner_html()

                # 评论区上传图片 - 修复图片获取逻辑
                pics_renderer = await item.query_selector("bili-comment-pictures-renderer")
                if pics_renderer:
                    try:
                        # 使用 evaluate 方法访问 shadow DOM
                        img_src_list = await pics_renderer.evaluate(
                            """(el) => {
                                const imgs = [];
                                const shadow = el.shadowRoot;
                                if (shadow) {
                                    const img_tags = shadow.querySelectorAll('img');
                                    img_tags.forEach(img => {
                                        let src = img.src;
                                        if (src.startsWith('//')) {
                                            src = 'https:' + src;
                                        }
                                        // 移除图片参数，获取原始图片
                                        if (src.includes('@')) {
                                            src = src.split('@')[0];
                                        }
                                        imgs.push(src);
                                    });
                                }
                                return imgs;
                            }"""
                        )
                        comment_images.extend(img_src_list)
                    except Exception as e:
                        logger.error(f"❌❌ 通过shadow DOM获取图片失败: {e}")

                        # 备用方法：尝试直接获取图片元素
                        try:
                            img_elements = await pics_renderer.query_selector_all('img')
                            for img in img_elements:
                                src = await img.get_attribute('src')
                                if src:
                                    if src.startswith('//'):
                                        src = 'https:' + src
                                    if '@' in src:
                                        src = src.split('@')[0]
                                    if src not in comment_images:
                                        comment_images.append(src)
                        except Exception as e2:
                            logger.error(f"❌❌ 直接获取图片元素失败: {e2}")

                break

        if pinned_comment_html:
            return pinned_comment_html.strip(), comment_images
        return "未找到置顶评论", []

    async def detect_comment_change(self, current_html, current_images, last_html, last_images):
        """检测评论变化"""
        try:
            current_text = self.extract_text_from_html(current_html)
            last_text = self.extract_text_from_html(last_html)

            logger.info(f"当前置顶评论: {current_text}")
            logger.info(f"上次记录: {last_text if last_text else '无记录'}")

            # 检测文字变化
            if last_text and current_text != last_text:
                logger.info("🔔🔔 检测到置顶评论文字变化！")
                return True

            # 检测图片变化
            if set(current_images) != set(last_images):
                logger.info("🔔🔔 检测到置顶评论图片变化！")
                return True

            return False

        except Exception as e:
            logger.error(f"❌❌ 检测评论变化失败: {e}")
            return False

    def render_email_content(self, dynamic_id, current_html, current_images, last_html, last_images, current_time=None):
        """渲染邮件内容 - 修复图片显示问题"""
        try:
            if current_time is None:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')

            primary_color = "#2196F3"
            secondary_color = "#1976D2"
            status_color = "#2196F3"

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
                    .content {{
                        padding: 30px;
                    }}
                    .info-section {{
                        background-color: #f9f9f9;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                    }}
                    .comment-content {{
                        border: 1px solid #ddd;
                        padding: 15px;
                        border-radius: 5px;
                        white-space: pre-wrap;
                        word-break: break-all;
                        margin-top: 10px;
                    }}
                    .current-comment {{
                        background-color: #f0f8ff;
                    }}
                    .previous-comment {{
                        background-color: #f0f0f0;
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
                    .footer {{
                        text-align: center;
                        color: #999;
                        font-size: 12px;
                        margin-top: 20px;
                        padding: 20px;
                        border-top: 1px solid #eee;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{UP_NAME}动态置顶评论更新通知</h1>
                    </div>

                    <div class="content">

                        <div class="info-section">
                            <p><strong>监测动态：</strong>
                            <a href="https://t.bilibili.com/{dynamic_id}">
                            https://t.bilibili.com/{dynamic_id}</a></p>
                            <p><strong>检测时间：</strong>{current_time}</p>
                        </div>

                        <div class="info-section">
                            <p><strong>新置顶评论：</strong></p>
                            <div class="comment-content current-comment">
                                {current_html if current_html else "无置顶评论"}
                            </div>
            """

            # ✅ 新置顶评论图片（关键修复点）
            if current_images:
                email_body += '<div class="images-container">'
                for img_url in current_images:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith(('http://', 'https://')):
                        img_url = 'https:' + img_url

                    email_body += f'''
                    <img class="image-item" src="{img_url}" alt="评论图片">
                    '''
                email_body += '</div>'

            email_body += f"""
                        </div>

                        <div class="info-section">
                            <p><strong>原置顶评论：</strong></p>
                            <div class="comment-content previous-comment">
                                {last_html if last_html else "无原置顶评论"}
                            </div>
            """

            # ✅ 原置顶评论图片（同样修复）
            if last_images:
                email_body += '<div class="images-container">'
                for img_url in last_images:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith(('http://', 'https://')):
                        img_url = 'https:' + img_url

                    email_body += f'''
                    <img class="image-item" src="{img_url}" alt="原评论图片">
                    '''
                email_body += '</div>'

            email_body += f"""
                        </div>
                    </div>

                    <div class="footer">
                        <p>此邮件由动态监控系统自动发送，请勿回复</p>
                        <p>{current_time}</p>
                    </div>
                </div>
            </body>
            </html>
            """

            return email_body

        except Exception as e:
            logger.error(f"❌ 渲染邮件内容失败: {e}")
            return f"<html><body><h1>渲染邮件内容出错: {e}</h1></body></html>"

    def generate_qq_message(self, up_name: str, dynamic_id: str, current_html: str, current_time: str,
                            current_images: list) -> str:
        """生成QQ群推送消息（纯文本，表情转为alt文字，图片使用CQ码）"""
        try:
            # 使用BeautifulSoup处理HTML，将表情图片替换为alt文字
            soup = BeautifulSoup(current_html, "html.parser")

            # 找到所有表情图片，替换为alt属性中的文字
            for img in soup.find_all("img"):
                alt_text = img.get("alt", "")
                if alt_text:
                    # 用alt文字替换图片
                    img.replace_with(alt_text)
                else:
                    # 如果没有alt属性，移除图片
                    img.decompose()

            # 提取纯文本内容
            text_content = soup.get_text(strip=True)

            # 生成QQ消息
            qq_message = f"【{up_name}】动态置顶评论更新啦~\n"
            qq_message += f"{text_content}\n"

            # 添加图片（如果有）
            if current_images:
                qq_message += "📸 图片：\n"
                # 限制最多发送3张图片，避免消息过长
                for i, img_url in enumerate(current_images[:3]):
                    # 使用CQ码发送图片
                    qq_message += f"[CQ:image,file={img_url}]\n"
                if len(current_images) > 3:
                    qq_message += f"... 还有 {len(current_images) - 3} 张图片\n"

            qq_message += "----------------\n"
            qq_message += f"📅 检测时间: {current_time}\n"
            qq_message += f"🔗 监测动态: https://t.bilibili.com/{dynamic_id}\n"
            qq_message += "----------------"

            return qq_message

        except Exception as e:
            logger.error(f"❌❌❌❌ 生成QQ消息失败: {e}")
            # 备用消息格式
            backup_msg = f"【{up_name}】置顶评论更新通知\n动态: {dynamic_id}\n时间: {current_time}"
            if current_images:
                backup_msg += f"\n包含 {len(current_images)} 张图片"
            return backup_msg
