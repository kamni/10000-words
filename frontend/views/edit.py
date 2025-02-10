"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from frontend.views.base import BaseView

class EditView(BaseView):
    """
    Add and edit text to practice with
    """
    pass

'''
document = {
    'sentences': ['Foo bar.', 'Baz' ],
}

documents = [('Dutch', ['Roodkapje']), ('English', ['Little Red Riding Hood'])]

def DocumentList(documents):
    with ui.column().classes():
        for section, doc_list in documents:
            with ui.expansion(section, icon='folder'):
                with ui.column():
                    for doc in doc_list:
                        ui.label(doc)

def DocumentDisplay(document):
    for sentence in document['sentences']:
        with ui.card():
            ui.label(sentence)


with ui.row():
    DocumentList(documents)
    DocumentDisplay(document)
'''
