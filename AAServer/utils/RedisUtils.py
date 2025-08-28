#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : RedisUtils.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/6 17:32 
@Version : 1.0
"""
import orjson

from typing import Any, Iterable

class RedisUtil:
    """
    轻量级 Redis 工具类
    说明：
    1) 所有网络/序列化异常由全局异常处理器接管。
    2) 空键返回 None，避免抛错。
    3) keys 结果统一解码为 str 列表。
    """

    def __init__(self, redis_client) -> None:
        """
        :param redis_client: redis.Redis 实例
        """
        self.conn = redis_client

    # ---------- string ----------
    def set_value(self, key: str, value: str, timeout: int | None = None) -> bool:
        """
        写入字符串/数值
        :param timeout: 秒；None 表示永不过期
        :return: True/False
        """
        return bool(self.conn.set(key, value, ex=timeout))

    def get_value(self, key: str) -> str | None:
        """
        读取字符串
        :return: str 或 None（键不存在）
        """
        val = self.conn.get(key)
        return val.decode() if val else None

    def delete_value(self, key: str) -> int:
        """
        删除键
        :return: 删除条数
        """
        return self.conn.delete(key)

    def get_all_keys(self, pattern: str = "*") -> list[str]:
        """
        按通配符获取所有 key
        :return: list[str]
        """
        keys = self.conn.keys(pattern)
        return [k.decode() for k in keys]

        # ---------- 对象 ----------

    def set_object(self, key: str, obj: Any, timeout: int | None = None) -> bool:
        """
        支持 datetime / UUID / Decimal / dataclass / numpy.ndarray 等
        """
        return bool(
            self.conn.set(key, orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS), ex=timeout)
        )

    def get_object(self, key: str) -> Any:
        """
        反序列化 JSON → Python 对象
        :return: 对象 or None（键不存在）
        """
        val = self.conn.get(key)
        if val is None:
            return None
        return orjson.loads(val)  # orjson.loads 接受 bytes 或 str

        # ---------- 批量 ----------

    def mget_objects(self, keys: Iterable[str]) -> list[Any]:
        """
        批量读取对象
        """
        raw_vals = self.conn.mget(keys)
        return [orjson.loads(v) if v else None for v in raw_vals]

class CacheKeys:
    TOKEN_USER = 'AUTH:TOKEN_USER:'          # token对应的用户信息缓存
    USER_PERMISSIONS = 'AUTH:USER_PERMISSION:'  # 用户权限缓存

    USER_INFO = 'USER:USER_INFO:'  # 用户信息缓存
    PERMISSION_TREE = 'PERM:PERMISSION_TREE'