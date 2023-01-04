import pygame

from os import walk
from csv import reader
from settings import TILE_SIZE
from level_data import level_0 # test

# Método responsável por aceder a um ficheiro consoante o path indicado, retornando uma lista com as imagens aí presentes
def import_folder(path):
    surface_list = []
    for _,__,imgs in walk(path):
        for img in imgs:
            full_path = path + '/' + img
            img_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(img_surface)
    
    return surface_list

# Método responsável por aceder a um ficheiro csv consoante o path indicado, retornando uma lista com o conteudo do ficheiro
def import_csv(path):
    with open(path) as layer:
        level = reader(layer, delimiter = ',')
        return list(level)    
        
# Método responsável por dividir uma imagem num conjunto de sprites consoante o tamanho do tile definido, devolvendo uma lista com essas sprites 
def import_cut_tiles(path):
    tileset = pygame.image.load(path).convert_alpha()
    tile_num_x = int(tileset.get_size()[0] / TILE_SIZE)
    tile_num_y = int(tileset.get_size()[1] / TILE_SIZE)
    
    tiles = []
    for row in range(tile_num_x):
        y = row * TILE_SIZE
        for column in range(tile_num_y):
            x = column * TILE_SIZE
            tile = pygame.Surface((TILE_SIZE, TILE_SIZE),flags = pygame.SRCALPHA)
            tile.blit(tileset,(0,0),pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            tiles.append(tile)
            
    return tiles