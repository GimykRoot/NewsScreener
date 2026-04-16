from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty, StringProperty
from kivy.graphics import Color, RoundedRectangle

import pandas as pd 
import webbrowser
from finvizfinance.quote import finvizfinance
from finvizfinance.news import News

class NewsScreenerApp(App):

    def build(self):
        Window.size = (600, 600)
        Window.clearcolor = (0.96, 0.96, 0.97, 1)
        self.titel = 'Article Screener'
        return ScreenerGUI()

class RoundedButton(Button):
    
    def __init__(self, on_press_color, **kwargs):
        self.first_color = kwargs.get('background_color', (0.094, 0.373, 0.647, 1))
        self.on_press_color = kwargs.pop('on_press_color', (0.07, 0.3, 0.5, 1))
        self.shape_color = self.first_color
        kwargs['background_normal'] = ''
        kwargs['background_down'] = ''
        kwargs['background_color'] = (0, 0, 0, 0)
        super(RoundedButton, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.shape_color)
            RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[20,] 
            )
            
    def on_press(self):
        self.shape_color = self.on_press_color
        self.update_canvas()

    def on_release(self):
        self.shape_color = self.first_color
        self.update_canvas()

class RoundedToggleButton(ToggleButton):
    
    def __init__(self, on_press_color, **kwargs):
        self.first_color = kwargs.get('background_color', (0.094, 0.373, 0.647, 1))
        self.on_press_color = kwargs.pop('on_press_color', (0.7, 0.3, 0.5, 1))
        self.shape_color = self.first_color
        kwargs['background_normal'] = ''
        kwargs['background_down'] = ''
        kwargs['background_color'] = (0, 0, 0, 0)
        super(RoundedToggleButton, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, state=self.update_canvas)
        
    def update_canvas(self, *args):
        if self.state == 'down':
            self.shape_color = self.on_press_color
        else:
            self.shape_color = self.first_color

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.shape_color)
            RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[20,]
            )
            
    def on_press(self): #this will avoid the unselection of the button(at least one button will be selected)
        if self.state == 'normal' and self.group:
            self.state = 'down'
        self.update_canvas()

