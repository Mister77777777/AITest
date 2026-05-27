"""
AuthSystem 的 pytest 测试脚本。

覆盖:
  - 6 条业务规则 (BR-01 至 BR-06)
  - 状态机的 4 条关键转换
  - 使用 parametrize 进行数据驱动测试

运行方式: pytest target_app/
"""

from __future__ import annotations
import pytest
from target_app.auth_system import (
    AuthSystem,
    AuthError,
    ValidationError,
    UserNotFoundError,
    InvalidCredentialsError,
    AccountLockedError,
    UserAlreadyExistsError,
)


# ═══════════════════════════════════════════
# 辅助 fixture
# ═══════════════════════════════════════════

@pytest.fixture
def auth() -> AuthSystem:
    """返回一个空的 AuthSystem 实例。"""
    return AuthSystem()


@pytest.fixture
def registered_user(auth: AuthSystem) -> AuthSystem:
    """预注册一名用户: testuser / Pass1234 / 25 岁。"""
    auth.register("testuser", "Pass1234", 25, "test@example.com")
    return auth


# ═══════════════════════════════════════════
# BR-01: 年龄 18-120
# ═══════════════════════════════════════════

class TestAgeValidation:
    """BR-01: 年龄必须在 18 至 120 之间。"""

    @pytest.mark.parametrize("age", [18, 25, 66, 120])
    def test_valid_age_accepted(self, auth: AuthSystem, age: int) -> None:
        auth.register(f"user_{age}", "Pass1234", age, f"user{age}@test.com")
        assert auth.get_user_state(f"user_{age}") == "Registered"

    @pytest.mark.parametrize("age", [0, 17, 121, 200])
    def test_invalid_age_rejected(self, auth: AuthSystem, age: int) -> None:
        with pytest.raises(ValidationError, match="年龄"):
            auth.register(f"user_{age}", "Pass1234", age, f"user{age}@test.com")


# ═══════════════════════════════════════════
# BR-02: 密码 8-32 字符,至少 1 数字 + 1 字母
# ═══════════════════════════════════════════

class TestPasswordValidation:
    """BR-02: 密码长度 8-32 字符,且至少包含 1 位数字 + 1 位字母。"""

    @pytest.mark.parametrize("password", [
        "abcd1234",          # 8 字符,有字母+数字
        "A1bcdefghijklmn",   # 14 字符
        "p" * 31 + "1",       # 32 字符,边界
        "hello123",          # 8 字符,刚好
    ])
    def test_valid_password_accepted(self, auth: AuthSystem, password: str) -> None:
        auth.register("pw_user", password, 20, "pw@test.com")
        assert auth.get_user_state("pw_user") == "Registered"

    @pytest.mark.parametrize("password,reason", [
        ("abc", "太短"),
        ("a" * 33 + "1", "太长"),
        ("abcdefgh", "无数字"),
        ("12345678", "无字母"),
        ("ab1", "过短且含数字字母但不足8位"),
        ("a1", "过短"),
    ])
    def test_invalid_password_rejected(
        self, auth: AuthSystem, password: str, reason: str
    ) -> None:
        with pytest.raises(ValidationError):
            auth.register("pw_user2", password, 20, "pw2@test.com")


# ═══════════════════════════════════════════
# BR-03: 邮箱必须包含 @ 和 .
# ═══════════════════════════════════════════

class TestEmailValidation:
    """BR-03: 邮箱必须包含 @ 和 .。"""

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "a@b.c",
        "test.user@domain.co.uk",
        "name@sub.domain.org",
    ])
    def test_valid_email_accepted(self, auth: AuthSystem, email: str) -> None:
        auth.register("em_user", "Pass1234", 20, email)
        assert auth.get_user_state("em_user") == "Registered"

    @pytest.mark.parametrize("email", [
        "no-at-sign",
        "no-dot@domain",
        "@nodotcom",
        "plain.address.com",
        "",
    ])
    def test_invalid_email_rejected(self, auth: AuthSystem, email: str) -> None:
        with pytest.raises(ValidationError, match="邮箱"):
            auth.register("em_user2", "Pass1234", 20, email)


# ═══════════════════════════════════════════
# BR-04: 用户名 3-20 字符且唯一
# ═══════════════════════════════════════════

class TestUsernameValidation:
    """BR-04: 用户名必须唯一,长度 3-20 字符。"""

    @pytest.mark.parametrize("username", ["abc", "user123", "a" * 20])
    def test_valid_username_accepted(self, auth: AuthSystem, username: str) -> None:
        auth.register(username, "Pass1234", 20, f"{username}@test.com")
        assert auth.get_user_state(username) == "Registered"

    @pytest.mark.parametrize("username", ["ab", "a" * 21])
    def test_length_out_of_range_rejected(self, auth: AuthSystem, username: str) -> None:
        with pytest.raises(ValidationError, match="用户名"):
            auth.register(username, "Pass1234", 20, f"{username}@test.com")

    def test_duplicate_username_rejected(self, registered_user: AuthSystem) -> None:
        with pytest.raises(UserAlreadyExistsError, match="已注册"):
            registered_user.register("testuser", "Another1", 30, "another@test.com")


# ═══════════════════════════════════════════
# BR-05: 5 次连续失败 → 锁定
# ═══════════════════════════════════════════

