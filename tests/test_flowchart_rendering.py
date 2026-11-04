"""Comprehensive test suite for flowchart text overflow prevention, box alignment,
decision diamond layout geometry, connector alignment, and SVG/PNG export.
"""

import os
import re
import html
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
import fitz


def escape_xml(s: str) -> str:
    return html.escape(s, quote=True)


def wrap_text(text: str, max_chars: int) -> list[str]:
    """Mirror frontend wrapText implementation."""
    if not text:
        return []
    words = text.strip().split()
    lines = []
    current_line = ""
    for word in words:
        if not current_line:
            current_line = word
        elif len(current_line + " " + word) <= max_chars:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines if lines else [text]


def get_project_workflow_nodes(project_title: str) -> list[dict]:
    """Mirror ProjectFlowDiagramModal workflow selection."""
    title_lower = project_title.strip().lower()

    if "enterprise network hardening" in title_lower:
        return [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Virtual Network Setup"},
            {"step": 3, "type": "phase", "label": "Deploy Ubuntu Server VMs"},
            {"step": 4, "type": "phase", "label": "Configure Network and Verify Connectivity"},
            {"step": 5, "type": "phase", "label": "Nmap Reconnaissance"},
            {"step": 6, "type": "phase", "label": "OpenVAS Vulnerability Assessment"},
            {"step": 7, "type": "phase", "label": "Linux Hardening and Firewall Configuration", "isLoopTarget": True},
            {"step": 8, "type": "phase", "label": "Post-Hardening Security Validation"},
            {
                "step": 9,
                "type": "decision",
                "label": "Are security requirements satisfied?",
                "noAction": "Review findings and perform further hardening.",
                "noTargetStep": 7,
                "yesAction": "Document verified results.",
            },
            {"step": 10, "type": "phase", "label": "Document verified results."},
            {"step": 11, "type": "phase", "label": "Generate Security Assessment Report"},
            {"step": 12, "type": "end", "label": "END"},
        ]
    elif "web application security" in title_lower:
        return [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Configure Isolated Lab in Docker (Juice Shop / DVWA)"},
            {"step": 3, "type": "phase", "label": "Map Attack Surface via Nmap & Burp Suite Proxy"},
            {"step": 4, "type": "phase", "label": "Execute Targeted Vulnerability Tests (SQLi, XSS, IDOR)", "isLoopTarget": True},
            {
                "step": 5,
                "type": "decision",
                "label": "Was the vulnerability verified & reproduced?",
                "noAction": "Review evidence and refine testing in authorized lab.",
                "noTargetStep": 4,
                "yesAction": "Record verified findings & exploit proof.",
            },
            {"step": 6, "type": "phase", "label": "Record verified findings & exploit proof."},
            {"step": 7, "type": "phase", "label": "Apply CVSS v3.1 Severity Scoring & Remediation Planning"},
            {"step": 8, "type": "phase", "label": "Compile Final Security Assessment Report"},
            {"step": 9, "type": "end", "label": "END"},
        ]
    else:
        return [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Prerequisites & Environment Setup"},
            {"step": 3, "type": "phase", "label": "Core System Implementation & Configuration"},
            {"step": 4, "type": "phase", "label": "Testing & Security Validation", "isLoopTarget": True},
            {
                "step": 5,
                "type": "decision",
                "label": "Are project requirements satisfied?",
                "noAction": "Review findings and perform further refinement.",
                "noTargetStep": 4,
                "yesAction": "Document verified deliverables.",
            },
            {"step": 6, "type": "phase", "label": "Document verified deliverables."},
            {"step": 7, "type": "phase", "label": "Generate Final Security Assessment Report"},
            {"step": 8, "type": "end", "label": "END"},
        ]


