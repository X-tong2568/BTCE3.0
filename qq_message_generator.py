# qq_message_generator.py
from bs4 import BeautifulSoup
from logger_config import logger


class QQMessageGenerator:
    """QQ消息生成类"""

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
            qq_message = f"【{up_name}】瞳瞳空间更新啦~\n"
            qq_message += f"{text_content}\n"

            # 添加图片（如果有）
            if current_images:
                qq_message += "📸 图片：\n"
                # 限制最多发送9张图片，避免消息过长
                for i, img_url in enumerate(current_images[:9]):
                    # 使用CQ码发送图片
                    qq_message += f"[CQ:image,file={img_url}]\n"
                if len(current_images) > 9:
                    qq_message += f"... 还有 {len(current_images) - 9} 张图片\n"

            qq_message += "----------------\n"
            qq_message += f"📅 检测时间: {current_time}\n"
            qq_message += f"🔗 监测动态: https://t.bilibili.com/{dynamic_id}\n"
            qq_message += "----------------"

            return qq_message

        except Exception as e:
            logger.error(f"❌ 生成QQ消息失败: {e}")
            # 备用消息格式
            backup_msg = f"【{up_name}】置顶评论更新通知\n动态: {dynamic_id}\n时间: {current_time}"
            if current_images:
                backup_msg += f"\n包含 {len(current_images)} 张图片"
            return backup_msg