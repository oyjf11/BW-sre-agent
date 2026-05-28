from types import SimpleNamespace

from app.rag.writer import write_back_confirmed_rca


class FakeRcaRepo:
    def __init__(self, rca):
        self.rca = rca

    def get(self, run_id):
        return self.rca


class FakeRunsRepo:
    def __init__(self, run=None):
        self.run = run

    def get(self, run_id):
        return self.run


def test_write_back_confirmed_rca_indexes_only_confirmed_reports():
    rca = SimpleNamespace(
        run_id="run-confirmed",
        report_markdown="## RCA\nSQL 慢查询导致支付服务 5xx",
        root_cause="SQL 慢查询",
        resolution="加索引并回滚发布",
        prevention_items_json=["上线前检查慢查询"],
        confirmed_by_human=1,
    )
    run = SimpleNamespace(service="payment-service", env="prod", severity="P1")
    indexed = {}

    def fake_index_documents(documents):
        docs = list(documents)
        indexed["docs"] = docs
        return SimpleNamespace(document_count=len(docs), chunk_count=len(docs), doc_ids=[doc.doc_id for doc in docs])

    result = write_back_confirmed_rca(
        run_id="run-confirmed",
        rca_repo=FakeRcaRepo(rca),
        runs_repo=FakeRunsRepo(run),
        index_documents_fn=fake_index_documents,
    )

    assert result.document_count == 1
    assert indexed["docs"][0].doc_type == "rca"
    assert indexed["docs"][0].metadata["service"] == "payment-service"


def test_write_back_confirmed_rca_skips_unconfirmed_reports():
    rca = SimpleNamespace(confirmed_by_human=0)

    result = write_back_confirmed_rca(
        run_id="run-draft",
        rca_repo=FakeRcaRepo(rca),
        runs_repo=FakeRunsRepo(),
        index_documents_fn=lambda docs: (_ for _ in ()).throw(AssertionError("should not index")),
    )

    assert result is None
