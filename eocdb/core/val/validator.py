import json
import os

from eocdb.core.val._date_record_rule import DateRecordRule
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val._meta_field_obsolete_rule import MetaFieldObsoleteRule
from eocdb.core.val._number_record_rule import NumberRecordRule
from eocdb.core.val._string_record_rule import StringRecordRule
from ..models.dataset import Dataset
from ..models.dataset_validation_result import DatasetValidationResult
from ..models.issue import ISSUE_TYPE_WARNING, ISSUE_TYPE_ERROR, Issue
from ...core.val._message_library import MessageLibrary
from ...core.val._meta_field_compare_rule import MetaFieldCompareRule
from ...core.val._meta_field_optional_rule import MetaFieldOptionalRule
from ...core.val._meta_field_required_rule import MetaFieldRequiredRule
from ...ws.context import Config

validator_inst = None


def validate_dataset(dataset: Dataset, config: Config) -> DatasetValidationResult:
    global validator_inst
    if validator_inst is None:
        validator_inst = Validator()

    if "mock_validation" in config:
        return DatasetValidationResult("OK", [])

    return validator_inst.validate_dataset(dataset)


class Validator(MessageLibrary):

    def __init__(self):
        file = os.path.join(os.path.dirname(__file__), "res", "validation_config.json")

        with open(file) as f:
            rules_config = json.load(f)

        self._parse_rules(rules_config)

    def validate_dataset(self, dataset: Dataset) -> DatasetValidationResult:
        issues = []

        header_errors = self._validate_header(dataset, issues)
        data_errors = self._validate_measurements(dataset, issues)

        num_errors = header_errors + data_errors

        status = "OK" if not issues else ISSUE_TYPE_ERROR if num_errors else ISSUE_TYPE_WARNING
        validation_result = DatasetValidationResult(status, issues)
        return validation_result

    def resolve_warning(self, template: str, tokens: GapAwareDict) -> str:
        warning = template
        if template.startswith("@"):
            template_key = template[1:]
            if not template_key in self._warning_messages:
                raise Exception("Requested warning message not defined: " + template_key)
            warning = self._warning_messages[template_key]

        return warning.format_map(tokens)

    def resolve_error(self, template: str, tokens: GapAwareDict) -> str:
        error = template
        if template.startswith("@"):
            template_key = template[1:]
            if not template_key in self._error_messages:
                raise Exception("Requested error message not defined: " + template_key)
            error = self._error_messages[template_key]

        return error.format_map(tokens)

    def _validate_header(self, dataset, issues) -> int:
        num_errors = 0
        for rule in self._header_rules:
            issue = rule.eval(dataset, self)
            if issue:
                issues.append(issue)
                if issue.type == ISSUE_TYPE_ERROR:
                    num_errors += 1
        return num_errors

    def _validate_measurements(self, dataset, issues) -> int:
        if not "fields" in dataset.metadata or not "units" in dataset.metadata:
            issues.append(Issue(ISSUE_TYPE_ERROR,
                                "Header tags /fields or /units missing. Skipping parsing of measurement records."))
            return 1

        var_names_list = dataset.metadata["fields"]
        var_names = var_names_list.lower().split(",")
        units_list = dataset.metadata["units"]
        units = units_list.lower().split(",")

        if len(var_names) != len(units):
            issues.append(Issue(ISSUE_TYPE_ERROR,
                                "Number of fields and units does not match. Skipping parsing of measurement records."))
            return 1

        index = 0
        errors = 0
        for variable in var_names:
            if not variable in self._record_rules:
                issues.append(Issue(ISSUE_TYPE_WARNING,
                                    "Variable not listed in valid variables: " + variable))
                index += 1
                continue

            rule = self._record_rules[variable]
            values = []
            for record in dataset.records:
                values.append(record[index])

            record_issues = rule.eval(units[index], values, self)
            if record_issues is not None:
                issues.extend(record_issues)
                for record_issue in record_issues:
                    if ISSUE_TYPE_ERROR == record_issue.type:
                        errors += 1

            index += 1

        return errors

    def _parse_rules(self, rules_config):
        self._parse_header_rules(rules_config)
        self._parse_record_rules(rules_config)
        self._parse_error_messages(rules_config)
        self._parse_warning_messages(rules_config)

    def _parse_warning_messages(self, rules_config):
        self._warning_messages = {}
        warnings_config = rules_config["warnings"]
        for warning in warnings_config:
            self._warning_messages[warning["name"]] = warning["message"]

    def _parse_error_messages(self, rules_config):
        self._error_messages = {}
        errors_config = rules_config["errors"]
        for error in errors_config:
            self._error_messages[error["name"]] = error["message"]

    def _parse_header_rules(self, rules_config):
        self._header_rules = []
        header_rules = rules_config["header"]
        for header_rule in header_rules:
            rule_type = header_rule["type"]
            if "field_compare" == rule_type:
                rule = self._create_meta_field_compare_rule(header_rule)
                self._header_rules.append(rule)
            elif "field_required" == rule_type:
                name = header_rule["name"]
                error = header_rule["error"]
                rule = MetaFieldRequiredRule(name, error)
                self._header_rules.append(rule)
            elif "field_optional" == rule_type:
                name = header_rule["name"]
                warning = header_rule["warning"]
                rule = MetaFieldOptionalRule(name, warning)
                self._header_rules.append(rule)
            elif "field_obsolete" == rule_type:
                name = header_rule["name"]
                warning = header_rule["warning"]
                rule = MetaFieldObsoleteRule(name, warning)
                self._header_rules.append(rule)
            else:
                raise ValueError("Invalid type of header validation rule: " + rule_type)

    def _parse_record_rules(self, rules_config):
        self._record_rules = {}

        record_rules = rules_config["record"]
        for record_rule in record_rules:
            data_type = record_rule["data_type"]
            name = record_rule["name"]
            if "number" == data_type:
                rule = NumberRecordRule.from_dict(record_rule)
                self._record_rules.update({name: rule})
            elif "string" == data_type:
                rule = StringRecordRule.from_dict(record_rule)
                self._record_rules.update({name: rule})
            elif "date" == data_type:
                rule = DateRecordRule.from_dict(record_rule)
                self._record_rules.update({name: rule})
            else:
                raise ValueError("Invalid data type in field validation rule: " + data_type)

    @staticmethod
    def _create_meta_field_compare_rule(header_rule):
        reference = header_rule["reference"]
        compare = header_rule["compare"]
        operation = header_rule["operation"]
        data_type = header_rule["data_type"]
        if "error" in header_rule:
            error = header_rule["error"]
        else:
            error = None
        if "warning" in header_rule:
            warning = header_rule["warning"]
        else:
            warning = None
        rule = MetaFieldCompareRule(reference, compare, operation, error=error, warning=warning, data_type=data_type)
        return rule
