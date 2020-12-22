#!/usr/bin/env python3

import argparse
import os
import io

from babel.messages import pofile

PO_EXT = ".po"


def load_catalogs(top_dir):
    catalogs = {}
    for root, dirs, files in os.walk(top_dir, topdown=False):
        for file in files:
            if file.endswith(PO_EXT):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, top_dir)
                with io.open(path, 'rb') as f:
                    catalogs[rel_path] = pofile.read_po(f)
            else:
                continue
    return catalogs


def load_lines_with_header_len(path):
    with open(path) as f:
        lines = f.readlines()
    header_len = lines.index('\n') if '\n' in lines else len(lines)
    return lines, header_len


def main(args):
    # Load source/target po files
    source_catalogs = load_catalogs(args.source)
    target_catalogs = load_catalogs(args.target)

    # Fill/format target catalogs
    for path in source_catalogs:
        source_catalog = source_catalogs[path]
        source_path = os.path.join(args.source, path)
        if path in target_catalogs:
            target_path = os.path.join(args.target, path)
            print(target_path)
            target_catalog = target_catalogs[path]
            # target_catalog.header_comment = source_catalog.header_comment
            # target_catalog.fuzzy = source_catalog.fuzzy
            # target_catalog.mime_headers = source_catalog.mime_headers
            for source_message in source_catalog:
                if source_message.id == source_message.string:
                    target_message = target_catalog.get(source_message.id)
                    if target_message is not None and len(target_message.string) == 0:
                        target_message.string = target_message.id
                        print("\t'%s' is filled" % target_message.string)

            # Write target once
            with io.open(target_path, 'wb') as f:
                pofile.write_po(f, target_catalog, width=79)

            # Copy headers
            source_lines, source_header_len = load_lines_with_header_len(source_path)
            target_lines, target_header_len = load_lines_with_header_len(target_path)
            final_lines = source_lines[0:source_header_len] + target_lines[target_header_len:]
            with open(target_path, mode='w') as f:
                f.writelines(final_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format target files')
    parser.add_argument('source', nargs='?', default='./source',
                        help="A source directory to compare (default is './source')")
    parser.add_argument('target', nargs='?', default='./target',
                        help="A target directory to format (default is './target')")
    args = parser.parse_args()
    main(args)