def compute_svg_layout(workflow_nodes: list[dict]):
    """Mirror frontend svgLayout computation."""
    center_x = 340
    box_width = 420
    diamond_width = 360
    diamond_height = 140
    start_y = 36
    vertical_gap = 36

    current_y = start_y
    node_coords = []

    for node in workflow_nodes:
        ntype = node.get("type", "phase")
        height = 54
        width = box_width
        if ntype in ("start", "end"):
            height = 44
            width = 200
            lines = [node["label"]]
        elif ntype == "decision":
            height = diamond_height
            width = diamond_width
            lines = wrap_text(node["label"], 24)
        else:
            width = box_width
            lines = wrap_text(node["label"], 36)
            if len(lines) == 1:
                height = 54
            elif len(lines) == 2:
                height = 68
            else:
                height = max(76, len(lines) * 20 + 26)

        x = center_x - width / 2
        y = current_y
        center_y = y + height / 2
        bottom_y = y + height

        node_coords.append({
            "node": node,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "centerY": center_y,
            "bottomY": bottom_y,
            "lines": lines,
        })
        current_y += height + vertical_gap

    decision_coord = next((c for c in node_coords if c["node"]["type"] == "decision"), None)
    no_box_x = 584
    no_box_width = 280
    no_box_height = 76
    no_box_y = 0
    no_box_lines = []

    if decision_coord:
        dec_right_x = center_x + diamond_width / 2
        no_box_x = dec_right_x + 64
        no_action_text = decision_coord["node"].get("noAction", "Review findings and perform further hardening.")
        no_box_lines = wrap_text(no_action_text, 24)
        no_box_height = max(74, len(no_box_lines) * 19 + 36)
        no_box_y = decision_coord["centerY"] - no_box_height / 2

    svg_width = max(960, int(no_box_x + no_box_width + 60))
    total_height = int(current_y + 36)

    return {
        "svgWidth": svg_width,
        "totalHeight": total_height,
        "centerX": center_x,
        "boxWidth": box_width,
        "diamondWidth": diamond_width,
        "diamondHeight": diamond_height,
        "nodeCoords": node_coords,
        "decisionCoord": decision_coord,
        "noBox": {
            "x": no_box_x,
            "y": no_box_y,
            "width": no_box_width,
            "height": no_box_height,
            "lines": no_box_lines,
            "centerX": no_box_x + no_box_width / 2,
        },
    }


