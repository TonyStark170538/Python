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


Builder.load_file("secret_recipe_app.kv")


class HomeScreen(Screen):
    def on_enter(self):
        chef = self.ids.get("chef_anim")
        if chef:
            self.animate_chef(chef)

    def animate_chef(self, widget):
        anim = Animation(y=widget.y + 10, duration=0.5) + Animation(y=widget.y, duration=0.5)
        anim.repeat = True
        anim.start(widget)

    def search_recipe(self):
        query = self.ids.search_input.text.strip()
        if query:
            app = MDApp.get_running_app()
            app.play_sound("click.wav")
            app.get_recipes_by_name(query)

    def get_random_recipe(self):
        app = MDApp.get_running_app()
        app.play_sound("music/back_music.mp3")
        app.get_random_recipe()

class DetailScreen(Screen):
    title = StringProperty("")
    instructions = StringProperty("")
    ingredients = ListProperty([])

    def on_enter(self):
        chef = self.ids.get("chef_anim")
        if chef:
            self.animate_chef(chef)

    def animate_chef(self, widget):
        anim = Animation(y=widget.y + 10, duration=0.5) + Animation(y=widget.y, duration=0.5)
        anim.repeat = True
        anim.start(widget)

    def on_ingredients(self, instance, value):
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

    def get_recipes_by_name(self, name):
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={name}"
        UrlRequest(url, self.show_recipes)

    def show_recipes(self, req, result):
        if result["meals"]:
            meal = result["meals"][0]
            self.display_recipe(meal)
        else:
            self.show_no_results()

    def get_random_recipe(self):
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
        if home.ids.get("score_label"):
            home.ids.score_label.text = f"Score: {self.score}"

        detail_screen = self.sm.get_screen("detail")
        detail_screen.title = meal.get("strMeal", "")
        detail_screen.instructions = meal.get("strInstructions", "")

        ingredients = []
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

    def show_no_results(self):
        detail_screen = self.sm.get_screen("detail")
        detail_screen.title = "Sorry, we couldn't find any matching recipes."
        detail_screen.instructions = " "
        detail_screen.ingredients = " "
        self.play_details_music_once()
        self.sm.current = "detail"
        if 'no_result_img' in detail_screen.ids:
            detail_screen.ids.no_result_img.opacity = 1

    def play_details_music_once(self):
        if not hasattr(self, 'music_started'):
            self.music_started = True
            self.details_music = SoundLoader.load("music/details_music.mp3")
        if self.details_music:
            self.details_music.loop = True
            self.details_music.volume = 0.3
            self.details_music.play()

if __name__ == "__main__":
    RecipeApp().run()
