# Tennis
Python program for tennis gun

Данная программа необходима для пристрелки теннисной пушки.
Существует мишень размером 1500 мм x 1500 мм (цвет – произвольный), в эту мишень прилетает теннисный мячик диаметром 50 мм со скоростью полёта около 20 м/с (цвет – произвольный).  При попадании мяч отскакивает и пропадает из кадра. Камера при этом расположена на расстоянии 5 – 10 метров от мишени под углом 30° – 60° к ней. Задачи: детектировать мишень, убрать с изображения перспективное искажение, детектировать мячик, вычислить координату его удара о мишень (с точностью до 70 мм), записать координаты в файл. 
При работе над проектом были применены такие технологии как машинное обучение, использовалось в сторонней библиотеке для детектирования меток, расположенных по краям мишени, и вычитание фона (для поиска шарика).
Так же было проведено исследование, направленное на поиск траектории шарика и вычисление точки удара о мишень.
В работе использовался язык Python и его библиотеки (os, tkinter, cv2, numpy, plt)
Проект передан заказчику и нормально функционирует.
Программу можно было бы улучшить, добавив в неё обработку ошибок и хороший web интерфейс, но этого не потребовалось.



Для запуска необходимо расположить метки в соответствии с номерами на углах. Размещать против часовой стрелки, начаная с левого верхнего угла, так чтобы красная точка каждой метки совпала с наружным углом мишени.

Для стабильной работы файлы .png должны располагаться в одной директоории с файлом .py или .exe.

Свич R/L - переключатель положения камеры относительно мишени (справа или слева). Свич 0/1 - переключатель видеопотока (первая или вторая камера). 