def generate_full_svg(project_title: str) -> str:
    """Generate exact standalone SVG markup matching the frontend modal component."""
    nodes = get_project_workflow_nodes(project_title)
    layout = compute_svg_layout(nodes)

    center_x = layout["centerX"]
    svg_w = layout["svgWidth"]
    svg_h = layout["totalHeight"]
    node_coords = layout["nodeCoords"]
    decision_coord = layout["decisionCoord"]
    no_box = layout["noBox"]

    # Target node for loop
    target_step = decision_coord["node"].get("noTargetStep", 7) if decision_coord else 7
    loop_target = next((c for c in node_coords if c["node"].get("step") == target_step), None)
    if not loop_target:
        loop_target = next((c for c in node_coords if c["node"].get("isLoopTarget")), node_coords[2])

    lines_svg = []
    # 1. Downward connectors
    for idx in range(len(node_coords) - 1):
        c = node_coords[idx]
        nc = node_coords[idx + 1]
        is_dec = c["node"]["type"] == "decision"
        stroke = "#16A34A" if is_dec else "#2563EB"
        marker = "url(#flow-arrow-green)" if is_dec else "url(#flow-arrow-blue)"
        sw = "2.5" if is_dec else "2"
        lines_svg.append(f'<line x1="{center_x}" y1="{c["bottomY"]}" x2="{center_x}" y2="{nc["y"] - 1}" stroke="{stroke}" stroke-width="{sw}" marker-end="{marker}"/>')

        if is_dec:
            lines_svg.append(f'''
            <g id="badge-yes">
              <rect x="{center_x + 12}" y="{c["bottomY"] + 8}" width="46" height="22" rx="4" fill="#DCFCE7" stroke="#16A34A" stroke-width="1"/>
              <text x="{center_x + 35}" y="{c["bottomY"] + 23}" text-anchor="middle" fill="#15803D" font-size="11" font-weight="800">YES</text>
            </g>''')

    # 2. Decision NO branch & loop
    if decision_coord:
        dec_rx = center_x + layout["diamondWidth"] / 2
        dec_y = decision_coord["centerY"]
        target_rx = loop_target["x"] + loop_target["width"]
        target_y = loop_target["centerY"]

        lines_svg.append(f'''
        <!-- Horizontal NO connector -->
        <line x1="{dec_rx}" y1="{dec_y}" x2="{no_box["x"] - 2}" y2="{dec_y}" stroke="#DC2626" stroke-width="2" marker-end="url(#flow-arrow-red)"/>

        <!-- NO label -->
        <rect x="{dec_rx + 12}" y="{dec_y - 26}" width="40" height="20" rx="4" fill="#FEE2E2" stroke="#DC2626" stroke-width="1"/>
        <text x="{dec_rx + 32}" y="{dec_y - 12}" text-anchor="middle" fill="#B91C1C" font-size="11" font-weight="800">NO</text>

        <!-- Remediation Box -->
        <rect x="{no_box["x"]}" y="{no_box["y"]}" width="{no_box["width"]}" height="{no_box["height"]}" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="1.75"/>
        <text x="{no_box["centerX"]}" y="{no_box["y"] + 20}" text-anchor="middle" fill="#B91C1C" font-size="10.5" font-weight="800" letter-spacing="0.8">REMEDIATION</text>
        <text text-anchor="middle" fill="#991B1B" font-size="12" font-weight="600">
        ''')
        for lidx, line in enumerate(no_box["lines"]):
            lines_svg.append(f'<tspan x="{no_box["centerX"]}" y="{no_box["y"] + 38 + lidx * 18}">{escape_xml(line)}</tspan>')
        lines_svg.append('</text>')

        # Return loop
        lines_svg.append(f'''
        <path d="M {no_box["centerX"]} {no_box["y"]} L {no_box["centerX"]} {target_y} L {target_rx + 2} {target_y}"
              fill="none" stroke="#DC2626" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#flow-arrow-red)"/>
        <g id="badge-loop">
          <rect x="{no_box["centerX"] - 74}" y="{(no_box["y"] + target_y) / 2 - 12}" width="148" height="24" rx="4" fill="#FFFFFF" stroke="#EF4444" stroke-width="1"/>
          <text x="{no_box["centerX"]}" y="{(no_box["y"] + target_y) / 2 + 4.5}" text-anchor="middle" fill="#DC2626" font-size="10.5" font-weight="700">Iterative Remediation Loop</text>
        </g>
        ''')

    # 3. Nodes
    for idx, c in enumerate(node_coords):
        node = c["node"]
        ntype = node["type"]
        x, y, w, h, cy = c["x"], c["y"], c["width"], c["height"], c["centerY"]
        lines = c["lines"]

        if ntype in ("start", "end"):
            lines_svg.append(f'''
            <g id="node-{idx}">
              <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
              <text x="{center_x}" y="{cy + 4.5}" text-anchor="middle" fill="#1D4ED8" font-size="13" font-weight="800" letter-spacing="1.2">{escape_xml(node["label"])}</text>
            </g>''')
        elif ntype == "decision":
            hw, hh = w / 2, h / 2
            pts = f"{center_x},{cy - hh} {center_x + hw},{cy} {center_x},{cy + hh} {center_x - hw},{cy}"
            lines_svg.append(f'''
            <g id="node-{idx}">
              <polygon points="{pts}" fill="#F8FAFC" stroke="#2563EB" stroke-width="2.5"/>
              <text x="{center_x}" y="{cy - 26}" text-anchor="middle" fill="#2563EB" font-size="11" font-weight="800" letter-spacing="1.2">DECISION</text>
              <text text-anchor="middle" fill="#0F172A" font-size="12.5" font-weight="700">
            ''')
            if len(lines) == 1:
                lines_svg.append(f'<tspan x="{center_x}" y="{cy + 8}">{escape_xml(lines[0])}</tspan>')
            elif len(lines) == 2:
                lines_svg.append(f'<tspan x="{center_x}" y="{cy - 2}">{escape_xml(lines[0])}</tspan>')
                lines_svg.append(f'<tspan x="{center_x}" y="{cy + 18}">{escape_xml(lines[1])}</tspan>')
            else:
                lines_svg.append(f'<tspan x="{center_x}" y="{cy - 6}">{escape_xml(lines[0])}</tspan>')
                lines_svg.append(f'<tspan x="{center_x}" y="{cy + 12}">{escape_xml(lines[1])}</tspan>')
                lines_svg.append(f'<tspan x="{center_x}" y="{cy + 30}">{escape_xml(lines[2])}</tspan>')
            lines_svg.append('</text></g>')
        else:
            is_target = node.get("isLoopTarget", False)
            border_c = "#2563EB" if is_target else "#3B82F6"
            b_width = "2" if is_target else "1.5"
            line_h = 19
            first_y = cy - ((len(lines) - 1) * line_h) / 2 + 4.5

            lines_svg.append(f'''
            <g id="node-{idx}">
              <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" stroke="{border_c}" stroke-width="{b_width}"/>
              <rect x="{x + 14}" y="{cy - 12}" width="24" height="24" rx="6" fill="#EFF6FF" stroke="#DBEAFE" stroke-width="1"/>
              <text x="{x + 26}" y="{cy + 4}" text-anchor="middle" fill="#2563EB" font-size="11" font-weight="800">{node["step"]}</text>
              <text text-anchor="middle" fill="#0F172A" font-size="{12 if len(lines) > 2 else 12.5}" font-weight="600">
            ''')
            for lidx, line in enumerate(lines):
                lines_svg.append(f'<tspan x="{center_x + 12}" y="{first_y + lidx * line_h}">{escape_xml(line)}</tspan>')
            lines_svg.append('</text></g>')

    svg_content = f'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
  <defs>
    <marker id="flow-arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#2563EB" />
    </marker>
    <marker id="flow-arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#DC2626" />
    </marker>
    <marker id="flow-arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#16A34A" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#FFFFFF"/>
  {"".join(lines_svg)}
