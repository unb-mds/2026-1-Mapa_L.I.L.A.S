"""
Testes estruturais para validar o schedule otimizado do workflow de ingestão.

Ref: Issue #77 — ci: Otimizar schedule do workflow de ingestão para economizar Actions
"""

import yaml
import pathlib
import pytest

WORKFLOWS = pathlib.Path(__file__).resolve().parent.parent / ".github" / "workflows"


def load_workflow(name: str) -> dict:
    path = WORKFLOWS / name
    assert path.exists(), f"Workflow {name} não encontrado em {WORKFLOWS}"
    with open(path) as f:
        return yaml.safe_load(f)


class TestDataIngestionSchedule:
    @pytest.fixture
    def workflow(self):
        return load_workflow("data-ingestion.yml")

    def test_cron_runs_tuesday_to_saturday_utc(self, workflow):
        """Terça a sábado UTC = segunda a sexta 23:57 BRT"""
        on = workflow.get(True, workflow.get("on", {}))
        schedules = on.get("schedule", [])
        crons = [s["cron"] for s in schedules]
        assert "57 2 * * 2-6" in crons, (
            f"Cron deve ser '57 2 * * 2-6' (seg-sex 23:57 BRT), encontrado: {crons}"
        )

    def test_cron_does_not_run_on_sunday_or_monday_utc(self, workflow):
        """Não deve rodar domingo (0) nem segunda (1) UTC"""
        on = workflow.get(True, workflow.get("on", {}))
        schedules = on.get("schedule", [])
        crons = [s["cron"] for s in schedules]
        for cron in crons:
            day_field = cron.strip().split()[4]
            assert "0" not in day_field.split(","), (
                f"Cron não deve incluir domingo (0) UTC: {cron}"
            )
            assert "1" not in day_field.split(","), (
                f"Cron não deve incluir segunda (1) UTC: {cron}"
            )
            assert "*" != day_field, (
                f"Cron não deve usar wildcard (*) nos dias: {cron}"
            )

    def test_workflow_dispatch_still_available(self, workflow):
        """workflow_dispatch deve continuar disponível para execuções manuais"""
        on = workflow.get(True, workflow.get("on", {}))
        assert "workflow_dispatch" in on or on.get("workflow_dispatch") is not None, (
            "workflow_dispatch deve permanecer disponível"
        )
