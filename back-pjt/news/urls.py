from django.urls import path
from . import views


# api/
urlpatterns = [
    path('articles/', views.show_articles),

    path('articles/<int:id_pk>/', views.article_detail_view),
    path('articles/<int:id_pk>/like/', views.toggle_like),
    path('articles/<int:id_pk>/bookmark/', views.toggle_bookmark),
    path('articles/<int:id_pk>/chatbot/', views.ask_chatbot),
    path('articles/<int:id_pk>/chatbot/reset/', views.reset_chatbot),


    path('user_info/', views.user_info),
    path('user_bookmark/', views.user_bookmark_list),
    path('<int:user_id>/dashboard/', views.user_dashboard),
    path('articles/recommend/', views.personalized_recommendation),
    path('search/', views.search_news),
    path('index/all/', views.index_all_articles),
]
