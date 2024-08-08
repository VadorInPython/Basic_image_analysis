#!/usr/bin/env python
# coding: utf-8

# # Zadanie 1.2

# <font color = 'red'>
#     
# 1. Dany jest zbiór plików PNG.
#     
# 2. Użytkownik określa rozmiar kafelka (np. 32 x 64 pixele (wysokość x szerokość)).
#     
# 3. Wyszukujemy wszystkie pliki PNG, z których można takie kafelki wyciąć, np. z pliku o rozmiarze 33 x 66 możemy wyciąć 6 takich kafelków.
#     
# 4. Dla każdego kafelka można wyliczyć średnią składowych RGB.
#     
# 5. Napisać skrypt/program/aplikację webową, która po podaniu trzech wartości liczbowych R, G, B oraz rozmiaru kafelka wyszuka N (wartość podawana przez użytkownika) kafelków o średnich wartościach RGB najbardziej zbliżonych do podanych trzech wartości R, G, B.
#     
# 6. Do zadania pasują zbiory danych 1 z tabeli powyżej.
#     
# 7. Koniecznie wykorzystać w rozwiązaniu wielowątkowość.
#     
# </font>

# # 0. Importy

# In[1]:


import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import math
import matplotlib.pyplot as plt
import numpy as np
import time
import os 
from PIL import Image


# 1. Dany jest zbiór plików PNG.

# In[2]:


path = "C:/Users/szymo/Desktop/images_0003"
path1 = "C:/Users/szymo/Desktop/flowers"


# 3. Wyszukujemy wszystkie pliki PNG (lub jpg), z których można takie kafelki wyciąć, np. z pliku o rozmiarze 33 x 66 możemy wyciąć 6 takich kafelków.

# In[3]:


def find_imgs(path, size_check = None):
    lst = []
    for file, subfiles, images in os.walk(path):
        for image in images:
            image_path = os.path.join(file, image)
            if image_path.lower().endswith('.jpg'):
                img = Image.open(image_path)
                if img.size >= size_check:
                    lst.append(image_path)
    return lst


# In[4]:


def extract_tiles(image_path, tile_size):
    img = Image.open(image_path)
    width, height = img.size
    tiles = []

    for y in range(0, height, tile_size[1]):
        for x in range(0, width, tile_size[0]):
            tile = img.crop((x, y, x + tile_size[0], y + tile_size[1]))
            tiles.append(tile)

    return tiles


# In[5]:


def calculate_average_rgb(image):
    r, g, b = image.split() #dzielenie na kanały
    r_avg = sum(r.getdata()) / len(r.getdata())
    g_avg = sum(g.getdata()) / len(g.getdata())
    b_avg = sum(b.getdata()) / len(b.getdata()) #dzielimy ilość pikseli danego koloru w foto przez ilość ilość wszystkich pikseli w danym kanale
    return r_avg, g_avg, b_avg


# In[6]:


def find_nearest_tiles(target_rgb, tiles, n):
    sorted_tiles = sorted(tiles, key=lambda tile: math.dist(target_rgb, calculate_average_rgb(tile)))
    return sorted_tiles[:n]


# # Poniżej podaj dane dot. foto i kafelka

# 2. Użytkownik określa rozmiar kafelka (np. 32 x 64 pixele (wysokość x szerokość)).

# In[7]:


x, y = int(input("Provide x: ")), int(input("Provide y: "))
size = (x, y)
size


# In[8]:


R, G, B = int(input("Provide R: ")), int(input("Provide G: ")), int(input("Provide B: "))
RGB_user = (R, G, B)
RGB_user


# # Wersja z threadpoolexecutor

# In[10]:


path = path
tile_size = size
size_check = (tile_size[0] + 1, tile_size[1] + 1)
target_rgb = RGB_user
n = 10
tiles = []

total_start_time = time.time()

num_threads = 16

#Funkcja do podgladania tego co jest przetwarzane w extract_tiles (jakie zdjecie przez jaki thread)
def monitor(image_path):
    current_thread = threading.current_thread().name
    print(f"Thread {current_thread} przetwarza plik {image_path}")
    return extract_tiles(image_path, tile_size)

find_imgs_executor = ThreadPoolExecutor(max_workers=num_threads)
find_imgs_future = find_imgs_executor.submit(find_imgs, path, size_check)
find_imgs_executor.shutdown()

extract_tiles_executor = ThreadPoolExecutor(max_workers=num_threads)
print("Liczba wątków dla extract_tiles_executor:", extract_tiles_executor._max_workers)
images = find_imgs_future.result()
for result in extract_tiles_executor.map(monitor, images):
    tiles.extend(result)
extract_tiles_executor.shutdown()

find_nearest_tiles_executor = ThreadPoolExecutor(max_workers=num_threads)
print("Liczba wątków dla find_nearest_tiles_executor:", find_nearest_tiles_executor._max_workers)
nearest_tiles = find_nearest_tiles_executor.submit(find_nearest_tiles, target_rgb, tiles, n)
find_nearest_tiles_executor.shutdown()

#Plotowanie kafelków
plt.figure(figsize=(15, 5))
for i, tile in enumerate(nearest_tiles.result()):
    plt.subplot(1, n, i + 1)
    plt.imshow(np.asarray(tile.resize((tile_size))))
    plt.axis("off")
    plt.title(f"Tile {i + 1}")
plt.tight_layout()
plt.show()

total_time = time.time() - total_start_time

print(f"Całkowity czas wykonania: {total_time:.2f} sekund.")


# In[11]:


#Sprawdzić jak executor dzieli proces na wątki (dopasować ilość wątków)
#Co jest zwracane w images, czy mozna pdoejrzec co tam jest zwracane?
#Wyeksportowac pdf, html i python.


# In[12]:


print(images[:5])
len(images)


# In[13]:


print(tiles[:5])


# In[14]:


print(find_imgs_future)
find_imgs_future.result()


# In[15]:


print(nearest_tiles)
nearest_tiles.result()

