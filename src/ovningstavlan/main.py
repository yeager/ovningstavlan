import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gdk, Gio
import gettext, locale, os, json, time, random
__version__ = "0.1.0"

APP_ID = "se.danielnylander.ovningstavlan"
LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'share', 'locale')
if not os.path.isdir(LOCALE_DIR): LOCALE_DIR = '/usr/share/locale'
try:
    locale.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.textdomain(APP_ID)
except Exception: pass
_ = gettext.gettext
def N_(s): return s

EXERCISES = [
    {'name': N_('Letters'), 'icon': '🔤', 'items': list('ABCDEFGHIJ')},
    {'name': N_('Numbers'), 'icon': '🔢', 'items': [str(i) for i in range(1, 11)]},
    {'name': N_('Colors'), 'icon': '🎨', 'items': [N_('Red'), N_('Blue'), N_('Green'), N_('Yellow'), N_('Orange'), N_('Purple')]},
    {'name': N_('Shapes'), 'icon': '🔷', 'items': [N_('Circle'), N_('Square'), N_('Triangle'), N_('Star'), N_('Heart')]},
    {'name': N_('Animals'), 'icon': '🐾', 'items': [N_('Dog'), N_('Cat'), N_('Bird'), N_('Fish'), N_('Horse'), N_('Rabbit')]},
]

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_('Övningstavlan'))
        self.set_default_size(500, 550)
        self._current = None
        self._index = 0
        self._stars = 0

        header = Adw.HeaderBar()
        menu_btn = Gtk.MenuButton(icon_name='open-menu-symbolic')
        menu = Gio.Menu()
        menu.append(_('About'), 'app.about')
        menu_btn.set_menu_model(menu)
        header.pack_end(menu_btn)

        self._stack = Gtk.Stack()

        # Categories
        picker = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        picker.set_margin_top(24)
        picker.set_margin_start(24)
        picker.set_margin_end(24)
        title = Gtk.Label(label=_('What do you want to practice?'))
        title.add_css_class('title-2')
        picker.append(title)
        for i, ex in enumerate(EXERCISES):
            btn = Gtk.Button()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            box.set_margin_start(12)
            icon = Gtk.Label(label=ex['icon'])
            icon.add_css_class('title-2')
            box.append(icon)
            name = Gtk.Label(label=_(ex['name']))
            name.add_css_class('title-4')
            box.append(name)
            btn.set_child(box)
            btn.add_css_class('card')
            btn.connect('clicked', self._start, i)
            picker.append(btn)
        self._stack.add_titled(picker, 'picker', _('Practice'))

        # Flash card
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        card.set_valign(Gtk.Align.CENTER)
        card.set_margin_top(32)
        card.set_margin_start(32)
        card.set_margin_end(32)
        self._card_text = Gtk.Label()
        self._card_text.add_css_class('title-1')
        card.append(self._card_text)
        self._card_num = Gtk.Label()
        self._card_num.add_css_class('dim-label')
        card.append(self._card_num)
        self._stars_label = Gtk.Label()
        self._stars_label.add_css_class('title-3')
        card.append(self._stars_label)
        self._prog = Gtk.ProgressBar()
        card.append(self._prog)
        btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btns.set_halign(Gtk.Align.CENTER)
        next_btn = Gtk.Button(label=_('Next ⭐'))
        next_btn.add_css_class('suggested-action')
        next_btn.add_css_class('pill')
        next_btn.connect('clicked', self._next)
        btns.append(next_btn)
        card.append(btns)
        back = Gtk.Button(label=_('← Back'))
        back.add_css_class('pill')
        back.connect('clicked', lambda b: self._stack.set_visible_child_name('picker'))
        card.append(back)
        self._stack.add_titled(card, 'card', _('Card'))

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main.append(header)
        main.append(self._stack)
        self.set_content(main)

    def _start(self, btn, i):
        self._current = EXERCISES[i]
        self._index = 0
        self._stars = 0
        self._show_card()
        self._stack.set_visible_child_name('card')

    def _show_card(self):
        items = self._current['items']
        item = _(items[self._index]) if self._index < len(items) else ''
        self._card_text.set_text(f"{self._current['icon']}  {item}")
        self._card_num.set_text(_('%d of %d') % (self._index+1, len(items)))
        self._stars_label.set_text('⭐' * self._stars)
        self._prog.set_fraction((self._index+1)/len(items))

    def _next(self, btn):
        self._stars += 1
        items = self._current['items']
        if self._index < len(items)-1:
            self._index += 1
            self._show_card()
        else:
            self._stack.set_visible_child_name('picker')

class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id='se.danielnylander.ovningstavlan')
        self.connect('activate', lambda a: MainWindow(application=a).present())
        about = Gio.SimpleAction.new('about', None)
        about.connect('activate', lambda a,p: Adw.AboutDialog(application_name=_('Övningstavlan'),
            application_icon=APP_ID, version=__version__, developer_name='Daniel Nylander',
            website='https://github.com/yeager/ovningstavlan', license_type=Gtk.License.GPL_3_0,
            comments=_('Practice board with visual feedback')).present(self.get_active_window()))
        self.add_action(about)

def main(): App().run()
if __name__ == '__main__': main()

