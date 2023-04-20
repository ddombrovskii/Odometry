from PathFinder.path_finder import PathFinder


if __name__ == "__main__":
    PathFinder('Maps/simple_test.bmp')()
    PathFinder('Maps/map1.png')()
    PathFinder('Maps/penalty_map_processed_lr.png')()
    PathFinder('Maps/map_low_res.png')()

