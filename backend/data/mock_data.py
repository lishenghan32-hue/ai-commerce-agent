"""
Mock data for product parsing fallback
Used when parsing fails or platform is not supported
"""
from typing import Dict, List


def get_mock_data(platform: str) -> Dict:
    """Get mock data based on platform"""

    mock_data = {
        "taobao": {
            "name": "美白精华液",
            "selling_points": "美白提亮，28天见效，温和不刺激",
            "comments": ["用了皮肤确实变白了", "就是价格有点贵", "包装很高大上", "用了一周效果不明显", "会回购的"]
        },
        "tmall": {
            "name": "美白精华液",
            "selling_points": "美白提亮，28天见效，温和不刺激",
            "comments": ["用了皮肤确实变白了", "就是价格有点贵", "包装很高大上", "用了一周效果不明显", "会回购的"]
        },
        "douyin": {
            "name": "无线蓝牙耳机",
            "selling_points": "主动降噪，30小时续航，Hi-Fi音质",
            "comments": ["音质真的很不错", "电池续航一般般", "操作很简单", "比实体店便宜", "售后态度很好"]
        },
        "jd": {
            "name": "智能手环",
            "selling_points": "心率监测，睡眠追踪，防水设计",
            "comments": ["功能很全面", "续航一周没问题", "佩戴舒服", "数据不太准", "性价比高"]
        },
        "pinduoduo": {
            "name": "实用小商品",
            "selling_points": "性价比高，实用性强",
            "comments": ["价格实惠", "质量一般", "物流很快", "包装简陋", "值得购买"]
        },
        "unknown": {
            "name": "通用商品",
            "selling_points": "高品质，性价比高，实用性强",
            "comments": ["质量很好", "发货速度快", "包装完好", "性价比不错", "会推荐给朋友"]
        }
    }

    return mock_data.get(platform, mock_data["unknown"])


def get_all_platforms() -> List[str]:
    """Get list of supported platforms"""
    return ["taobao", "tmall", "douyin", "jd", "pinduoduo", "unknown"]
