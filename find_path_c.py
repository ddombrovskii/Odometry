from path_finder.PathFinder import PathFinder


if __name__ == "__main__":
    #simple_test.bmp
    PathFinder('./mapping/simple_test.bmp')()  # - сойдёт
    # PathFinder('./mapping/map1.png')()  # - сойдёт
    PathFinder('./mapping/penalty_map_processed_lr.png')() # херова
    PathFinder('./mapping/map_low_res.png')()  # ваще норм
