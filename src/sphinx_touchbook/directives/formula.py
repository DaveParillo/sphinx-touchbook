"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
---

A Touchbook directive for calculated numeric formula assessments.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import re
import shlex
from typing import NamedTuple

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbFormulaNode, TbFormulaPromptNode, TbFormulaVariableNode

FORMULA_RE = re.compile(r"^(?P<indent>\s*)\.\.\s+answer-formula::(?:\s+(?P<language>\S+))?\s*$")
OPTION_RE = re.compile(r"^\s*:(?P<name>[A-Za-z-]+):(?:\s*(?P<value>.*))?$")
VARIABLE_RE = re.compile(r"\{\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)\}\}")
VARIABLE_SPEC_RE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(?P<minimum>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\.\.\s*"
    r"(?P<maximum>[+-]?(?:\d+(?:\.\d*)?|\.\d+))$"
)


class FormulaError(ValueError):
    """Raised when tb-formula content is invalid."""


class FormulaBlock(NamedTuple):
    language: str
    source: str
    parameters: dict[str, list[str]]


def _nonnegative_float(argument: str) -> float:
    value = float(argument)
    if value < 0:
        raise ValueError("negative value; must be positive or zero")
    return value


class TbFormulaDirective(Directive):
    """Parse a calculated formula assessment."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
        "variables": directives.unchanged_required,
        "tolerance": _nonnegative_float,
    }

    def run(self):
        self.assert_has_content()
        try:
            prompt_lines, formula = self._split_content()
            parsed = nodes.container()
            self.state.nested_parse(prompt_lines, self.content_offset, parsed)
            node = self._build_node(parsed, formula)
        except FormulaError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        return [node]

    def _split_content(self) -> tuple[StringList, FormulaBlock]:
        prompt_lines = StringList()
        formulas: list[FormulaBlock] = []
        index = 0
        while index < len(self.content):
            line = self.content[index]
            match = FORMULA_RE.match(line)
            if match is None:
                prompt_lines.append(line, source=self.content.source(index), offset=self.content.offset(index))
                index += 1
                continue

            block_indent = len(match.group("indent"))
            language = match.group("language") or "javascript"
            block_lines = []
            index += 1
            while index < len(self.content):
                next_line = self.content[index]
                nested_match = FORMULA_RE.match(next_line)
                if nested_match is not None and len(nested_match.group("indent")) <= block_indent:
                    break
                if next_line.strip() and self._indent_width(next_line) <= block_indent:
                    break
                block_lines.append(next_line[block_indent + 3 :] if len(next_line) > block_indent + 3 else "")
                index += 1
            formulas.append(self._formula_block(language, block_lines))

        if len(formulas) != 1:
            raise FormulaError("tb-formula must contain exactly one nested answer-formula block.")
        return prompt_lines, formulas[0]

    def _build_node(self, parsed: nodes.container, formula: FormulaBlock) -> TbFormulaNode:
        variables = self._parse_variables(self.options.get("variables", ""))
        prompt = TbFormulaPromptNode()
        prompt.extend(deepcopy(child) for child in parsed.children)
        placeholders = self._replace_variable_markers(prompt)
        missing = sorted(set(placeholders) - set(variables))
        if missing:
            raise FormulaError(f"tb-formula placeholders are missing variable ranges: {', '.join(missing)}.")
        if not placeholders:
            raise FormulaError("tb-formula prompt must contain at least one {{variable}} marker.")

        node = TbFormulaNode()
        assign_node_id(self, node)
        node["variables"] = variables
        node["formula"] = {
            "language": formula.language,
            "source": formula.source,
            "parameters": self._formula_parameters(formula),
        }
        node["tolerance"] = float(self.options.get("tolerance", 0))
        node += prompt
        return node

    def _formula_block(self, language: str, lines: list[str]) -> FormulaBlock:
        parameters: dict[str, list[str]] = {}
        source_lines: list[str] = []
        parsing_options = True
        for line in lines:
            option = OPTION_RE.match(line) if parsing_options else None
            if option is not None:
                name = option.group("name")
                if name not in {"compileargs", "linkargs", "runargs", "interpreterargs"}:
                    raise FormulaError(f"Unsupported answer-formula option ':{name}:'.")
                parameters[name] = _as_arg_list(option.group("value") or "")
                continue
            if parsing_options and not line.strip():
                continue
            parsing_options = False
            source_lines.append(line)

        source = "\n".join(source_lines).strip()
        if not source:
            raise FormulaError("answer-formula must contain a formula or program.")
        return FormulaBlock(language=language, source=source, parameters=parameters)

    def _formula_parameters(self, formula: FormulaBlock) -> dict[str, list[str]]:
        config = _config_from_state(self.state)
        defaults = getattr(config, "tb_formula_language_defaults", {}) if config is not None else {}
        language_defaults = defaults.get(formula.language, {}) if isinstance(defaults, dict) else {}
        parameters = {}
        for name in ("compileargs", "linkargs", "runargs", "interpreterargs"):
            value = formula.parameters.get(name, language_defaults.get(name))
            parameters[name] = _as_arg_list(value)
        return parameters

    def _parse_variables(self, value: str) -> dict[str, dict[str, float | bool]]:
        variables: dict[str, dict[str, float | bool]] = {}
        for part in re.split(r"[;,]", value):
            spec = part.strip()
            if not spec:
                continue
            match = VARIABLE_SPEC_RE.match(spec)
            if match is None:
                raise FormulaError(f"Invalid variable range '{spec}'. Use name=min..max.")
            name = match.group("name")
            minimum_text = match.group("minimum")
            maximum_text = match.group("maximum")
            minimum = float(minimum_text)
            maximum = float(maximum_text)
            if minimum > maximum:
                raise FormulaError(f"Variable '{name}' minimum must be less than or equal to maximum.")
            variables[name] = {
                "min": minimum,
                "max": maximum,
                "integer": _is_integer_text(minimum_text) and _is_integer_text(maximum_text),
            }
        if not variables:
            raise FormulaError("tb-formula requires at least one variable range in :variables:.")
        return variables

    def _replace_variable_markers(self, root: nodes.Element) -> list[str]:
        placeholders = []
        for text_node in list(root.findall(nodes.Text)):
            text = text_node.astext()
            parts: list[nodes.Node] = []
            last = 0
            for match in VARIABLE_RE.finditer(text):
                if match.start() > last:
                    parts.append(nodes.Text(text[last : match.start()]))
                name = match.group("name")
                variable = TbFormulaVariableNode()
                variable["name"] = name
                parts.append(variable)
                placeholders.append(name)
                last = match.end()
            if not parts:
                continue
            if last < len(text):
                parts.append(nodes.Text(text[last:]))
            text_node.parent.replace(text_node, parts)
        return placeholders

    def _indent_width(self, line: str) -> int:
        return len(line) - len(line.lstrip(" "))


def _config_from_state(state):
    settings = getattr(state.document, "settings", None)
    env = getattr(settings, "env", None)
    return getattr(env, "config", None)


def _as_arg_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = ast.literal_eval(stripped)
        except (SyntaxError, ValueError):
            return shlex.split(stripped)
        if isinstance(parsed, (list, tuple)):
            return [str(item) for item in parsed]
        if isinstance(parsed, str):
            return [parsed]
        return [str(parsed)]
    return [str(value)]


def _is_integer_text(value: str) -> bool:
    try:
        return float(value).is_integer() and "." not in value
    except ValueError:
        return False
