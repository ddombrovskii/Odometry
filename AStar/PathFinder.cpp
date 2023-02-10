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


DLL_EXPORT Map2* map_2_new(const int rows, const int cols, const float* weights)
{
	assert(weights);
	Map2* map = (Map2*)malloc(sizeof(Map2));
	assert(map);
	map->cols = cols;
	map->rows = rows;
	map->weights = weights;
	return map;
}

DLL_EXPORT void  map_2_del(Map2* map) 
{
	assert(map);
	free(map);
}

DLL_EXPORT Map3* map_3_new(const int rows, const int cols, const int layers, const float* weights)
{
	assert(weights);
	Map3* map = (Map3*)malloc(sizeof(Map3));
	assert(map);
	map->cols = cols;
	map->rows = rows;
	map->layers = layers;
	map->weights = weights;
	return map;
}

DLL_EXPORT void  map_3_del(Map3* map)
{
	assert(map);
	free(map);
}

DLL_EXPORT Path2*   path_2_new(const int n_points)
{
	Path2* p = (Path2*)malloc(sizeof(Path2));
	assert(p);
	if (n_points == 0) return p;
	p->n_points = n_points;
	p->path_points = (Pt2*)malloc(sizeof(Pt2) * n_points);
	assert(p->path_points);
	return p;
}

DLL_EXPORT void     path_2_del(Path2* path)
{
	if (path == NULL)return;
	if (path->path_points != NULL)free(path->path_points);
	free(path);
}

DLL_EXPORT Path2*  find_path_2(const Map2* map, const Pt2* start, const  Pt2* end, const int& heuristics)
{
	AStar2 path_finder(map->rows, map->cols, map->weights);
	
	Path2d path = path_finder.search(Point2(start->row, start->col), Point2(end->row, end->col), heuristics);

	if (path == nullptr)
	{
		return path_2_new(0);
	}
	
	Path2* out_path = path_2_new(path->size());
	
	/// path->cost = path->back().;
	
	int index = 0;

	for (const auto& pt : *path)
	{
		out_path->path_points[index] = { pt.row, pt.col };
		index++;
	}

	return out_path;
}

DLL_EXPORT Path3*   path_3_new(const int n_points)
{
	Path3* p = (Path3*)malloc(sizeof(Path3));
	assert(p);
	if (n_points == 0) return p;
	p->n_points = n_points;
	p->path_points = (Pt3*)malloc(sizeof(Pt3) * n_points);
	assert(p->path_points);
	return p;
}

DLL_EXPORT void     path_3_del(Path3* path)
{
	if (path == NULL)return;
	if (path->path_points != NULL)free(path->path_points);
	free(path);
}

DLL_EXPORT Path3*  find_path_3(const Map3* map, const Pt3* start, const  Pt3* end, const int& heuristics)
{
	AStar3 path_finder(map->rows, map->cols, map->layers, map->weights);

	Path3d path = path_finder.search(Point3(start->row, start->col, start->layer), Point3(end->row, end->col, end->layer), heuristics);

	if (path == nullptr)
	{
		return path_3_new(0);
	}

	Path3* new_path = path_3_new(path->size());

	// path->cost = path_finder.path_cost();
	
	int index = 0;

	for (const auto& pt : *path)
	{
		new_path->path_points[index] = { pt.row, pt.col, pt.layer };
		index++;
	}

	return new_path;
}


#define _X 1000.0f
#define _F 1.0f


DLL_EXPORT void		print_map2(const Map2* map)
{
	/// вообще-то можно взыать у WeightMap2 или WeightMap3 перегрузку оператора <<
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

	const float* map3 = new float[49 * 3]
	{
		_F, _X, _F, _F, _F, _F, _F,
		_F, _X, _F, _F, _F, _F, _F,
		_F, _X, _X, _X, _X, _F, _F,
		_F, _F, _F, _F, _X, _F, _F,
		_F, _F, _F, _F, _X, _F, _F,
		_F, _F, _F, _F, _X, _F, _F,
		_F, _F, _F, _F, _X, _F, _F,
	//		   .0f	 .0f   .0f	 .0f   .0f	 .0f
		_F, _X, _F, _F, _F, _F, _F,
		_F, _X, _F, _F, _F, _F, _F,
		_F, _X, _X, _X, _X, _F, _F,
		_F, _X, _F, _F, _F, _X, _F,
		_F, _X, _F, _F, _F, _X, _F,
		_F, _X, _X, _X, _X, _X, _F,
		_F, _F, _F, _F, _X, _F, _F,
	//		   .0f	 .0f   .0f	 .0f   .0f	 .0f
		_F, _X, _F, _F, _F, _F, _F,
		_F, _X, _F, _F, _F, _F, _F,
		_F, _X, _X, _X, _X, _F, _F,
		_F, _X, _F, _X, _X, _X, _X,
		_F, _X, _F, _X, _F, _F, _X,
		_F, _X, _X, _X, _X, _F, _X,
		_F, _F, _F, _F, _X, _F, _F,
	};

	// WeightMap3 map(7, 7, 3, map3);
	// WeightMap map(32, 32, raw_map);
    //std::cout << map;
    // std::cout << "\n";
    AStar2 a_star2(32, 32, raw_map);
	AStar3 a_star3(7, 7, 3, map3);

	delete[] raw_map;
	delete[] map3;
	// a_star2.search(); // ({ 0, 0 }, { 14, 26 });
	// a_star3.search();
	/*
	
	for (const auto& p : a_star.path())
	{
		std::cout << p;
		std::cout << "\n";
	}
	*/
	/// std::cout << a_star2.path_cost()<<"\n";

    std::cout << a_star2;
	std::cout << "\n";

	//std::cout << a_star3.path_cost() << "\n";

	std::cout << a_star3;
	std::cout << "\n";
    return 0;
}

