#include "Map/WeightMap.h"
#include "AStar/AStar.h"
#include "PathFinder.h"

/*
class _Pt(Structure):
	_fields_ = ("row", c_int32), ("col", c_int32)

class _Path(Structure):
	_fields_ = ("cost", c_float), ("n_points", c_int32), ("path_points", POINTER(_Pt2)) 

NP_ARRAY_2_D_POINTER = np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags="aligned, contiguous")

class _Map(Structure):
	_fields_ = ("rows", c_int32), ("cols", c_int32), ("weights", NP_ARRAY_2_D_POINTER)

path_new           = interpolators_lib.path_new
path_new.argtypes  = [c_int32,]
path_new.restype   =  POINTER(_Path)
				   
path_del           = interpolators_lib.path_del
path_del.argtypes  = [POINTER(_Path),]
path_del.restype   =  None
				   
find_path          = interpolators_lib.find_path
find_path.argtypes = [POINTER(_Map), POINTER(_Pt), POINTER(_Pt)]
find_path.restype  =  POINTER(_Path)
*/

AStar*            a_start_new(const int rows, const int cols, const float* weights)
{
	return new AStar(rows, cols, weights);
}
void              a_start_del(AStar* a_star)
{
	if (a_star == nullptr)return;
	delete a_star;
}
DLL_EXPORT Path*     path_new(const int n_points)
{
	Path* p = (Path*)malloc(sizeof(Path));
	assert(p);
	if (n_points == 0) return p;
	p->n_points = n_points;
	p->path_points = (Pt*)malloc(sizeof(Pt) * n_points);
	assert(p->path_points);
	return p;
}
DLL_EXPORT void      path_del(Path* path)
{
	if (path == NULL)return;
	if (path->path_points != NULL)free(path->path_points);
	free(path);
}
DLL_EXPORT Path*    find_path(const Map* map, const Pt* start, const  Pt* end)
{
	AStar* path_finder = a_start_new(map->rows, map->cols, map->weights);
	
	assert(path_finder);
	
	if (!path_finder->search(Point(start->row, start->col), Point(end->row, end->col)))
	{
		a_start_del(path_finder);
		return path_new(0);
	}
	int index = 0;
	
	Path* path = path_new(path_finder->path().size());
	
	path->cost = path_finder->path_cost();

	for (const auto& pt : path_finder->path())
	{
		path->path_points[index] = { pt.row, pt.col };
		index++;
	}

	a_start_del(path_finder);

	return path;
}


#define _X 1000.0f
#define _F 1.01f


DLL_EXPORT void		print_map(const Map* map)
{
	int rows = map->rows;
	int cols = map->cols;
	std::cout << "Rows: " << rows << std::endl;
	std::cout << "Cols: " << cols << std::endl;
	for (int i = 0; i < rows; ++i)
	{
		for (int j = 0; j < cols; ++j)
			std::cout << map->weights[rows * i + j] << ' ';
		std::cout << std::endl;
	}
}

int main(int argc, char* argv[])
{
    const float* raw_map = new float[1024]
	{ _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
	  _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F,
	  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
	  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
	  _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F,
	  _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
	  _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
	  _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
	  _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F,
	  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
	  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
	  _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F,
	  _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
	  _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
	  _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
	  _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
	  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F
	};

	// WeightMap map(32, 32, raw_map);
    // std::cout << map;
    std::cout << "\n";
    AStar a_star(32, 32, raw_map);
	a_star.search(); // ({ 0, 0 }, { 14, 26 });

	/*
	
	for (const auto& p : a_star.path())
	{
		std::cout << p;
		std::cout << "\n";
	}
	*/
    std::cout << a_star;

    return 0;
}

