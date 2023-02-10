from path_finder.PathFinder import PathFinder


if __name__ == "__main__":
    path_finder = PathFinder()
    path_finder.find_path_on_image('./mapping/map1.png')
    path_finder.find_path_on_image('./mapping/penalty_map_processed_lr.png')
    path_finder.find_path_on_image('./mapping/map_low_res.png')