class ArticleListItem(BoxLayout):      #widget for every file
    selected = BooleanProperty(False)
    name = StringProperty('')


    def __init__(self, date, name, source, link, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = 5
        self.spacing = 10
        self.selected_link = link
 
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(radius=[8], size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.bind(selected=self.on_select_change)
        # date
        date_label = Label(
            text=date,
            size_hint_x=0.1,
            color=(0.498, 0.498, 0.478, 1),
            halign='left',
            valign='middle'
        )
        date_label.bind(size=date_label.setter('text_size'))
        self.add_widget(date_label)
        #title
        name_label = Label(
            text=name,
            size_hint_x=0.35,
            color=(0.173, 0.173, 0.165, 1),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        self.add_widget(name_label)
        #source
        source_label = Label(
            text=source,
            size_hint_x=0.15,
            color=(0.498, 0.498, 0.478, 1),
            halign='right',
            valign='middle'
        )
        source_label.bind(size=source_label.setter('text_size'))
        self.add_widget(source_label)
        #link
        link_label = Label(
            text=link,
            size_hint_x=0.40,
            color=(0.118, 0.565, 1, 1),
            halign='center',
            valign='middle'
        )
        link_label.bind(size=link_label.setter('text_size'))
        self.add_widget(link_label)
        

        
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_select_change(self, instance, value):
        if value:
            self.bg_color.rgba = (0.2, 0.6, 1, 0.3)
        else:
            self.bg_color.rgba = (0.1, 0.1, 0.1, 0)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                from kivy.app import App
                app = App.get_running_app()
                app.root.open_link(self.selected_link)
            else:
                self.selected = not self.selected
            return True
        return super().on_touch_down(touch)


class ScreenerGUI(BoxLayout, News):
  
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.current_type_of_info = None
        self.setup_ui()

    def setup_ui(self):
        #Top panel
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.05, spacing=10)    
        #search field
        input_field =  GridLayout(cols=2, size_hint_y=1, size_hint_x=0.75)
        self.search_query = TextInput(
            multiline=False, 
            hint_text='NewsScreener',
            background_color=(0.865,0.865,0.865, 0.1)
        )
        input_field.add_widget(self.search_query)
        top_layout.add_widget(input_field)
        #search button
        search_btn = RoundedButton(
            text='Search', 
            size_hint_x=0.15, 
            on_press_color = (0.094, 0.373, 0.647, 0.07),
            background_color=(0.094, 0.373, 0.647, 1), 
            color=(0.706, 0.831, 0.957, 1)
        )
        search_btn.bind(on_press=lambda instance: self.display_content(None, instance))
        top_layout.add_widget(search_btn)
        #refresh button
        refresh_btn = RoundedButton(
            text='Refresh', 
            size_hint_x=0.15, 
            on_press_color = (0.094, 0.373, 0.647, 0.07),
            background_color=(0.094, 0.373, 0.647, 1), 
            color=(0.706, 0.831, 0.957, 1)
        )
        refresh_btn.bind(on_press=lambda instance: self.display_content(self.current_type_of_info, instance))
        top_layout.add_widget(refresh_btn)
        self.add_widget(top_layout)
        #content type
        content_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)    
        #Button for all
        news_btn = RoundedToggleButton(
            text='All', 
            group='categories',
            size_hint_x=0.2, 
            on_press_color = (0.7, 0.3, 0.5, 1),
            background_color=(0.094, 0.373, 0.647, 0.07),
            color=(0, 0, 0, 1)
        )
        news_btn.bind(on_press=lambda instance: self.display_content(None, instance))
        content_layout.add_widget(news_btn)
        #Button for news
        news_btn = RoundedToggleButton(
            text='News', 
            group='categories',
            size_hint_x=0.2, 
            on_press_color = (0.7, 0.3, 0.5, 1),
            background_color=(0.094, 0.373, 0.647, 0.07),
            color=(0, 0, 0, 1)
        )
        news_btn.bind(on_press=lambda instance: self.display_content('news', instance))
        content_layout.add_widget(news_btn)
        #Blogs
        blogs_btn = RoundedToggleButton(
            text='Blogs',
            group='categories',
            size_hint_x=0.2, 
            on_press_color = (0.7, 0.3, 0.5, 1),
            background_color=(0.094, 0.373, 0.647, 0.07),
            color=(0, 0, 0, 1)
        )
        blogs_btn.bind(on_press=lambda instance: self.display_content('blogs', instance))
        content_layout.add_widget(blogs_btn)
        self.add_widget(content_layout)
        
        # Names of labels
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.05, spacing=10)
        header_layout.add_widget(
            Label(
                text='Date', 
                size_hint_x=0.10, 
                bold=True, 
                color=(0, 0, 0, 1)
            )
        )
        header_layout.add_widget(
            Label(
                text='Title', 
                size_hint_x=0.35, 
                bold=True, 
                color=(0, 0, 0, 1)
            )
        )
        header_layout.add_widget(
            Label(
                text='Source', 
                size_hint_x=0.10, 
                bold=True, 
                color=(0, 0, 0, 1)
            )
        )
        header_layout.add_widget(
            Label(
                text='Link', 
                size_hint_x=0.45, 
                bold=True, 
                color=(0, 0, 0, 1)
            )
        )
        
        self.add_widget(header_layout)
        # Scroll of files
        scroll_view = ScrollView(size_hint=(1, 0.85))
        self.news_list = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.news_list.bind(minimum_height=self.news_list.setter('height'))
        scroll_view.add_widget(self.news_list)
        self.add_widget(scroll_view)
    
    def convert_et_to_local(self, dt_element):
        if isinstance(dt_element, str):
            dt_element = pd.to_datetime(dt_element)
        if isinstance(dt_element, pd.Timestamp):
            if dt_element.tz is None:
                dt_element = dt_element.tz_localize('US/Eastern')
        return dt_element.tz_convert('Europe/Berlin').strftime('%Y-%m-%d %H:%M')

    def search_article(self, df):
        if self.search_query:
            mask = df['Title'].str.contains(self.search_query.text, case=False, na=False)
            return df[mask]
        return df

    def display_content(self, content_type, instance):
        self.news_list.clear_widgets()
        self.current_type_of_info = content_type
        try:
            all_infos=self.get_news()
            if not content_type: 
                df_to_process = pd.concat(all_infos.values(), ignore_index=True) #unites all articles
            else:
                df_to_process = all_infos[content_type]
            df_to_process['Date'] = pd.to_datetime(df_to_process['Date'])
            df_to_process = df_to_process.sort_values(by='Date', ascending=False)
            
            info_news = self.search_article(df_to_process)
            for _, item in info_news.iterrows():
                local_t = self.convert_et_to_local(item.Date)
                article_date = f"{local_t} (Berlin) | {item.Date} ET"
                article_title = item.Title
                article_source = item.Source
                article_link = item.Link

                article_item = ArticleListItem(
                    date=article_date,
                    name=article_title,
                    source=article_source,
                    link=article_link
                )
                self.news_list.add_widget(article_item)
        except PermissionError:
            self.show_error("No infos")
        except Exception as e:
            self.show_error(f"An Error occurred: {e}")
            
    def open_link(self, link):
        webbrowser.open(link)

    def show_error(self, message):
        #Error return
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.8)
        )
        popup.open()
