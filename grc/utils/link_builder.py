from markupsafe import Markup


class LinkBuilder:

    def __init__(self, opening_anchor_tag, link_text, before_link_text='', after_link_text=''):
        self.opening_anchor_tag = opening_anchor_tag
        self.link_text = link_text
        self.before_link_text = before_link_text
        self.after_link_text = after_link_text

    def get_link_with_text_safe(self):
        return Markup(f'{self.before_link_text}{self.opening_anchor_tag}{self.link_text}</a>{self.after_link_text}')


