"""
AuthSystem — 纯 Python 内存实现的用户注册与登录系统。

业务规则:
  BR-01  年龄必须在 18 至 120 之间
  BR-02  密码长度 8-32 字符,且至少包含 1 位数字 + 1 位字母
  BR-03  邮箱必须包含 @ 和 .
  BR-04  用户名必须唯一,长度 3-20 字符
  BR-05  连续登录失败 5 次后账户锁定
  BR-06  锁定账户通过密码重置解锁

状态机: Guest → Registered → LoggedIn → Locked → Registered
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Literal


UserState = Literal["Registered", "LoggedIn", "Locked"]


@dataclass
class _User:
    username: str
    password: str
    age: int
    email: str
    state: UserState = "Registered"
    failed_attempts: int = 0


class AuthError(Exception):
    """AuthSystem 相关错误的基类。"""


class ValidationError(AuthError):
    """输入校验失败。"""


class UserNotFoundError(AuthError):
    """指定用户不存在。"""


class InvalidCredentialsError(AuthError):
    """密码错误。"""


class AccountLockedError(AuthError):
    """账户已锁定。"""


class UserAlreadyExistsError(AuthError):
    """用户名已注册。"""


class AuthSystem:
    """用户注册与登录系统。

    纯 Python 实现,使用 dict 在内存中存储用户数据,零外部依赖。
    适合作为 AutoTestDesign 工具的目标被测应用。
    """

    # ---------- 校验规则 ----------

    @staticmethod
    def validate_age(age: int) -> None:
        """BR-01: 年龄必须在 18 至 120 之间。"""
        if not (18 <= age <= 120):
            raise ValidationError(f"年龄必须在 18 至 120 之间,实际值: {age}")

    @staticmethod
    def validate_password(password: str) -> None:
        """BR-02: 密码长度 8-32,且至少包含 1 位数字 + 1 位字母。"""
        if not (8 <= len(password) <= 32):
            raise ValidationError(f"密码长度必须为 8-32 字符,实际长度: {len(password)}")
        if not re.search(r"\d", password):
            raise ValidationError("密码必须至少包含 1 位数字")
        if not re.search(r"[a-zA-Z]", password):
            raise ValidationError("密码必须至少包含 1 位字母")

    @staticmethod
    def validate_email(email: str) -> None:
        """BR-03: 邮箱必须包含 @ 和 .。"""
        if "@" not in email or "." not in email:
            raise ValidationError(f"邮箱格式无效,必须包含 @ 和 .: {email}")

    @staticmethod
    def validate_username(username: str) -> None:
        """BR-04 前半: 用户名长度 3-20 字符。"""
        if not (3 <= len(username) <= 20):
            raise ValidationError(f"用户名长度必须为 3-20 字符,实际长度: {len(username)}")

    # ---------- 核心操作 ----------

    def __init__(self) -> None:
        self._users: dict[str, _User] = {}

    def register(self, username: str, password: str, age: int, email: str) -> None:
        """注册新用户。

        Raises:
            ValidationError: 输入校验失败时抛出。
            UserAlreadyExistsError: 用户名已存在时抛出。
        """
        self.validate_username(username)
        if username in self._users:
            raise UserAlreadyExistsError(f"用户名已注册: {username}")
        self.validate_password(password)
        self.validate_age(age)
        self.validate_email(email)

        self._users[username] = _User(
            username=username,
            password=password,
            age=age,
            email=email,
            state="Registered",
            failed_attempts=0,
        )

    def login(self, username: str, password: str) -> None:
        """用户登录。

        Raises:
            UserNotFoundError: 用户不存在。
            AccountLockedError: 账户已锁定 (BR-05)。
            InvalidCredentialsError: 密码错误。
        """
        if username not in self._users:
            raise UserNotFoundError(f"用户不存在: {username}")

        user = self._users[username]

        if user.state == "Locked":
            raise AccountLockedError(f"账户已锁定: {username},请重置密码后重试")

        if user.password != password:
            user.failed_attempts += 1
            # BR-05: 5 次连续失败 → 锁定
            if user.failed_attempts >= 5:
                user.state = "Locked"
                raise AccountLockedError(
                    f"连续登录失败 {user.failed_attempts} 次,账户已锁定: {username}"
                )
            raise InvalidCredentialsError("密码错误,登录失败")

        # 登录成功,重置失败计数
        user.failed_attempts = 0
        user.state = "LoggedIn"

    def logout(self, username: str) -> None:
        """用户登出,回到 Registered 状态。

        Raises:
            UserNotFoundError: 用户不存在。
        """
        if username not in self._users:
            raise UserNotFoundError(f"用户不存在: {username}")

        user = self._users[username]
        if user.state == "LoggedIn":
            user.state = "Registered"

    def reset_password(self, username: str, new_password: str) -> None:
        """重置密码并解锁账户 (BR-06)。

        Raises:
            UserNotFoundError: 用户不存在。
            ValidationError: 新密码不符合规则。
        """
        if username not in self._users:
            raise UserNotFoundError(f"用户不存在: {username}")

        self.validate_password(new_password)

        user = self._users[username]
        user.password = new_password
        user.failed_attempts = 0
        user.state = "Registered"

    def get_user_state(self, username: str) -> UserState:
        """获取用户当前状态。

        Raises:
            UserNotFoundError: 用户不存在。
        """
        if username not in self._users:
            raise UserNotFoundError(f"用户不存在: {username}")
        return self._users[username].state

    def get_failed_attempts(self, username: str) -> int:
        """获取当前连续失败次数。

        Raises:
            UserNotFoundError: 用户不存在。
        """
        if username not in self._users:
            raise UserNotFoundError(f"用户不存在: {username}")
        return self._users[username].failed_attempts

    @property
    def user_count(self) -> int:
        """已注册用户总数。"""
        return len(self._users)
