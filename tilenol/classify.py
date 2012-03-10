from . import ewmh
from . import icccm


class Classifier(object):

    def __init__(self):
        self.global_rules = []
        self.class_rules = {}

    def add_rule(self, condition, action, klass=None):
        if klass is None:
            self.global_rules.append((condition, action))
        else:
            if klass not in self.class_rules:
                self.class_rules[klass] = []
            self.class_rules[klass].append((condition, action))

    def default_rules(self):
        self.add_rule(ewmh.match_type(
            'UTILITY',
            'NOTIFICATION',
            'TOOLBAR',
            'SPLASH',
            ), set_lprop('floating', True))
        self.add_rule(ewmh.match_type('UTILITY'),
                      set_lprop('floating', False),
                      klass='Gimp')
        self.add_rule(match_role('gimp-toolbox'),
                      set_lprop('stack', 'left'),
                      klass='Gimp')
        self.add_rule(match_role('gimp-dock'),
                      set_lprop('stack', 'right'),
                      klass='Gimp')
        self.add_rule(lambda w: True,
                      set_lprop('floating', True),
                      klass='VCLSalFrame')
        self.add_rule(lambda w: True,
                      set_lprop('floating', False),
                      klass='VCLSalFrame.DocumentWindow')

    def apply(self, win):
        for condition, action in self.global_rules:
            if condition(win):
                action(win)

        for klass in self._split_class(win.props.get('WM_CLASS', '')):
            for condition, action in self.class_rules.get(klass, ''):
                if condition(win):
                    action(win)

    @staticmethod
    def _split_class(cls):
        for name in cls.split('\0'):
            if not name:
                continue
            yield name
            while '-' in name:
                name, _ = name.rsplit('-', 1)
                yield name


def match_role(*roles):
    def checker(win):
        for typ in roles:
            if typ == win.props.get('WM_WINDOW_ROLE'):
                return True
    return checker

def set_property(name, value):
    def setter(win):
        setattr(win, name, value)
    return setter


def set_lprop(name, value):
    def setter(win):
        setattr(win.lprops, name, value)
    return setter

