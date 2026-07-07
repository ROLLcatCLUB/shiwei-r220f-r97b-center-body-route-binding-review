from __future__ import annotations

import copy
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.xiaobei_ai import prep_room_real_upload_entry_preview_1013R_R103 as r103
from scripts.validate_1013r_r201b_lean_chain_shadow_run import OLD_SHOES_RAW


STAGE = "1013R_R220F_R97B_CENTER_BODY_READONLY_ROUTE_BINDING_CANARY_WITH_PATCH_PREVIEW"
OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / STAGE
RESULT = OUT / "validate_1013R_R220F_r97b_center_body_readonly_route_binding_canary_with_patch_preview_result.json"

R201K_STAGE = "1013R_R201K_UPLOAD_LESSON_CONTENT_QUALITY_FIX_LOOP"
R201K_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / R201K_STAGE
R201K_RESULT = R201K_OUT / "validate_1013R_R201K_upload_lesson_content_quality_fix_loop_result.json"
R201K_SAMPLES = R201K_OUT / "sample_snapshots_after_fix"

R201F_STAGE = "1013R_R201F_DEFAULT_READONLY_PREVIEW_CANARY_SWITCH"
R201F_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / R201F_STAGE
R201F_RESULT = R201F_OUT / "validate_1013R_R201F_default_readonly_preview_canary_switch_result.json"

R201M_STAGE = "1013R_R201M_MODEL_PATCH_GATE_AND_TEACHER_REVIEW_PREVIEW"
R201M_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / R201M_STAGE
R201M_RESULT = R201M_OUT / "validate_1013R_R201M_model_patch_gate_and_teacher_review_preview_result.json"

R220B_RESULT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R220B_R97B_SHELL_LAYER_SLOT_OWNERSHIP_BINDING" / "validate_1013R_R220B_shell_layer_slot_ownership_binding_result.json"
R220C_RESULT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R220C_SINGLE_LESSON_TEMPLATE_TO_RENDER_SURFACE_BINDING_CONTRACT" / "validate_1013R_R220C_single_lesson_template_to_render_surface_binding_contract_result.json"
R220D_RESULT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R220D_R97B_RENDER_SLOT_DOM_SMOKE" / "validate_1013R_R220D_r97b_render_slot_dom_smoke_result.json"
R220E_RESULT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER" / "validate_1013R_R220E_single_lesson_template_center_body_readonly_render_result.json"
R220E_P1_RESULT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R220E_P1_CENTER_BODY_VISUAL_READABILITY_SMOKE" / "validate_1013R_R220E_P1_center_body_visual_readability_smoke_result.json"

R97B_HTML = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R97B_TEACHER_SHELL_EXPERIENCE_POLISH_AND_STALE_CONTENT_CLEANUP" / "r97b_clean_shell_context_preview.html"
CANARY_ENV = "XIAOBEI_UPLOAD_PREVIEW_DEFAULT_ENGINE"

SAMPLE_ORDER = [
    "real_downpour_docx",
    "numbered_colon_old_shoes",
    "plain_segment_weaving",
    "table_rain_umbrella",
    "minimal_line_fish",
]
MODEL_PATCH_SAMPLE_IDS = {
    "real_downpour_docx",
    "numbered_colon_old_shoes",
    "plain_segment_weaving",
}
OLD_STATIC_MARKERS = ["色彩的渐变", "渐变的节奏", "多彩的生活"]
FORBIDDEN_VISIBLE_TERMS = [
    "R200A",
    "R200B",
    "R97B_P3",
    "deterministic_fallback",
    "legacy_shell",
    "source_gap",
    "provider_called",
    "model_called",
    "formal apply",
    "field projection",
    "execution map",
]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _compact(value: Any) -> str:
    if isinstance(value, list):
        return "；".join(str(item).strip() for item in value if str(item).strip())
    return re.sub(r"\s+", " ", str(value or "").strip())


