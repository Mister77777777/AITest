from __future__ import annotations
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.llm.client import LLMClient
from autotestdesign.core.pipeline import run_pipeline
from autotestdesign.core.models import TestCase
from autotestdesign.ui.state import get_session, render_workset_chip
from autotestdesign.ui.state_diagram import render_state_diagram_section


def _build_llm_or_none():
    """构建 LLM 客户端,无 API Key 时返回 None(退化到规则/算法兜底)。"""
    try:
        cfg = load_config()
        if not cfg.api_key:
            return None
        return LLMClient(cfg)
    except Exception:
        return None


def render_test_design_tab() -> None:
    """FR3/FR4/FR5/FR7 面板:配置 → 覆盖项/策略编辑 → 运行 → 交互式用例编辑。"""
    session = get_session()
    render_workset_chip()
    st.markdown(
        '<div class="atd-section">FR3 · FR4 · FR5 · FR7 · 测试设计</div>'
        '<h2>流水线配置与结果</h2>',
        unsafe_allow_html=True,
    )

    if not session.requirements:
        st.info("请先在「需求录入」页载入或输入需求。")
        return

    # ---------- 策略编辑区 ----------
    with st.expander("覆盖策略设置", expanded=False):
        st.caption("在运行流水线前调整测试策略。")
        st_cols = st.columns(4, gap="medium")
        with st_cols[0]:
            ep_enabled = st.checkbox("等价类 (EP)", value=True)
        with st_cols[1]:
            bva_enabled = st.checkbox("边界值 (BVA)", value=True)
        with st_cols[2]:
            dt_enabled = st.checkbox("判定表 (DT)", value=True)
        with st_cols[3]:
            stt_enabled = st.checkbox("状态转换 (STT)", value=True)

    # ---------- 顶部配置栏 ----------
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="medium")
    with c1:
        use_llm = st.toggle("启用 LLM", value=True, help="用 LLM 生成风险理由与 Oracle")
    with c2:
        include_stt = st.checkbox("状态转换 (FR4)", value=True)
    with c3:
        max_cases = st.number_input("最大用例数", min_value=0, value=0, help="0 = 不限")
    with c4:
        stt_req_id = st.selectbox(
            "状态机挂载 ID",
            options=[r.id for r in session.requirements],
            disabled=not include_stt,
        )

    sm = None
    if include_stt:
        st.write("")
        st.markdown('<div class="atd-section">状态机 DSL</div>', unsafe_allow_html=True)
        sm = render_state_diagram_section()

    # ---------- 运行入口卡片 ----------
    st.markdown(
        f"""
        <div class="atd-runcard">
          <div class="atd-runcard-title">▶ 运行完整流水线</div>
          <div class="atd-runcard-sub">
            将依序执行:LLM 自动结构化 → 风险打分 → 等价类 / 边界值 / 判定表
            {'→ 状态转换覆盖' if include_stt else ''} → Oracle 合成 → 加权覆盖优化。
            共 {len(session.requirements)} 条需求,{'LLM 已启用' if use_llm else 'LLM 已关闭(规则兜底)'}。
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    run = st.button(
        "开始运行",
        type="primary",
        use_container_width=True,
        key="run_pipeline_btn",
    )

    status_placeholder = st.empty()

    if run:
        with status_placeholder.status("正在运行流水线…", expanded=True) as status:
            llm = _build_llm_or_none() if use_llm else None
            t0 = time.time()
            st.write("① 初始化 LLM 客户端" if llm else "① LLM 已关闭,走规则兜底")
            st.write(f"② 对 {len(session.requirements)} 条需求进行结构化与风险打分")
            st.write("③ 生成等价类 / 边界值 / 判定表用例")
            if include_stt and sm:
                st.write(f"④ 状态转换覆盖(挂载 {stt_req_id})")
            st.write("⑤ 合成 Oracle 并按风险优先级优化")

            try:
                suite = run_pipeline(
                    session.requirements,
                    llm=llm,
                    state_machine=sm,
                    state_machine_requirement_id=stt_req_id if include_stt else None,
                    optimize_max_cases=max_cases or None,
                )
                # 按策略过滤技术
                enabled_techs = []
                if ep_enabled:
                    enabled_techs.append("EP")
                if bva_enabled:
                    enabled_techs.append("BVA")
                if dt_enabled:
                    enabled_techs.append("DT")
                if stt_enabled and include_stt:
                    enabled_techs.append("STT")
                if enabled_techs:
                    suite.cases = [c for c in suite.cases if c.technique in enabled_techs]

                session.suite = suite
                # 初始化编辑快照
                st.session_state["edited_cases"] = None
                elapsed = time.time() - t0
                status.update(
                    label=f"完成 · 生成 {len(suite.cases)} 条用例 · 耗时 {elapsed:.1f}s",
                    state="complete",
                    expanded=False,
                )
            except Exception as e:
                status.update(label=f"运行失败:{e}", state="error", expanded=True)
                return

    if not session.suite:
        return

    # ---------- 覆盖项概览 ----------
    st.write("")
    st.markdown('<div class="atd-section">覆盖项概览</div>', unsafe_allow_html=True)

    _render_coverage_items(session)

    # ---------- 交互式用例编辑 ----------
    st.write("")
    st.markdown('<div class="atd-section">交互式用例编辑</div>', unsafe_allow_html=True)
    st.caption("双击单元格可编辑。修改后可通过导出页下载更新后的套件。")

    _render_editable_case_grid(session)


# ═══════════════════════════════════════════
# 覆盖项可视化
# ═══════════════════════════════════════════

def _render_coverage_items(session) -> None:
    """显示每个需求在各技术下的覆盖项数量,支持增删覆盖项。"""
    suite = session.suite
    req_ids = sorted(set(c.requirement_id for c in suite.cases))

    rows = []
    for rid in req_ids:
        cases_for_req = [c for c in suite.cases if c.requirement_id == rid]
        by_tech = {"EP": 0, "BVA": 0, "DT": 0, "STT": 0}
        for c in cases_for_req:
            by_tech[c.technique] = by_tech.get(c.technique, 0) + 1
        rows.append({
            "需求 ID": rid,
            "EP": by_tech["EP"],
            "BVA": by_tech["BVA"],
            "DT": by_tech["DT"],
            "STT": by_tech["STT"],
            "合计": len(cases_for_req),
            "覆盖状态": "✅ 已覆盖" if sum(by_tech.values()) > 0 else "❌ 未覆盖",
        })

    df_cov = pd.DataFrame(rows)
    col1, col2 = st.columns([3, 1], gap="medium")
    with col1:
        st.dataframe(df_cov, use_container_width=True, hide_index=True, height=(len(rows) + 1) * 35 + 3)
    with col2:
        st.metric("需求覆盖", f"{len(req_ids)}/{len(session.requirements)}")
        total_tech = sum(
            1 for t in ["EP", "BVA", "DT", "STT"]
            if any(c.technique == t for c in suite.cases)
        )
        st.metric("使用技术", str(total_tech))
        st.metric("用例总数", str(len(suite.cases)))

    # 手动添加覆盖项
    with st.expander("添加覆盖项", expanded=False):
        ac1, ac2, ac3 = st.columns(3, gap="small")
        with ac1:
            new_req = st.selectbox("挂载需求", options=req_ids, key="cov_new_req")
        with ac2:
            new_tech = st.selectbox("测试技术", options=["EP", "BVA", "DT", "STT"], key="cov_new_tech")
        with ac3:
            new_input = st.text_input("输入值 (key=val, 逗号分隔)", placeholder="age=25, password=Test1234",
                                       key="cov_new_input")

        if st.button("新增覆盖项", type="secondary"):
            inputs = _parse_input_str(new_input)
            case = TestCase(
                id=f"MAN-{new_tech}-{len(suite.cases) + 1:03d}",
                requirement_id=new_req,
                technique=new_tech,
                inputs=inputs,
                expected_result="[手动添加] 请编辑预期结果",
                priority="Medium",
                tags=["手动添加"],
            )
            suite.cases.append(case)
            st.session_state["edited_cases"] = None
            st.rerun()


# ═══════════════════════════════════════════
# 交互式用例编辑网格
# ═══════════════════════════════════════════

def _render_editable_case_grid(session) -> None:
    """使用 st.data_editor 提供可编辑的测试用例表格。

    支持的操作:
      - 修改输入值、预期结果、优先级、标签
      - 删除用例(选中行后点击删除按钮)
      - 新增用例(点击新增按钮)
      - 修改自动同步到 session.suite
    """
    suite = session.suite

    # 构建可编辑 DataFrame
    cases_data = []
    for i, c in enumerate(suite.cases):
        cases_data.append({
            "_idx": i,
            "ID": c.id,
            "需求": c.requirement_id,
            "技术": c.technique,
            "优先级": c.priority,
            "输入": ", ".join(f"{k}={v}" for k, v in c.inputs.items()),
            "预期结果": c.expected_result,
            "前置条件": "; ".join(c.preconditions),
            "标签": ", ".join(c.tags),
        })

    df = pd.DataFrame(cases_data)

    # 使用 data_editor 实现交互式编辑
    edited_df = st.data_editor(
        df,
        column_config={
            "_idx": st.column_config.NumberColumn("序号", disabled=True),
            "ID": st.column_config.TextColumn("ID", disabled=True, width="small"),
            "需求": st.column_config.TextColumn("需求", disabled=True, width="small"),
            "技术": st.column_config.TextColumn("技术", disabled=True, width="small"),
            "优先级": st.column_config.SelectboxColumn(
                "优先级",
                options=["High", "Medium", "Low"],
                width="small",
                help="修改测试用例优先级",
            ),
            "输入": st.column_config.TextColumn("输入", width="medium", help="格式: key=val, key=val"),
            "预期结果": st.column_config.TextColumn("预期结果", width="large", help="编辑预期结果"),
            "前置条件": st.column_config.TextColumn("前置条件", width="medium"),
            "标签": st.column_config.TextColumn("标签", width="medium"),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",  # 允许用户直接在表格底部添加行
        key="case_editor",
    )

    # 按钮行
    b1, b2, b3, _ = st.columns([1, 1, 1, 3], gap="small")
    with b1:
        if st.button("同步修改到套件", type="primary", use_container_width=True):
            _sync_edits_to_suite(suite, edited_df, df)
            st.toast(f"已同步 {len(suite.cases)} 条用例到套件")
            st.session_state["edited_cases"] = None

    with b2:
        if st.button("撤销修改", type="secondary", use_container_width=True):
            st.session_state["edited_cases"] = None
            st.rerun()

    with b3:
        csv_data = _build_case_csv(suite)
        st.download_button(
            "导出 CSV (含编辑)",
            data=csv_data,
            file_name=f"testsuite_edited_{datetime.now():%Y%m%d_%H%M%S}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # 变更追踪提示
    if not edited_df.equals(df):
        changed = (edited_df != df).any(axis=1).sum()
        st.info(f"检测到 {changed} 行发生变更,点击「同步修改到套件」保存。")


def _sync_edits_to_suite(suite, edited_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
    """将编辑后的 DataFrame 同步回 TestSuite。"""
    # 构建新用例列表
    new_cases = []
    for _, row in edited_df.iterrows():
        cid = row.get("ID", "")
        rid = row.get("需求", "")
        tech = row.get("技术", "EP")
        priority = row.get("优先级", "Medium")
        inputs = _parse_input_str(str(row.get("输入", "")))
        expected = str(row.get("预期结果", ""))
        preconditions = [p.strip() for p in str(row.get("前置条件", "")).split(";") if p.strip()]
        tags = [t.strip() for t in str(row.get("标签", "")).split(",") if t.strip()]

        # 保留原始 ID 或分配新 ID
        if not cid or cid.startswith("NEW-"):
            cid = f"USR-EP-{len(new_cases) + 1:03d}"

        case = TestCase(
            id=cid,
            requirement_id=rid,
            technique=tech,
            inputs=inputs,
            preconditions=preconditions,
            expected_result=expected,
            priority=priority,
            tags=tags,
        )
        new_cases.append(case)

    suite.cases = new_cases


def _parse_input_str(s: str) -> dict[str, object]:
    """解析 'key=val, key=val' 格式的输入字符串。"""
    result: dict[str, object] = {}
    if not s or s == "nan":
        return result
    for part in s.split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            k, v = k.strip(), v.strip()
            # 尝试转换数值
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass
            result[k] = v
    return result


def _build_case_csv(suite) -> str:
    """将当前套件转为 CSV 字符串(包含编辑后的字段)。"""
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Requirement", "Technique", "Priority", "Inputs", "Expected", "Preconditions", "Tags"])
    for c in suite.cases:
        writer.writerow([
            c.id,
            c.requirement_id,
            c.technique,
            c.priority,
            ", ".join(f"{k}={v}" for k, v in c.inputs.items()),
            c.expected_result,
            "; ".join(c.preconditions),
            ", ".join(c.tags),
        ])
    return buf.getvalue()


# ═══════════════════════════════════════════
# 指标卡片
# ═══════════════════════════════════════════

def _mini_metric(label: str, value: str, color: str) -> None:
    """紧凑指标卡(覆盖率栏用)。"""
    st.markdown(
        f"""
        <div class="atd-minicard">
          <div class="atd-minicard-label">{label}</div>
          <div class="atd-minicard-value" style="color:{color}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
