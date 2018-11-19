from typing import Callable, Optional

from eocdb.core.models.qc_info import QC_INFO_STATUS_WAITING
from ..models.dataset import Dataset
from ..models.dataset_validation_result import DatasetValidationResult
from ..models.issue import Issue

ValidationRule = Callable[[Dataset], Optional[Issue]]

ISSUE_TYPE_ERROR = "ERROR"
ISSUE_TYPE_WARNING = "WARNING"


def assert_id_is_none(dataset: Dataset) -> Optional[Issue]:
    qc_status = dataset.metadata.get("qc_status", QC_INFO_STATUS_WAITING)
    if qc_status == QC_INFO_STATUS_WAITING and dataset.id is not None:
        return Issue(ISSUE_TYPE_WARNING, "Datasets should have no ID before insert or update")
    return None


_VALIDATION_RULES = [
    assert_id_is_none,
]


def validate_dataset(dataset: Dataset) -> DatasetValidationResult:
    issues = []
    num_errors = 0
    for rule in _VALIDATION_RULES:
        issue = rule(dataset)
        if issue:
            issues.append(issue)
            if issue.type == ISSUE_TYPE_ERROR:
                num_errors += 1

    status = "OK" if not issues else ISSUE_TYPE_ERROR if num_errors else ISSUE_TYPE_WARNING
    validation_result = DatasetValidationResult(status, issues)
    return validation_result