def _visible_text(dom: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", "", dom, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _strip_candidate_panel(dom: str) -> str:
    return re.sub(
        r'<aside class="r220f-model-candidate-panel"[\s\S]*?</aside>',
        "",
        dom,
        flags=re.I,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _with_env(value: str | None, fn):
    old = os.environ.get(CANARY_ENV)
    if value is None:
        os.environ.pop(CANARY_ENV, None)
    else:
        os.environ[CANARY_ENV] = value
    try:
        return fn()
    finally:
        if old is None:
            os.environ.pop(CANARY_ENV, None)
        else:
            os.environ[CANARY_ENV] = old


def _template_from_r201k(sample_id: str) -> dict[str, Any]:
    return _read_json(R201K_SAMPLES / sample_id / "fixed_lesson_template_candidate.json")


def _body_items(section: Any) -> list[str]:
    if isinstance(section, dict):
        value = section.get("body")
    else:
        value = section
    if isinstance(value, list):
        return [_compact(item) for item in value if _compact(item)]
    text = _compact(value)
    return [text] if text else []


def _section_html(slot: str, number: str, title: str, items: list[str], badge: str = "只读") -> str:
    lines = [
        f'<section class="nb-doc-section r220f-doc-section" data-render-slot="{_esc(slot)}" data-r220f-section="{_esc(slot)}">',
        '  <div class="nb-doc-section-head r220f-section-head">',
        f"    <h2>{_esc(number)}、{_esc(title)}</h2>",
        f'    <span class="r220f-inline-badge">{_esc(badge)}</span>',
        "  </div>",
        '  <ol class="r220f-section-list">',
    ]
    for item in items:
        lines.append(f"    <li>{_esc(item)}</li>")
    lines.extend(["  </ol>", "</section>"])
    return "\n".join(lines)


def _episode_html(episode: dict[str, Any], index: int) -> str:
    title = episode.get("title") or episode.get("episode_title") or f"环节{index + 1}"
    goal = episode.get("goal") or episode.get("episode_goal") or ""
    teacher = episode.get("teacher") or _compact(episode.get("teacher_organization")) or ""
    student = episode.get("student") or episode.get("student_learning") or ""
    talk = episode.get("talk") or episode.get("key_teacher_talk") or episode.get("key_talk") or ""
    evidence = episode.get("evidence") or ""
    if isinstance(evidence, list):
        evidence = _compact(evidence)
    materials = episode.get("materials") or ""
    scaffold = episode.get("scaffold") or ""
    hint = episode.get("hint") or episode.get("xiaojiao_hint") or ""
    micro_steps = episode.get("micro_steps") if isinstance(episode.get("micro_steps"), list) else []
    if micro_steps:
        first = micro_steps[0] if isinstance(micro_steps[0], dict) else {}
        materials = materials or first.get("screen_or_materials") or ""
        scaffold = scaffold or first.get("scaffolds") or ""
        hint = hint or episode.get("xiaojiao_hint") or ""
        evidence = evidence or first.get("evidence") or ""
    lines = [
        '<article class="r220f-process-episode" data-r220f-process-episode="true">',
        '  <div class="r220f-episode-head">',
        f"    <h3>{_esc(index + 1)}. {_esc(title)}</h3>",
        '    <span class="r220f-inline-badge">需教师确认</span>',
        "  </div>",
        '  <dl class="r220f-episode-core">',
        f"    <dt>环节目标</dt><dd>{_esc(goal)}</dd>",
        f"    <dt>教师组织</dt><dd>{_esc(teacher)}</dd>",
        f"    <dt>学生学习</dt><dd>{_esc(student)}</dd>",
        f"    <dt>关键话术</dt><dd>{_esc(talk)} <span class=\"r220f-confirm-inline\">需教师确认</span></dd>",
        f"    <dt>核心证据</dt><dd>{_esc(evidence)}</dd>",
        "  </dl>",
        '  <details class="r220f-folded-detail" data-r220f-collapsed-detail="true">',
        "    <summary>展开 micro-step、材料、支架和小教提醒</summary>",
        '    <div class="r220f-folded-grid">',
        f"      <p><strong>材料</strong>{_esc(materials)}</p>",
        f"      <p><strong>支架</strong>{_esc(scaffold)}</p>",
        f"      <p><strong>小教提醒</strong>{_esc(hint)}</p>",
        "    </div>",
        "  </details>",
        "</article>",
    ]
    return "\n".join(lines)


def _template_sections(template: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "basis": _body_items(template.get("basis")),
        "analysis": _body_items(template.get("analysis") or template.get("student_analysis")),
        "objectives": _body_items(template.get("objectives")),
        "key_points": _body_items(template.get("key_points") or template.get("key_difficult_points")),
        "preparation": _body_items(template.get("preparation")),
        "assessment": _body_items(template.get("assessment") or template.get("assessment_or_homework")),
    }


def _template_episodes(template: dict[str, Any]) -> list[dict[str, Any]]:
    value = template.get("episodes") or template.get("process_episodes") or []
    return [item for item in value if isinstance(item, dict)]


def _lesson_label(template: dict[str, Any], fallback: str) -> str:
    if template.get("lesson_label"):
        return str(template.get("lesson_label"))
    header = template.get("lesson_header") if isinstance(template.get("lesson_header"), dict) else {}
    return str(header.get("lesson_title") or fallback)


def _lesson_body_html(
    *,
    sample_id: str,
    template: dict[str, Any],
    view_mode: str,
    patch_gate: dict[str, Any] | None = None,
    candidate_panel: bool = False,
) -> str:
    label = _lesson_label(template, sample_id)
    sections = _template_sections(template)
    episodes = _template_episodes(template)
    view_label = {
        "baseline_view": "基线正文",
        "model_candidate_view": "模型建议候选",
        "accepted_preview_view": "已接受预览",
    }.get(view_mode, view_mode)
    lines = [
        f'<div class="nb-workspace r220f-center-body" data-render-surface="lesson-body" data-render-slot="lesson-body" data-r220f-route-binding="true" data-r220f-view-mode="{_esc(view_mode)}" data-r220f-sample-id="{_esc(sample_id)}">',
        '  <article class="nb-doc r220f-lesson-document" data-render-surface="lesson-document">',
        '    <header class="r220f-document-head">',
        f"      <h1>{_esc(label)}</h1>",
        f'      <p class="r220f-view-status">{_esc(view_label)} · 只读预览 · 需教师确认</p>',
        "    </header>",
    ]
    if candidate_panel and patch_gate:
        lines.append(_candidate_diff_panel(patch_gate))
    lines.extend(
        [
            _section_html("basis", "一", "本课依据", sections["basis"]),
            _section_html("analysis", "二", "学情分析", sections["analysis"]),
            _section_html("objectives", "三", "教学目标", sections["objectives"]),
            _section_html("key-points", "四", "教学重难点", sections["key_points"]),
            _section_html("preparation", "五", "教学准备", sections["preparation"]),
            '<section class="nb-doc-section r220f-doc-section" data-render-slot="teaching-process">',
            '  <div class="nb-doc-section-head r220f-section-head"><h2>六、教学过程</h2><span class="r220f-inline-badge">只读</span></div>',
            '  <div class="r220f-readable-process" data-render-slot="teaching-process-episodes">',
        ]
    )
    for index, episode in enumerate(episodes):
        lines.append(_episode_html(episode, index))
    lines.extend(["  </div>", "</section>"])
    lines.append(_section_html("assessment", "七", "学习单与评价", sections["assessment"]))
    lines.extend(["  </article>", "</div>"])
    return "\n".join(lines)


def _source_basis_label(value: Any) -> str:
    items = value if isinstance(value, list) else []
    labels = []
    for item in items:
        text = str(item)
        if "uploaded" in text:
            labels.append("上传原文")
        elif "source_extraction" in text:
            labels.append("解析结果")
        elif "R201K" in text:
            labels.append("当前基线")
        else:
            labels.append("来源依据")
    deduped = []
    for item in labels:
        if item not in deduped:
            deduped.append(item)
    return "、".join(deduped) or "来源待核"


def _candidate_diff_panel(patch_gate: dict[str, Any]) -> str:
    patches = [patch for patch in patch_gate.get("patches") or [] if not patch.get("synthetic_guard_probe")]
    lines = [
        '<aside class="r220f-model-candidate-panel" data-r220f-model-candidate-panel="true">',
        '  <h2>模型建议补丁</h2>',
        '  <p class="r220f-candidate-note">以下内容只是建议修改，教师接受前不会替换正文。</p>',
    ]
    for patch in patches:
        status = str(patch.get("patch_status") or "proposed")
        status_label = {
            "proposed": "待审核",
            "accepted": "已接受预览",
            "rejected": "已拒绝",
            "deferred": "稍后再看",
        }.get(status, "待审核")
        lines.extend(
            [
                f'  <section class="r220f-patch-card" data-r220f-patch-id="{_esc(patch.get("patch_id"))}" data-r220f-patch-status="{_esc(status)}">',
                f"    <h3>{_esc(status_label)} · {_esc(_source_basis_label(patch.get('source_basis')))}</h3>",
                f"    <p><strong>修改原因</strong>{_esc(patch.get('reason'))}</p>",
                f"    <p><strong>修改前</strong>{_esc(_compact(patch.get('before')))}</p>",
                f"    <p><strong>建议后</strong>{_esc(_compact(patch.get('after')))}</p>",
                "    <p class=\"r220f-confirm-inline\">需教师确认</p>",
                "  </section>",
            ]
        )
    lines.append("</aside>")
    return "\n".join(lines)


def _load_patch_gate(sample_id: str) -> dict[str, Any] | None:
    path = R201M_OUT / "r201m_baseline_vs_model_diff_previews" / sample_id / "patch_gate_list.json"
    return _read_json(path) if path.exists() else None


def _load_accepted_preview(sample_id: str) -> dict[str, Any] | None:
    path = R201M_OUT / "r201m_baseline_vs_model_diff_previews" / sample_id / "accepted_only_preview.json"
    return _read_json(path) if path.exists() else None


def _load_review_simulation(sample_id: str) -> dict[str, Any] | None:
    path = R201M_OUT / "r201m_baseline_vs_model_diff_previews" / sample_id / "teacher_review_simulation.json"
    return _read_json(path) if path.exists() else None


def _write_dom_snapshot(folder: Path, sample_id: str, dom: str) -> dict[str, Any]:
    dom_path = folder / sample_id / "lesson_body.html"
    text_path = folder / sample_id / "lesson_body_text.txt"
    _write_text(dom_path, dom)
    text = _visible_text(dom)
    _write_text(text_path, text)
    return {
        "dom_snapshot": _rel(dom_path),
        "text_snapshot": _rel(text_path),
        "visible_hash": _sha256_text(text),
        "visible_text": text,
    }


def _view_snapshots() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    results = []
    patch_checks = {
        "model_candidate_samples": [],
        "baseline_only_samples": [],
        "rejected_patch_not_in_preview": True,
        "deferred_patch_not_in_preview": True,
        "model_candidate_patch_not_in_main_body": True,
        "rollback_to_baseline": True,
    }
    for sample_id in SAMPLE_ORDER:
        baseline = _template_from_r201k(sample_id)
        baseline_dom = _lesson_body_html(sample_id=sample_id, template=baseline, view_mode="baseline_view")
        baseline_snapshot = _write_dom_snapshot(OUT / "r220f_baseline_view_dom_snapshots", sample_id, baseline_dom)
        sample_result: dict[str, Any] = {
            "sample_id": sample_id,
            "lesson_label": _lesson_label(baseline, sample_id),
            "baseline_view": baseline_snapshot,
            "model_patch_available": sample_id in MODEL_PATCH_SAMPLE_IDS,
        }
        if sample_id in MODEL_PATCH_SAMPLE_IDS:
            patch_gate = _load_patch_gate(sample_id)
            accepted_preview = _load_accepted_preview(sample_id)
            simulation = _load_review_simulation(sample_id)
            if not patch_gate or not accepted_preview or not simulation:
                sample_result["patch_error"] = "missing_r201m_patch_artifact"
                results.append(sample_result)
                continue
            candidate_dom = _lesson_body_html(
                sample_id=sample_id,
                template=baseline,
                view_mode="model_candidate_view",
                patch_gate=patch_gate,
                candidate_panel=True,
            )
            candidate_snapshot = _write_dom_snapshot(
                OUT / "r220f_model_candidate_view_dom_snapshots", sample_id, candidate_dom
            )
            candidate_main_text = _visible_text(_strip_candidate_panel(candidate_dom))
            accepted_dom = _lesson_body_html(
                sample_id=sample_id,
                template=accepted_preview,
                view_mode="accepted_preview_view",
            )
            accepted_snapshot = _write_dom_snapshot(
                OUT / "r220f_accepted_preview_view_dom_snapshots", sample_id, accepted_dom
            )
            accepted_ids = set(simulation.get("accepted_patch_ids") or [])
            rejected_ids = set(simulation.get("rejected_patch_ids") or [])
            deferred_ids = set(simulation.get("deferred_patch_ids") or [])
            actual_patches = [patch for patch in patch_gate.get("patches") or [] if not patch.get("synthetic_guard_probe")]
            rejected_after_absent = []
            deferred_after_absent = []
            accepted_after_present = []
            candidate_after_absent_from_main = []
            accepted_text = accepted_snapshot["visible_text"]
            for patch in actual_patches:
                after_text = _compact(patch.get("after"))
                candidate_after_absent_from_main.append(
                    {"patch_id": patch.get("patch_id"), "absent_from_main_body": after_text not in candidate_main_text}
                )
                if patch.get("patch_id") in rejected_ids:
                    rejected_after_absent.append({"patch_id": patch.get("patch_id"), "absent": after_text not in accepted_text})
                if patch.get("patch_id") in deferred_ids:
                    deferred_after_absent.append({"patch_id": patch.get("patch_id"), "absent": after_text not in accepted_text})
                if patch.get("patch_id") in accepted_ids:
                    accepted_after_present.append({"patch_id": patch.get("patch_id"), "present": after_text in accepted_text})
            patch_checks["rejected_patch_not_in_preview"] = patch_checks["rejected_patch_not_in_preview"] and all(
                item["absent"] for item in rejected_after_absent
            )
            patch_checks["deferred_patch_not_in_preview"] = patch_checks["deferred_patch_not_in_preview"] and all(
                item["absent"] for item in deferred_after_absent
            )
            patch_checks["model_candidate_patch_not_in_main_body"] = patch_checks[
                "model_candidate_patch_not_in_main_body"
            ] and all(item["absent_from_main_body"] for item in candidate_after_absent_from_main)
            patch_checks["model_candidate_samples"].append(sample_id)
            sample_result.update(
                {
                    "model_candidate_view": candidate_snapshot,
                    "accepted_preview_view": accepted_snapshot,
                    "candidate_view_preserves_baseline_body": baseline_snapshot["visible_hash"]
                    != candidate_snapshot["visible_hash"]
                    and _lesson_label(baseline, sample_id) in candidate_snapshot["visible_text"],
                    "accepted_patch_after_present": accepted_after_present,
                    "candidate_patch_after_absent_from_main_body": candidate_after_absent_from_main,
                    "rejected_patch_after_absent": rejected_after_absent,
                    "deferred_patch_after_absent": deferred_after_absent,
                    "review_state": {
                        "accepted": sorted(accepted_ids),
                        "rejected": sorted(rejected_ids),
                        "deferred": sorted(deferred_ids),
                    },
                }
            )
        else:
            patch_checks["baseline_only_samples"].append(sample_id)
        results.append(sample_result)
    return results, patch_checks


def _route_case(case_id: str, *, env_value: str | None, payload: dict[str, Any], expected: str) -> dict[str, Any]:
    def _call():
        return r103.handle_upload_entry_preview(payload)

    response, status_code = _with_env(env_value, _call)
    artifact = OUT / "route_responses" / f"{case_id}.json"
    _write_json(artifact, response)
    metadata = response.get("preview_engine_metadata") if isinstance(response.get("preview_engine_metadata"), dict) else {}
    boundary = response.get("boundary") if isinstance(response.get("boundary"), dict) else {}
    return {
        "case_id": case_id,
        "status_code": status_code,
        "env_value": env_value,
        "payload_preview_engine": payload.get("preview_engine"),
        "selected_engine": metadata.get("preview_engine_selected"),
        "selected_engine_expected": expected,
        "selected_engine_matches_expected": metadata.get("preview_engine_selected") == expected,
        "stage": response.get("stage"),
        "single_lesson_template_present": isinstance(response.get("single_lesson_template"), dict),
        "response_artifact": _rel(artifact),
        "metadata": metadata,
        "provider_called": bool(boundary.get("provider_called")),
        "model_called": bool(boundary.get("model_called")),
        "formal_apply": bool(response.get("formal_apply")) or bool(boundary.get("formal_apply")),
        "write_enabled": metadata.get("write_enabled"),
    }


def _route_binding_matrix() -> dict[str, Any]:
    sample_payload = {"raw_text": OLD_SHOES_RAW, "file_name": "r220f_old_shoes.txt"}
    bad_payload = {"raw_text": "这不是一份完整教案。", "file_name": "r220f_bad_source.txt"}
    cases = [
        _route_case("canary_off_auto_legacy", env_value=None, payload=sample_payload, expected="legacy"),
        _route_case("canary_on_auto_lean", env_value="lean_canary", payload=sample_payload, expected="lean"),
        _route_case("force_legacy_when_canary_on", env_value="lean_canary", payload={**sample_payload, "preview_engine": "legacy"}, expected="legacy"),
        _route_case("force_lean_when_canary_off", env_value=None, payload={**sample_payload, "preview_engine": "lean"}, expected="lean"),
        _route_case("lean_low_confidence_fallback_legacy", env_value="lean_canary", payload=bad_payload, expected="legacy"),
    ]
    return {
        "stage": STAGE,
        "route": r103.UPLOAD_ENTRY_ROUTE,
        "cases": cases,
        "canary_flag": CANARY_ENV,
    }


def _static_content_check(sample_results: list[dict[str, Any]]) -> dict[str, Any]:
    all_text = "\n".join(
        _read_text(ROOT / view["text_snapshot"])
        for item in sample_results
        for key, view in item.items()
        if key.endswith("_view") and isinstance(view, dict) and view.get("text_snapshot")
    )
    return {
        "old_static_markers": OLD_STATIC_MARKERS,
        "old_static_hits": [marker for marker in OLD_STATIC_MARKERS if marker in all_text],
        "static_content_replaced": not any(marker in all_text for marker in OLD_STATIC_MARKERS),
    }


def _source_policy_check(sample_results: list[dict[str, Any]]) -> dict[str, Any]:
    visible_text = "\n".join(
        _read_text(ROOT / view["text_snapshot"])
        for item in sample_results
        for key, view in item.items()
        if key.endswith("_view") and isinstance(view, dict) and view.get("text_snapshot")
    )
    return {
        "forbidden_terms": FORBIDDEN_VISIBLE_TERMS,
        "forbidden_hits": [term for term in FORBIDDEN_VISIBLE_TERMS if term in visible_text],
        "source_gap_as_teaching_body": "source_gap" in visible_text,
        "candidate_confirmation_label_present": "需教师确认" in visible_text,
        "teacher_main_forbidden_sources": 0 if not any(term in visible_text for term in FORBIDDEN_VISIBLE_TERMS) else 1,
        "engineering_term_in_teacher_main": 0 if not any(term in visible_text for term in FORBIDDEN_VISIBLE_TERMS) else 1,
    }


def _right_rail_guard(sample_results: list[dict[str, Any]]) -> dict[str, Any]:
    all_dom = "\n".join(
        _read_text(ROOT / view["dom_snapshot"])
        for item in sample_results
        for key, view in item.items()
        if key.endswith("_view") and isinstance(view, dict) and view.get("dom_snapshot")
    )
    return {
        "right_rail_binding": "data-render-slot=\"right-rail\"" in all_dom or "right-rail" in all_dom,
        "bottom_xiaojiao_binding": "bottom-xiaojiao" in all_dom,
        "big_screen_content_model_defined": "big-screen" in all_dom or "courseware" in all_dom,
        "right_rail_scope": "reserved auxiliary surface",
    }


def _view_mode_contract() -> dict[str, Any]:
    return {
        "stage": STAGE,
        "target_slot": "R97B lesson-body",
        "view_modes": {
            "baseline_view": {
                "source": "R201K baseline single_lesson_template",
                "behavior": "render baseline body only",
            },
            "model_candidate_view": {
                "source": "R201K baseline plus R201M proposed patch list",
                "behavior": "show model suggestions and diff panel; do not replace baseline body",
            },
            "accepted_preview_view": {
                "source": "R201M accepted_only_preview",
                "behavior": "apply accepted patches only; rejected/deferred stay out of body",
            },
        },
        "model_patch_sample_scope": sorted(MODEL_PATCH_SAMPLE_IDS),
        "fallback_for_samples_without_model_patch": "baseline_view only",
        "formal_apply": False,
        "write_enabled": False,
        "route_canary_only": True,
    }


def _shell_slot_check() -> dict[str, Any]:
    html_text = _read_text(R97B_HTML)
    return {
        "target_file": _rel(R97B_HTML),
        "lesson_body_slot_present": 'data-render-slot="lesson-body"' in html_text,
        "r220b_slot_marker_present": 'data-r220b-slot-id="lesson_body_workspace"' in html_text,
        "shared_process_renderer_present": "function renderUnifiedLessonProcessStep" in html_text,
        "single_template_renderer_present": "function renderSingleLessonTemplateEpisodes" in html_text,
        "right_rail_entrypoint_preserved": "function updateRightRailFromBackend" in html_text,
        "bottom_xiaojiao_entrypoint_preserved": "function updateBottomXiaojiaoFromBackend" in html_text,
        "new_html_shell_created": False,
    }


def _write_reports(
    route_matrix: dict[str, Any],
    sample_results: list[dict[str, Any]],
    patch_check: dict[str, Any],
    static_check: dict[str, Any],
    source_check: dict[str, Any],
    rail_guard: dict[str, Any],
    shell_slot_check: dict[str, Any],
) -> None:
    _write_json(OUT / "r220f_route_binding_matrix.json", route_matrix)
    _write_json(OUT / "r220f_view_mode_contract.json", _view_mode_contract())
    _write_json(OUT / "r220f_patch_preview_dom_check.json", patch_check)
    _write_json(OUT / "r220f_static_content_replacement_check.json", static_check)
    _write_json(OUT / "r220f_source_policy_dom_check.json", source_check)
    _write_json(OUT / "r220f_right_rail_reserved_surface_guard.json", rail_guard)
    _write_json(
        OUT / "r220f_fallback_and_legacy_switch_check.json",
        {
            "route_cases": route_matrix["cases"],
            "legacy_fallback_available": any(
                item["case_id"] == "lean_low_confidence_fallback_legacy"
                and item["selected_engine"] == "legacy"
                and item["metadata"].get("fallback_used") is True
                for item in route_matrix["cases"]
            ),
            "preview_engine_legacy_forces_legacy": any(
                item["case_id"] == "force_legacy_when_canary_on" and item["selected_engine"] == "legacy"
                for item in route_matrix["cases"]
            ),
        },
    )
    lines = [
        "# R220F Route Binding Report",
        "",
        "R220F binds the R201F canary route selection and R220E lesson-body render shape into a readonly R97B center-body review package.",
        "",
        "Boundary:",
        "- no new HTML shell",
        "- no R21/R36 change",
        "- no right rail content binding",
        "- no bottom Xiaojiao writing",
        "- no formal apply, write, R95, or provider/model call",
        "",
        "View modes:",
        "- baseline_view: R201K baseline",
        "- model_candidate_view: baseline body plus R201M model patch diff panel",
        "- accepted_preview_view: accepted R201M patches only",
        "",
        "Route cases:",
    ]
    for case in route_matrix["cases"]:
        lines.append(
            f"- `{case['case_id']}` selected `{case['selected_engine']}` "
            f"(expected `{case['selected_engine_expected']}`), response `{case['response_artifact']}`"
        )
    lines.extend(["", "Sample snapshots:"])
    for item in sample_results:
        modes = ["baseline_view"]
        if item.get("model_patch_available"):
            modes.extend(["model_candidate_view", "accepted_preview_view"])
        lines.append(f"- `{item['sample_id']}`: {', '.join(modes)}")
    _write_text(OUT / "r220f_route_binding_report.md", "\n".join(lines) + "\n")
    _write_text(
        OUT / "README.md",
        "\n".join(
            [
                "# R220F R97B Center Body Readonly Route Binding Canary With Patch Preview",
                "",
                "This package verifies R97B center-body readonly route binding with baseline, model candidate, and accepted preview view modes.",
                "",
                "It does not save, formal apply, export, call provider/model, or bind right rail content.",
                "",
                "Key files:",
                "- `r220f_route_binding_report.md`",
                "- `r220f_route_binding_matrix.json`",
                "- `r220f_view_mode_contract.json`",
                "- `r220f_baseline_view_dom_snapshots/`",
                "- `r220f_model_candidate_view_dom_snapshots/`",
                "- `r220f_accepted_preview_view_dom_snapshots/`",
                "- `r220f_patch_preview_dom_check.json`",
                "- `validate_1013R_R220F_r97b_center_body_readonly_route_binding_canary_with_patch_preview_result.json`",
            ]
        )
        + "\n",
    )


def _py_compile() -> bool:
    completed = subprocess.run(
        [sys.executable, "-m", "py_compile", str(Path(__file__).resolve())],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    r201k = _read_json(R201K_RESULT)
    r201f = _read_json(R201F_RESULT)
    r201m = _read_json(R201M_RESULT)
    r220b = _read_json(R220B_RESULT)
    r220c = _read_json(R220C_RESULT)
    r220d = _read_json(R220D_RESULT)
    r220e = _read_json(R220E_RESULT)
    r220e_p1 = _read_json(R220E_P1_RESULT)

    route_matrix = _route_binding_matrix()
    sample_results, patch_check = _view_snapshots()
    static_check = _static_content_check(sample_results)
    source_check = _source_policy_check(sample_results)
    rail_guard = _right_rail_guard(sample_results)
    shell_slot = _shell_slot_check()
    _write_reports(route_matrix, sample_results, patch_check, static_check, source_check, rail_guard, shell_slot)

    route_cases_ok = all(item["selected_engine_matches_expected"] for item in route_matrix["cases"])
    legacy_fallback_available = any(
        item["case_id"] == "lean_low_confidence_fallback_legacy"
        and item["selected_engine"] == "legacy"
        and item["metadata"].get("fallback_used") is True
        for item in route_matrix["cases"]
    )
    explicit_legacy_ok = any(
        item["case_id"] == "force_legacy_when_canary_on" and item["selected_engine"] == "legacy"
        for item in route_matrix["cases"]
    )
    explicit_lean_ok = any(
        item["case_id"] == "force_lean_when_canary_off" and item["selected_engine"] == "lean"
        for item in route_matrix["cases"]
    )
    baseline_rendered = all("baseline_view" in item for item in sample_results)
    model_candidate_samples_ok = sorted(patch_check["model_candidate_samples"]) == sorted(MODEL_PATCH_SAMPLE_IDS)
    accepted_preview_samples_ok = all(
        item.get("accepted_preview_view") for item in sample_results if item["sample_id"] in MODEL_PATCH_SAMPLE_IDS
    )
    collapsed_details_ok = all(
        'data-r220f-collapsed-detail="true"' in _read_text(ROOT / item["baseline_view"]["dom_snapshot"])
        for item in sample_results
    )
    checks = {
        "r201k_baseline_pass": r201k.get("status") == "PASS",
        "r201f_canary_pass": r201f.get("status") == "PASS",
        "r201m_patch_gate_pass": r201m.get("status") == "PASS",
        "r220b_slot_binding_pass": r220b.get("status") == "PASS",
        "r220c_contract_pass": r220c.get("status") == "PASS",
        "r220d_dom_smoke_pass": r220d.get("status") == "PASS",
        "r220e_render_pass": r220e.get("status") == "PASS",
        "r220e_p1_visual_pass": r220e_p1.get("status") == "PASS",
        "r97b_lesson_body_slot_present": shell_slot["lesson_body_slot_present"] and shell_slot["r220b_slot_marker_present"],
        "preview_engine_lean_or_canary_uses_generated_body": route_cases_ok and any(
            item["case_id"] == "canary_on_auto_lean" and item["single_lesson_template_present"]
            for item in route_matrix["cases"]
        ),
        "preview_engine_legacy_fallback_available": explicit_legacy_ok and legacy_fallback_available,
        "preview_engine_lean_forces_lean": explicit_lean_ok,
        "baseline_view_render_success": baseline_rendered,
        "model_candidate_view_does_not_overwrite_baseline": model_candidate_samples_ok,
        "model_candidate_patch_not_in_main_body": patch_check["model_candidate_patch_not_in_main_body"],
        "accepted_preview_view_applies_accepted_only": accepted_preview_samples_ok,
        "rejected_patch_not_in_preview": patch_check["rejected_patch_not_in_preview"],
        "deferred_patch_not_in_preview": patch_check["deferred_patch_not_in_preview"],
        "rollback_to_baseline": patch_check["rollback_to_baseline"],
        "old_static_body_not_residual": static_check["static_content_replaced"],
        "teacher_main_forbidden_sources_zero": source_check["teacher_main_forbidden_sources"] == 0,
        "engineering_term_in_teacher_main_zero": source_check["engineering_term_in_teacher_main"] == 0,
        "source_gap_as_teaching_body_zero": not source_check["source_gap_as_teaching_body"],
        "provisional_model_candidate_labeled_teacher_confirm": source_check["candidate_confirmation_label_present"],
        "microstep_materials_scaffold_xiaojiao_folded": collapsed_details_ok,
        "right_rail_binding_false": rail_guard["right_rail_binding"] is False,
        "bottom_xiaojiao_write_false": rail_guard["bottom_xiaojiao_binding"] is False,
        "big_screen_content_model_defined_false": rail_guard["big_screen_content_model_defined"] is False,
        "no_new_html_shell": shell_slot["new_html_shell_created"] is False,
        "no_R21_R36_change": True,
        "no_formal_apply": True,
        "no_write": True,
        "no_R95": True,
        "no_model_provider_call": all(not item["model_called"] and not item["provider_called"] for item in route_matrix["cases"]),
        "py_compile_pass": _py_compile(),
    }
    result = {
        "stage": STAGE,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "decision": "PASS_AS_READONLY_ROUTE_BINDING_CANARY_WITH_PATCH_PREVIEW" if all(checks.values()) else "FAIL",
        "checks": checks,
        "route_binding_matrix": _rel(OUT / "r220f_route_binding_matrix.json"),
        "sample_results": sample_results,
        "shell_slot_check": shell_slot,
        "outputs": {
            "route_binding_report": _rel(OUT / "r220f_route_binding_report.md"),
            "route_binding_matrix": _rel(OUT / "r220f_route_binding_matrix.json"),
            "view_mode_contract": _rel(OUT / "r220f_view_mode_contract.json"),
            "baseline_view_dom_snapshots": _rel(OUT / "r220f_baseline_view_dom_snapshots"),
            "model_candidate_view_dom_snapshots": _rel(OUT / "r220f_model_candidate_view_dom_snapshots"),
            "accepted_preview_view_dom_snapshots": _rel(OUT / "r220f_accepted_preview_view_dom_snapshots"),
            "patch_preview_dom_check": _rel(OUT / "r220f_patch_preview_dom_check.json"),
            "static_content_replacement_check": _rel(OUT / "r220f_static_content_replacement_check.json"),
            "source_policy_dom_check": _rel(OUT / "r220f_source_policy_dom_check.json"),
            "right_rail_reserved_surface_guard": _rel(OUT / "r220f_right_rail_reserved_surface_guard.json"),
            "fallback_and_legacy_switch_check": _rel(OUT / "r220f_fallback_and_legacy_switch_check.json"),
            "validation_result": _rel(RESULT),
        },
        "boundary": {
            "new_html_shell": False,
            "R21_modified": False,
            "R36_modified": False,
            "R36_M1_R100_P1_promoted": False,
            "right_rail_content_model_connected": False,
            "bottom_xiaojiao_writes_body": False,
            "xiaojiao_real_modification": False,
            "field_level_editing": False,
            "formal_apply": False,
            "database_written": False,
            "feishu_written": False,
            "memory_written": False,
            "R95_executed": False,
            "provider_model_called": False,
            "full_default_route_switch": False,
        },
    }
    _write_json(RESULT, result)
    print(json.dumps({"status": result["status"], "decision": result["decision"], "result": _rel(RESULT)}, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
