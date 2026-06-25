"""
Testes estruturais para validar que os workflows de CI
incluem o job de deploy do Pages após commits automáticos.

Ref: Issue #76 — fix: Pages não atualiza automaticamente
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


# ──────────────────────────────────────────────
# Ciclo 1: data-ingestion.yml — permissões
# ──────────────────────────────────────────────

class TestDataIngestionPermissions:
    @pytest.fixture
    def workflow(self):
        return load_workflow("data-ingestion.yml")

    def test_has_pages_write_permission(self, workflow):
        perms = workflow.get("permissions", {})
        assert perms.get("pages") == "write", (
            "data-ingestion.yml deve ter permissions.pages: write"
        )

    def test_has_id_token_write_permission(self, workflow):
        perms = workflow.get("permissions", {})
        assert perms.get("id-token") == "write", (
            "data-ingestion.yml deve ter permissions.id-token: write"
        )


# ──────────────────────────────────────────────
# Ciclo 2: data-ingestion.yml — concurrency
# ──────────────────────────────────────────────

class TestDataIngestionConcurrency:
    @pytest.fixture
    def workflow(self):
        return load_workflow("data-ingestion.yml")

    def test_has_concurrency_group_pages(self, workflow):
        conc = workflow.get("concurrency", {})
        assert conc.get("group") == "pages", (
            "data-ingestion.yml deve ter concurrency.group: 'pages'"
        )


# ──────────────────────────────────────────────
# Ciclo 3: data-ingestion.yml — job deploy-pages
# ──────────────────────────────────────────────

class TestDataIngestionDeployJob:
    @pytest.fixture
    def workflow(self):
        return load_workflow("data-ingestion.yml")

    @pytest.fixture
    def deploy_job(self, workflow):
        jobs = workflow.get("jobs", {})
        assert "deploy-pages" in jobs, (
            "data-ingestion.yml deve ter o job 'deploy-pages'"
        )
        return jobs["deploy-pages"]

    def test_deploy_depends_on_ingestion(self, deploy_job):
        needs = deploy_job.get("needs")
        if isinstance(needs, str):
            needs = [needs]
        assert "ingestion" in needs, (
            "deploy-pages deve depender do job 'ingestion'"
        )

    def test_deploy_has_checkout_step(self, deploy_job):
        steps = deploy_job.get("steps", [])
        checkout_steps = [s for s in steps if s.get("uses", "").startswith("actions/checkout")]
        assert len(checkout_steps) >= 1, "deploy-pages deve ter step de checkout"

    def test_deploy_has_mkdocs_build_step(self, deploy_job):
        steps = deploy_job.get("steps", [])
        build_steps = [s for s in steps if "mkdocs build" in s.get("run", "")]
        assert len(build_steps) >= 1, "deploy-pages deve ter step de mkdocs build"

    def test_deploy_copies_dashboards(self, deploy_job):
        steps = deploy_job.get("steps", [])
        copy_steps = [s for s in steps if "cp -r" in s.get("run", "") or "docs/scrum" in s.get("run", "")]
        assert len(copy_steps) >= 1, "deploy-pages deve copiar dashboards para site/"

    def test_deploy_has_upload_pages_artifact(self, deploy_job):
        steps = deploy_job.get("steps", [])
        upload_steps = [s for s in steps if "upload-pages-artifact" in s.get("uses", "")]
        assert len(upload_steps) >= 1, "deploy-pages deve ter upload-pages-artifact"

    def test_deploy_has_deploy_pages_action(self, deploy_job):
        steps = deploy_job.get("steps", [])
        deploy_steps = [s for s in steps if "deploy-pages" in s.get("uses", "")]
        assert len(deploy_steps) >= 1, "deploy-pages deve ter actions/deploy-pages"


# ──────────────────────────────────────────────
# Ciclo 4: scrum metrics.yml — permissões
# ──────────────────────────────────────────────

class TestScrumMetricsPermissions:
    @pytest.fixture
    def workflow(self):
        return load_workflow("scrum metrics.yml")

    def test_has_pages_write_permission(self, workflow):
        perms = workflow.get("permissions", {})
        assert perms.get("pages") == "write", (
            "scrum metrics.yml deve ter permissions.pages: write"
        )

    def test_has_id_token_write_permission(self, workflow):
        perms = workflow.get("permissions", {})
        assert perms.get("id-token") == "write", (
            "scrum metrics.yml deve ter permissions.id-token: write"
        )


# ──────────────────────────────────────────────
# Ciclo 5: scrum metrics.yml — concurrency e deploy
# ──────────────────────────────────────────────

class TestScrumMetricsDeployJob:
    @pytest.fixture
    def workflow(self):
        return load_workflow("scrum metrics.yml")

    @pytest.fixture
    def deploy_job(self, workflow):
        jobs = workflow.get("jobs", {})
        assert "deploy-pages" in jobs, (
            "scrum metrics.yml deve ter o job 'deploy-pages'"
        )
        return jobs["deploy-pages"]

    def test_has_concurrency_group_pages(self, workflow):
        conc = workflow.get("concurrency", {})
        assert conc.get("group") == "pages", (
            "scrum metrics.yml deve ter concurrency.group: 'pages'"
        )

    def test_deploy_depends_on_build_and_commit(self, deploy_job):
        needs = deploy_job.get("needs")
        if isinstance(needs, str):
            needs = [needs]
        assert "build-and-commit" in needs, (
            "deploy-pages deve depender do job 'build-and-commit'"
        )

    def test_deploy_has_mkdocs_build_step(self, deploy_job):
        steps = deploy_job.get("steps", [])
        build_steps = [s for s in steps if "mkdocs build" in s.get("run", "")]
        assert len(build_steps) >= 1, "deploy-pages deve ter step de mkdocs build"

    def test_deploy_has_deploy_pages_action(self, deploy_job):
        steps = deploy_job.get("steps", [])
        deploy_steps = [s for s in steps if "deploy-pages" in s.get("uses", "")]
        assert len(deploy_steps) >= 1, "deploy-pages deve ter actions/deploy-pages"


# ──────────────────────────────────────────────
# Ciclo 6: static.yml — deve continuar intacto
# ──────────────────────────────────────────────

class TestStaticWorkflowUntouched:
    @pytest.fixture
    def workflow(self):
        return load_workflow("static.yml")

    def test_still_triggers_on_push_to_main(self, workflow):
        on = workflow.get(True, workflow.get("on", {}))
        push = on.get("push", {})
        branches = push.get("branches", [])
        assert "main" in branches, "static.yml deve continuar triggerando em push para main"

    def test_still_has_build_and_deploy_jobs(self, workflow):
        jobs = workflow.get("jobs", {})
        assert "build" in jobs, "static.yml deve manter o job build"
        assert "deploy" in jobs, "static.yml deve manter o job deploy"
