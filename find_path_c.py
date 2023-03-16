from PathFinder.path_finder import PathFinder


if __name__ == "__main__":
    PathFinder('Maps/simple_test.bmp')()  # - сойдёт
    PathFinder('Maps/map1.png')()  # - сойдёт
    PathFinder('Maps/penalty_map_processed_lr.png')() # херова
    PathFinder('Maps/map_low_res.png')()  # ваще норм
