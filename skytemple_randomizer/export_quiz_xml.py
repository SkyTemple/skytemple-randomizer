#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

from typing import TYPE_CHECKING
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from skytemple_files.common.i18n_util import _
from skytemple_files.common.xml_util import (
    prettify,
    validate_xml_tag,
    XmlValidateError,
)

from skytemple_randomizer.config import QuizQuestion

if TYPE_CHECKING:
    from io import BufferedWriter, BufferedReader


XML_QUESTIONS = "Questions"
XML_QUESTION = "Question"
XML_TEXT = "Text"
XML_ANSWERS = "Answers"
XML_ANSWER = "Answer"


def export_personality_quiz_xml(questions: list[QuizQuestion], file: BufferedWriter):
    xml = Element(XML_QUESTIONS)

    for question in questions:
        question_xml = Element(XML_QUESTION)

        text_xml = Element(XML_TEXT)
        text_xml.text = question["question"]
        question_xml.append(text_xml)

        answers_xml = Element(XML_ANSWERS)
        for answer in question["answers"]:
            answer_xml = Element(XML_ANSWER)
            answer_xml.text = answer
            answers_xml.append(answer_xml)
        question_xml.append(answers_xml)

        xml.append(question_xml)

    file.write(prettify(xml))


def import_personality_quiz_xml(file: BufferedReader) -> list[QuizQuestion]:
    xml = ElementTree.parse(file).getroot()

    validate_xml_tag(xml, XML_QUESTIONS)
    questions_output = []
    for question in xml:
        validate_xml_tag(question, XML_QUESTION)
        question_output: QuizQuestion = {"question": "", "answers": []}
        found_question = False
        found_answers = False
        for question_content in question:
            if question_content.tag == XML_TEXT:
                found_question = True
                if question_content.text is not None:
                    question_output["question"] = question_content.text
            elif question_content.tag == XML_ANSWERS:
                found_answers = True
                for answer in question_content:
                    validate_xml_tag(answer, XML_ANSWER)
                    if answer.text is not None:
                        question_output["answers"].append(answer.text)
            else:
                raise_missing_node()
        if not found_answers or not found_question:
            raise_missing_node()

        questions_output.append(question_output)

    return questions_output


def raise_missing_node():
    raise XmlValidateError(_("A question must contain two XML sub-nodes: {}, {}".format(XML_TEXT, XML_ANSWERS)))
