import secrets

from flask import g


def generate_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)


def get_nonce():
    if not getattr(g, 'csp_nonce', None):
        generate_nonce()
    return g.csp_nonce


def csp_context():
    return {'csp_nonce': get_nonce()}


def build_csp(script_hosts=None, connect_hosts=None, form_actions=None, img_hosts=None, font_hosts=None,
              style_hosts=None):
    script_hosts = script_hosts or []
    connect_hosts = connect_hosts or []
    form_actions = form_actions or ["'self'"]
    img_hosts = img_hosts or []
    font_hosts = font_hosts or []
    style_hosts = style_hosts or []
    nonce = get_nonce()
    script_sources = " ".join(["'self'", f"'nonce-{nonce}'", *script_hosts])
    connect_sources = " ".join(["'self'", *connect_hosts])
    form_action_sources = " ".join(form_actions)
    img_sources = " ".join(["'self'", *img_hosts])
    font_sources = " ".join(["'self'", *font_hosts])
    style_sources = " ".join(["'self'", *style_hosts])

    return "; ".join([
        "default-src 'self'",
        f"script-src {script_sources}",
        f"script-src-elem {script_sources}",
        "script-src-attr 'none'",
        f"style-src {style_sources}",
        f"img-src {img_sources}",
        f"font-src {font_sources}",
        f"connect-src {connect_sources}",
        f"form-action {form_action_sources}",
    ])
