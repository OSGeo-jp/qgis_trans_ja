#!/usr/bin/env python3

# Referred mint-check-translations, but changed much
# https://github.com/linuxmint/mint-dev-tools/blob/master/usr/bin/mint-check-translations

import argparse
import polib
import os
from attrdict import AttrDict
from docutils.parsers.rst import roles
from docutils.parsers.rst.states import Inliner, Struct
from docutils.utils import Reporter, new_document
from io import StringIO

PO_EXT = ".po"

# https://www.sphinx-doc.org/en/1.8/usage/restructuredtext/roles.html
SPHINX_ROLES = [
    # Cross-referencing documents
    'any', 'ref', 'doc', 'download', 'numref', 'envvar', 'token', 'keyword', 'option', 'term',
    # Math
    'math', 'eq',
    # Other semantic markup
    'abbr', 'command', 'dfn', 'file', 'guilabel', 'kbd', 'mailheader', 'makevar', 'manpage', 'menuselection',
    'mimetype', 'newsgroup', 'program', 'regexp', 'samp', 'pep', 'rfc'
]


class Po:
    def __init__(self, inst, file, path):
        self.inst = inst
        self.file = file.replace(".po", "")
        self.current_index = 1


class Main:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Check target files')
        parser.add_argument('directory', nargs='?', default='./target',
                            help="A directory to check (default is to check './target')")
        self.args = parser.parse_args()
        self.type = PO_EXT
        for role in SPHINX_ROLES:
            roles.register_local_role(role, self.docutils_role_fn)
        self.issue_count = 0
        self.load_files()
        if self.issue_count > 0:
            print("\n%d issues found" % self.issue_count)
            exit(1)

    def load_files(self):
        count_files = 0
        for root, subFolders, files in os.walk(self.args.directory, topdown=False):
            for file in files:
                if file.endswith(PO_EXT):
                    po_inst = polib.pofile(os.path.join(root, file))
                    po = Po(po_inst, file, os.path.join(root, file))
                else:
                    continue
                count_files += 1
                self.check_file(po)

    def check_file(self, po):
        for entry in po.inst:
            if entry.obsolete:
                continue  # skip obsolete translations (prefixed with #~ in po file)
            issue_found = False
            msgid = entry.msgid
            msgstr = entry.msgstr
            if ".rst" in str(entry):
                # Sphinx build equivalent
                res = self.check_docutils_inliner(po, msgstr)
                if len(res) > 0:
                    issue_found = True

            if issue_found:
                self.print_issue(po, msgid, msgstr, res, po.current_index)
                self.issue_count += 1

            po.current_index += 1

    @staticmethod
    def docutils_role_fn(typ, rawtext, text, lineno, inliner, options={}, content=[]):
        return [], []

    @staticmethod
    def check_docutils_inliner(po, msgstr):
        inliner = Inliner()
        settings = AttrDict({'character_level_inline_markup': False, 'pep_references': None, 'rfc_references': None})
        inliner.init_customizations(settings)
        document = new_document(None)
        document.settings.syntax_highlight = 'long'
        stream = StringIO()
        reporter = Reporter(po.file, report_level=Reporter.WARNING_LEVEL,
                            halt_level=Reporter.SEVERE_LEVEL, stream=stream)
        memo = Struct(document=document, reporter=reporter, language=None, inliner=inliner)
        inliner.parse(msgstr, po.current_index, memo, None)
        return stream.getvalue()

    @staticmethod
    def print_issue(po, msgid, msgstr, issue, current_index):
        # print("po: %s" % po)
        print("==========================")
        print("file: %s" % po.file)
        print("index: %s" % current_index)
        print("msgid: %s" % msgid)
        print("msgstr: %s" % msgstr)
        print("issue: %s" % issue)


if __name__ == "__main__":
    Main()