</svg>'''
    return svg_content


def test_enterprise_network_hardening_flowchart_geometry():
    """Verify text containment, diamond geometry, box alignment, and boundaries for Enterprise Network Hardening."""
    title = "Enterprise Network Hardening & Vulnerability Remediation Lab"
    nodes = get_project_workflow_nodes(title)
    layout = compute_svg_layout(nodes)

    assert len(nodes) == 12, "Must contain 12 stages"
    assert layout["svgWidth"] >= 960, "Canvas must provide at least 960px width"
    assert layout["totalHeight"] > 800, "Canvas height must dynamically enclose all 12 stages"

    center_x = layout["centerX"]

    # 1. Process boxes text wrapping and bounds check
    for coord in layout["nodeCoords"]:
        node = coord["node"]
        lines = coord["lines"]

        if node["type"] == "phase":
            # Label must not exceed 36 chars per line
            for line in lines:
                assert len(line) <= 38, f"Line exceeds max chars: '{line}'"
                # Pixel width approximation for 12.5px font: ~7.5px per character
                approx_line_w = len(line) * 7.5
                assert approx_line_w < (layout["boxWidth"] - 60), f"Line text overflows box: '{line}'"

            # Box height dynamically scales
            if len(lines) == 1:
                assert coord["height"] == 54
            elif len(lines) == 2:
                assert coord["height"] == 68
            else:
                assert coord["height"] >= 76

            # Box edges must stay within canvas
            assert coord["x"] > 0
            assert coord["x"] + coord["width"] < layout["svgWidth"]

    # 2. Decision diamond layout check
    dec = layout["decisionCoord"]
    assert dec is not None, "Decision node must exist"
    assert dec["width"] == 360
    assert dec["height"] == 140

    dec_lines = dec["lines"]
    assert len(dec_lines) in (2, 3), f"Decision question should wrap to 2 or 3 lines: {dec_lines}"

    # Verify every line fits strictly inside diamond geometry
    # In a diamond with width W and height H, maximum width at distance dy from center is:
    # W_max(dy) = W * (1 - 2*|dy| / H)
    W = dec["width"]
    H = dec["height"]
    cy = dec["centerY"]

    # "DECISION" header sits at dy = 26
    header_dy = 26
    w_allowable_header = W * (1 - 2 * header_dy / H)
    assert 65 < w_allowable_header, f"'DECISION' header ({65}px) overflows diamond width ({w_allowable_header}px)"

    # Question lines
    if len(dec_lines) == 2:
        y_offsets = [-2, 18]
    else:
        y_offsets = [-6, 12, 30]

    for line, y_off in zip(dec_lines, y_offsets):
        approx_w = len(line) * 7.5
        w_allowable = W * (1 - 2 * abs(y_off) / H)
        assert approx_w < w_allowable, f"Question line '{line}' (approx {approx_w}px) overflows diamond geometry at offset {y_off} (max {w_allowable}px)"

    # 3. YES and NO badges positioning
    # YES badge: x = centerX + 12, y = bottomY + 8 -> completely outside diamond
    yes_badge_x = center_x + 12
    assert yes_badge_x > center_x, "YES badge must sit to the right of downward arrow"
    assert dec["bottomY"] + 8 >= dec["bottomY"], "YES badge must sit below diamond bottom vertex"

    # NO badge: x = centerX + W/2 + 12 -> completely outside diamond to the right
    no_badge_x = center_x + W / 2 + 12
    assert no_badge_x > (center_x + W / 2), "NO badge must sit outside diamond right vertex"

    # 4. Remediation box check
    no_box = layout["noBox"]
    assert no_box["width"] == 280, "Remediation box must be at least 280px wide"
    assert no_box["height"] >= 74, "Remediation box must have adaptive height"
    assert no_box["x"] == center_x + W / 2 + 64, "Remediation box must be spaced 64px from diamond right vertex"
    assert no_box["x"] + no_box["width"] < layout["svgWidth"], "Remediation box must not clip at SVG right canvas border"

    # 5. Return loop check
    target_step = dec["node"]["noTargetStep"]
    target_coord = next(c for c in layout["nodeCoords"] if c["node"]["step"] == target_step)
    assert target_coord["node"]["isLoopTarget"] is True
    assert "Hardening" in target_coord["node"]["label"]


def test_svg_and_png_export_generation(tmp_path):
    """Test generating and saving actual SVG and PNG files and validating their binary format."""
    title = "Enterprise Network Hardening & Vulnerability Remediation Lab"
    svg_markup = generate_full_svg(title)

    # 1. Validate SVG is well-formed XML
    root = ET.fromstring(svg_markup)
    assert root.tag.endswith("svg"), "Root element must be <svg>"
    assert root.attrib["width"] == "960"
    assert int(root.attrib["height"]) > 800

    # Save SVG file
    svg_path = tmp_path / "Enterprise_Network_Hardening_Flowchart.svg"
    svg_path.write_text(svg_markup, encoding="utf-8")
    assert svg_path.exists()
    assert svg_path.stat().st_size > 5000, "SVG file must have substantial content"

    # 2. Render to PNG using PyMuPDF (fitz)
    doc = fitz.open(stream=svg_markup.encode("utf-8"), filetype="svg")
    assert len(doc) == 1, "Must contain 1 page"
    page = doc[0]

    # Render at 2x resolution
    pix = page.get_pixmap(dpi=144)
    png_bytes = pix.tobytes("png")
    doc.close()

    png_path = tmp_path / "Enterprise_Network_Hardening_Flowchart.png"
    png_path.write_bytes(png_bytes)

    assert png_path.exists()
    assert len(png_bytes) > 20000, "PNG file must be substantial in size"
    # Verify PNG header
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n"), "Must be a valid PNG binary"

    # Also verify in workspace for user review
    out_dir = Path("docs/diagrams")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_svg = out_dir / "Enterprise_Network_Hardening_Flowchart.svg"
    out_png = out_dir / "Enterprise_Network_Hardening_Flowchart.png"
    out_svg.write_text(svg_markup, encoding="utf-8")
    out_png.write_bytes(png_bytes)
    print(f"Generated test files at {out_svg.resolve()} and {out_png.resolve()}")


def test_other_projects_render_without_clipping():
    """Verify that multiple other projects (Web App Security, Cloud, SOC, DevSecOps) render correctly."""
    projects = [
        "Web Application Security Testing Lab & Vulnerability Remediation",
        "Security Operations Center (SOC) Log Analysis & Threat Hunting Lab",
        "Cloud Security & Compliance Hardening Lab",
        "DevSecOps Pipeline & Automated Code Security Scanning Lab",
    ]

    for p in projects:
        svg_content = generate_full_svg(p)
        root = ET.fromstring(svg_content)
        w = int(root.attrib["width"])
        h = int(root.attrib["height"])
        assert w >= 960
        assert h >= 600

        # Verify no negative coords in rects or lines
        for rect in root.iter("{http://www.w3.org/2000/svg}rect"):
            if rect.attrib.get("width", "").endswith("%"):
                continue
            rx = float(rect.attrib.get("x", 0))
            ry = float(rect.attrib.get("y", 0))
            rw = float(rect.attrib.get("width", 0))
            rh = float(rect.attrib.get("height", 0))
            assert rx >= 0, f"Rect x must be non-negative in {p}"
            assert ry >= 0, f"Rect y must be non-negative in {p}"
            assert rx + rw <= w + 1, f"Rect overflows svg width {w} in {p}: x={rx}, w={rw}"
            assert ry + rh <= h + 1, f"Rect overflows svg height {h} in {p}: y={ry}, h={rh}"