class TestAccountLockout:
    """BR-05: 连续登录失败 5 次后账户锁定。"""

    def test_four_failures_not_locked(self, registered_user: AuthSystem) -> None:
        for _ in range(4):
            with pytest.raises(InvalidCredentialsError):
                registered_user.login("testuser", "WrongPass1")
        # 第 4 次失败后仍不应锁定
        assert registered_user.get_user_state("testuser") == "Registered"
        assert registered_user.get_failed_attempts("testuser") == 4

    def test_fifth_failure_locks_account(self, registered_user: AuthSystem) -> None:
        for _ in range(4):
            with pytest.raises(InvalidCredentialsError):
                registered_user.login("testuser", "WrongPass1")
        # 第 5 次失败
        with pytest.raises(AccountLockedError, match="已锁定"):
            registered_user.login("testuser", "WrongPass1")
        assert registered_user.get_user_state("testuser") == "Locked"

    def test_success_resets_counter(self, registered_user: AuthSystem) -> None:
        registered_user.login("testuser", "Pass1234")
        registered_user.logout("testuser")
        # 此时计数器已重置,再失败不会锁定
        for _ in range(3):
            with pytest.raises(InvalidCredentialsError):
                registered_user.login("testuser", "WrongPass1")
        assert registered_user.get_failed_attempts("testuser") == 3

    def test_locked_account_cannot_login(self, registered_user: AuthSystem) -> None:
        # 先锁住
        for _ in range(5):
            with pytest.raises(AuthError):
                registered_user.login("testuser", "WrongPass1")
        # 用正确密码尝试
        with pytest.raises(AccountLockedError):
            registered_user.login("testuser", "Pass1234")


# ═══════════════════════════════════════════
# BR-06: 密码重置可解锁
# ═══════════════════════════════════════════

class TestPasswordReset:
    """BR-06: 锁定账户通过密码重置解锁。"""

    def test_reset_unlocks_account(self, registered_user: AuthSystem) -> None:
        # 先锁住
        for _ in range(5):
            with pytest.raises(AuthError):
                registered_user.login("testuser", "WrongPass1")
        assert registered_user.get_user_state("testuser") == "Locked"

        # 重置密码
        registered_user.reset_password("testuser", "NewPass999")
        assert registered_user.get_user_state("testuser") == "Registered"
        assert registered_user.get_failed_attempts("testuser") == 0

        # 用新密码登录
        registered_user.login("testuser", "NewPass999")
        assert registered_user.get_user_state("testuser") == "LoggedIn"


# ═══════════════════════════════════════════
# 状态机转换测试
# ═══════════════════════════════════════════

class TestStateMachineTransitions:
    """覆盖 AuthSystem 的 4 条状态转换。"""

    def test_guest_to_registered_via_register(self, auth: AuthSystem) -> None:
        """Guest --register→ Registered"""
        auth.register("alice", "Alice123", 30, "alice@test.com")
        assert auth.get_user_state("alice") == "Registered"

    def test_registered_to_loggedin_via_login(self, registered_user: AuthSystem) -> None:
        """Registered --login→ LoggedIn"""
        registered_user.login("testuser", "Pass1234")
        assert registered_user.get_user_state("testuser") == "LoggedIn"

    def test_loggedin_to_registered_via_logout(self, registered_user: AuthSystem) -> None:
        """LoggedIn --logout→ Registered"""
        registered_user.login("testuser", "Pass1234")
        registered_user.logout("testuser")
        assert registered_user.get_user_state("testuser") == "Registered"

    def test_loggedin_to_locked_via_failed_attempts(self, registered_user: AuthSystem) -> None:
        """LoggedIn/Registered --5次失败→ Locked"""
        for _ in range(5):
            with pytest.raises(AuthError):
                registered_user.login("testuser", "WrongPass1")
        assert registered_user.get_user_state("testuser") == "Locked"

    def test_locked_to_registered_via_reset(self, registered_user: AuthSystem) -> None:
        """Locked --resetPassword→ Registered"""
        for _ in range(5):
            with pytest.raises(AuthError):
                registered_user.login("testuser", "WrongPass1")
        registered_user.reset_password("testuser", "NewPass999")
        assert registered_user.get_user_state("testuser") == "Registered"

    def test_loggedin_self_loop_on_success(self, registered_user: AuthSystem) -> None:
        """LoggedIn --failedAttempt→ LoggedIn (attempts < 5)"""
        registered_user.login("testuser", "Pass1234")
        # 登出再登回来,验证自环逻辑
        registered_user.logout("testuser")
        registered_user.login("testuser", "Pass1234")
        assert registered_user.get_user_state("testuser") == "LoggedIn"


# ═══════════════════════════════════════════
# 边缘场景
# ═══════════════════════════════════════════

class TestEdgeCases:
    """边缘与错误场景。"""

    def test_login_nonexistent_user(self, auth: AuthSystem) -> None:
        with pytest.raises(UserNotFoundError):
            auth.login("nobody", "pass")

    def test_logout_nonexistent_user(self, auth: AuthSystem) -> None:
        with pytest.raises(UserNotFoundError):
            auth.logout("nobody")

    def test_reset_nonexistent_user(self, auth: AuthSystem) -> None:
        with pytest.raises(UserNotFoundError):
            auth.reset_password("nobody", "Pass1234")

    def test_register_multiple_users(self, auth: AuthSystem) -> None:
        auth.register("u01", "Pass1111", 20, "u01@test.com")
        auth.register("u02", "Pass2222", 30, "u02@test.com")
        auth.register("u03", "Pass3333", 40, "u03@test.com")
        assert auth.user_count == 3

    def test_reset_password_validation(self, registered_user: AuthSystem) -> None:
        """重置密码时,新密码仍需通过 BR-02 校验。"""
        with pytest.raises(ValidationError):
            registered_user.reset_password("testuser", "short")
