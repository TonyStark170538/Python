from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.core.window import Window
import random

Builder.load_file("secret_recipe_app.kv")

class HomeScreen(Screen):
    def on_enter(self):
        chef = self.ids.get("chef_anim")
        if chef:
            self.animate_chef(chef)

    def animate_chef(self, widget):   # not sure if it work?
        anim = Animation(y=widget.y + 10, duration=0.5) + Animation(y=widget.y, duration=0.5)
        anim.repeat = True
        anim.start(widget)

    def search_recipe(self):    # sound
        query = self.ids.search_input.text.strip()
        if query:
            app = MDApp.get_running_app()
            app.play_sound("click.wav")
            app.get_recipes_by_name(query)

    def get_random_recipe(self):
        app = MDApp.get_running_app()
        app.play_sound("music/back_music.mp3")
        app.get_random_recipe()

class DetailScreen(Screen):  # main screen with recipe
    title = StringProperty("")
    instructions = StringProperty("")
    ingredients = ListProperty([])

    def on_enter(self):
        chef = self.ids.get("chef_anim")
        if chef:
            self.animate_chef(chef)

    def animate_chef(self, widget):  # not sure if I need it
        anim = Animation(y=widget.y + 10, duration=0.5) + Animation(y=widget.y, duration=0.5)
        anim.repeat = True
        anim.start(widget)

    def on_ingredients(self, instance, value):   # ingredients don't work
        self.ids.ingredients_list.data = [
            {
                "text": f"- {item}",
                "theme_text_color": "Custom",
                "text_color": (0.4, 0.26, 0.13, 1)
            } for item in value if item.strip()
        ]

class RecipeApp(MDApp):
    score = NumericProperty(0)

    def build(self):
        self.theme_cls.primary_palette = "Brown"
        self.theme_cls.accent_palette = "Pink"
        self.sm = ScreenManager(transition=SlideTransition(duration=0.4))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(DetailScreen(name="detail"))
        return self.sm

    def play_sound(self, sound_file):
        sound = SoundLoader.load(sound_file)
        if sound:
            sound.play()

    def get_recipes_by_name(self, name):   # recipe by name
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={name}"
        UrlRequest(url, self.show_recipes)

    def show_recipes(self, req, result):
        if result["meals"]:
            meal = result["meals"][0]
            self.display_recipe(meal)
        else:
            self.show_no_results()

    def get_random_recipe(self):   # random recipe
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        UrlRequest(url, self.show_random_recipe)

    def show_random_recipe(self, req, result):
        if result["meals"]:
            meal = result["meals"][0]
            self.display_recipe(meal)

    def display_recipe(self, meal):
        self.play_sound("music/transition.wav")
        self.score += 1
        home = self.sm.get_screen("home")
        if home.ids.get("score_label"):   # score don't work
            home.ids.score_label.text = f"Score: {self.score}"

        detail_screen = self.sm.get_screen("detail")
        detail_screen.title = meal.get("strMeal", "")
        detail_screen.instructions = meal.get("strInstructions", "")

        ingredients = []   # ingr don't work
        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                measure = measure.strip() if measure else ""
                ingredients.append(f"{measure} {ingredient.strip()}")

        detail_screen.ingredients = ingredients
        if 'no_result_img' in detail_screen.ids:
            detail_screen.ids.no_result_img.opacity = 0

        self.play_details_music_once()
        self.sm.current = "detail"

        # Show the cute toast message when recipe displayed
        self.show_toast()

    def show_no_results(self):    # no recipe
        detail_screen = self.sm.get_screen("detail")
        detail_screen.title = "Sorry, no matching recipes."
        detail_screen.instructions = " "
        detail_screen.ingredients = []
        self.play_details_music_once()
        self.sm.current = "detail"
        if 'no_result_img' in detail_screen.ids:
            detail_screen.ids.no_result_img.opacity = 1

    def play_details_music_once(self):   # music loop
        if not hasattr(self, 'music_started'):
            self.music_started = True
            self.details_music = SoundLoader.load("music/details_music.mp3")
        if self.details_music:
            self.details_music.loop = True
            self.details_music.volume = 0.3
            self.details_music.play()

    def show_toast(self):    # pop-up toast massage
        messages = [
            "New Recipe Unlocked!",
            "Wow, time to try something new!",
            "You unlocked new cooking skill!",
            "A delicious surprise awaits!",
            "A magical recipe just appeared!",
            "You're cooking up greatness!"
        ]
        message = random.choice(messages)

        toast = Label(
            text=message,
            size_hint=(None, None),
            size=(dp(300), dp(50)),
            pos=(Window.width / 2 - dp(150), Window.height),
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            font_size='18sp',
            bold=True
        )

        with toast.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            Color(1, 0.8, 0.9, 1)
            toast.bg = RoundedRectangle(size=toast.size, pos=toast.pos, radius=[20])
            Color(0.4, 0.26, 0.13, 1)
            toast.border = Line(rounded_rectangle=(toast.x, toast.y, toast.width, toast.height, 20), width=1.2)

        def update_bg(*args):
            toast.bg.size = toast.size
            toast.bg.pos = toast.pos
            toast.border.rounded_rectangle = (toast.x, toast.y, toast.width, toast.height, 20)

        toast.bind(pos=update_bg, size=update_bg)

        Window.add_widget(toast)    # stil massage

        anim = (Animation(y=Window.height - dp(120), duration=0.4, t='out_back') +
                Animation(y=Window.height - dp(100), duration=0.2, t='out_bounce') +
                Animation(opacity=0, duration=4.5))
        anim.bind(on_complete=lambda *x: Window.remove_widget(toast))
        anim.start(toast)

if __name__ == "__main__":
    RecipeApp().run()
