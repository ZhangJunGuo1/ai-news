from enum import IntEnum

class NewsStatus(IntEnum):
    DRAFT = 0
    PUBLISHED = 1

    @classmethod
    def get_name(cls, value: int) -> str:
        names = {
            cls.DRAFT: '草稿',
            cls.PUBLISHED: '已发布'
        }
        return names.get(value, '未知')

    @classmethod
    def from_name(cls, name: str) -> int:
        mapping = {
            '草稿': cls.DRAFT,
            '已发布': cls.PUBLISHED
        }
        return mapping.get(name, cls.DRAFT)
