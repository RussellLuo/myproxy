from collections import OrderedDict

from sly import Lexer, Parser


class ConfLexer(Lexer):
    keywords = {'server', 'location', 'set_header'}

    tokens = {
        'domain',
        'path',
        'identifier',
        *keywords,
    }

    literals = {'{', '}', '=', ';'}

    ignore = ' \t'
    ignore_comment = r'\#.*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'[-a-zA-Z_]+(\.[-a-zA-Z_]+){1,}')
    def domain(self, t):
        return t

    @_(r'(/[-a-zA-Z_]*)+')
    def path(self, t):
        return t

    @_(r'[a-zA-Z_][-a-zA-Z_]*')
    def identifier(self, t):
        if t.value in self.keywords:
            t.type = t.value
        return t

    def error(self, value):
        print('Line %d: Bad character %r' % (self.lineno, value[0]))
        self.index += 1


class ConfParser(Parser):
    tokens = ConfLexer.tokens

    @_('server_block extra_blocks')
    def blocks(self, p):
        servers = OrderedDict()
        servers.update(p.server_block)
        if p.extra_blocks:
            servers.update(p.extra_blocks)
        return servers

    @_('')
    def empty(self, p):
        pass

    @_('blocks')
    def extra_blocks(self, p):
        return p.blocks

    @_('empty')
    def extra_blocks(self, p):
        pass

    @_('server "=" domain "{" location_block "}"')
    def server_block(self, p):
        return {p.domain: p.location_block}

    @_('location "=" path "{" location_body "}"')
    def location_block(self, p):
        return {p.path: p.location_body}

    @_('set_header_clause extra_clauses')
    def location_body(self, p):
        clauses = [p.set_header_clause]
        if p.extra_clauses:
            clauses.extend(p.extra_clauses)
        return clauses

    @_('location_body')
    def extra_clauses(self, p):
        return p.location_body

    @_('empty')
    def extra_clauses(self, p):
        pass

    @_('set_header identifier identifier ";"')
    def set_header_clause(self, p):
        return p[1], p[2]


def parse(conf_filename):
    with open(conf_filename, 'r') as f:
        data = f.read()

    lexer = ConfLexer()
    parser = ConfParser()
    result = parser.parse(lexer.tokenize(data))
    return result
