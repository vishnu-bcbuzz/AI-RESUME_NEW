"""Automated tests for persistent Round Robin scheduler."""

import tempfile
from pathlib import Path
import threading
import pytest

from app.reports.round_robin import RoundRobinScheduler
from app.reports.templates import TemplateRegistry, ResumeTemplate


@pytest.fixture
def clean_scheduler():
    temp_dir = Path(tempfile.mkdtemp())
    state_file = temp_dir / "test_rr.json"
    assignments_file = temp_dir / "test_assignments.json"
    scheduler = RoundRobinScheduler(state_file=state_file, assignments_file=assignments_file)
    scheduler.reset_cursor(0)
    return scheduler


def test_round_robin_sequential_sequence(clean_scheduler):
    """Verifies sequence: T01 -> T02 -> ... -> T30 -> T01 -> T02."""
    sequence = []
    for _ in range(32):
        tmpl, _ = clean_scheduler.select_next_template()
        sequence.append(tmpl.template_id)

    expected = [
        f"T{i:02d}" for i in range(1, 31)
    ] + ["T01", "T02"]
    assert sequence == expected


def test_round_robin_persistence(clean_scheduler):
    """Verifies that cursor state survives application restart."""
    state_file = clean_scheduler.state_file

    # Advance cursor by 3
    clean_scheduler.select_next_template()  # T01
    clean_scheduler.select_next_template()  # T02
    clean_scheduler.select_next_template()  # T03

    # Instantiate brand new scheduler instance simulating app restart
    restarted = RoundRobinScheduler(state_file=state_file, assignments_file=clean_scheduler.assignments_file)
    tmpl, _ = restarted.select_next_template()
    assert tmpl.template_id == "T04"


def test_round_robin_idempotent_retry(clean_scheduler):
    """Verifies that retrying with existing job_id preserves the assigned template without advancing counter."""
    job_id = "retry_job_123"
    tmpl1, rec1 = clean_scheduler.select_next_template(job_id=job_id)
    initial_cursor = clean_scheduler.get_current_cursor()

    # Retry with same job_id
    tmpl2, rec2 = clean_scheduler.select_next_template(job_id=job_id)
    assert tmpl1.template_id == tmpl2.template_id
    assert clean_scheduler.get_current_cursor() == initial_cursor
    assert rec2.retry_count == 1


def test_inactive_template_exclusion():
    """Verifies that disabled templates are skipped."""
    temp_dir = Path(tempfile.mkdtemp())
    test_templates = [
        ResumeTemplate(template_id="T1", template_name="T1", description="d", is_active=True),
        ResumeTemplate(template_id="T2", template_name="T2", description="d", is_active=False),  # Inactive
        ResumeTemplate(template_id="T3", template_name="T3", description="d", is_active=True),
    ]
    custom_reg = TemplateRegistry(test_templates)
    sched = RoundRobinScheduler(state_file=temp_dir / "inactive_test.json", registry=custom_reg)
    sched.reset_cursor(0)

    t_a, _ = sched.select_next_template()
    t_b, _ = sched.select_next_template()
    t_c, _ = sched.select_next_template()

    assert t_a.template_id == "T1"
    assert t_b.template_id == "T3"
    assert t_c.template_id == "T1"  # Wraps around skipping T2


def test_concurrent_requests(clean_scheduler):
    """Verifies concurrency safety across 20 threads."""
    results = []
    lock = threading.Lock()

    def worker():
        tmpl, _ = clean_scheduler.select_next_template()
        with lock:
            results.append(tmpl.template_id)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 20
    assert clean_scheduler.get_current_cursor() == 20
