import pygame
from support import import_csv_layout, import_cut_graphics
from tiles import StaticTile, Crate, Palm
from decoration import Sky, Water, Clouds


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface

        # ландшафт
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

        # трава
        grass_layout = import_csv_layout(level_data["grass"])
        self.grass_sprites = self.create_tile_group(grass_layout, "grass")

        # ящики
        crates_layout = import_csv_layout(level_data["crates"])
        self.crates_sprites = self.create_tile_group(crates_layout, "crates")

        # пальмы на переднем плане
        fg_palm_layout = import_csv_layout(level_data["fg palms"])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, "fg palms")

        # пальмы на заднем плане
        bg_palm_layout = import_csv_layout(level_data["bg palms"])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, "bg palms")

        # декорации
        self.sky = Sky(6)
        self.water = Water(680, 1280)
        self.clouds = Clouds(375, 1280, 20)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * 64
                    y = row_index * 64

                    if type == "terrain":
                        terrain_tile_list = import_cut_graphics("graphics/terrain/terrain_tiles.png")
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(64, x, y, tile_surface)

                    if type == "grass":
                        grass_tile_list = import_cut_graphics("graphics/decoration/grass/grass.png")
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(64, x, y, tile_surface)

                    if type == "crates":
                        sprite = Crate(64, x, y)

                    if type == "fg palms":
                        if val == "0":
                            sprite = Palm(64, x, y, "graphics/terrain/palm_small", 38)
                        if val == "1":
                            sprite = Palm(64, x, y, "graphics/terrain/palm_large", 64)

                    if type == "bg palms":
                        sprite = sprite = Palm(64, x, y, "graphics/terrain/palm_bg", 64)
                    sprite_group.add(sprite)
        return sprite_group

    # запуск игры
    def run(self):
        # отрисовка спрайтов
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface)

        self.bg_palm_sprites.update()
        self.bg_palm_sprites.draw(self.display_surface)

        self.terrain_sprites.draw(self.display_surface)
        self.crates_sprites.draw(self.display_surface)
        self.grass_sprites.draw(self.display_surface)

        self.fg_palm_sprites.update()
        self.fg_palm_sprites.draw(self.display_surface)

        self.water.draw(self.display_surface)
