from __future__ import print_function, unicode_literals

from conllu.parser import ParseException

DEFAULT_EXCLUDE_FIELDS = ('id', 'deprel', 'xpostag', 'feats', 'head', 'deps', 'misc')


def print_tree_b(tokentree, s="", exclude_fields=DEFAULT_EXCLUDE_FIELDS):
    if not tokentree.token:
        raise ParseException("Can't print, token is None.")

    if "deprel" not in tokentree.token or "id" not in tokentree.token:
        raise ParseException("Can't print, token is missing either the id or deprel fields.")

    relevant_data = tokentree.token.copy()
    for key in exclude_fields:
        if key in relevant_data:
            del relevant_data[key]

    print(tokentree.token['form'], s)

    if len(tokentree.children) == 0 or tokentree.children is None:
        return "{}/{} ".format(tokentree.token['form'], tokentree.token['upostag'])

    for child in tokentree.children:
        s += "(" + print_tree_b(child, s=s, exclude_fields=exclude_fields) + ")"

    return s



# def print_tree_brackets(tokentree, s="", exclude_fields=DEFAULT_EXCLUDE_FIELDS):
#
#     if not tokentree.token:
#         raise ParseException("Can't print, token is None.")
#
#     if "deprel" not in tokentree.token or "id" not in tokentree.token:
#         raise ParseException("Can't print, token is missing either the id or deprel fields.")
#
#     print(tokentree.token['form'])
#     relevant_data = tokentree.token.copy()
#     for key in exclude_fields:
#         if key in relevant_data:
#             del relevant_data[key]
#
#     s += '( {}/{} )'.format(tokentree.token['form'], tokentree.token['upostag'])
#
#     for child in tokentree.children:
#         s += '(' + print_tree_brackets(child) + ') '
#
#     return s
#

