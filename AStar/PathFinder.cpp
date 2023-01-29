#include "Map/WeightMap.h"
#include "AStar/AStar.h"
#include "PathFinder.h"

/*
class _Pt2(Structure):
	_fields_ = ("row", c_int32), ("col", c_int32)

class Path(Structure):
	_fields_ = ("cost", c_float), ("n_points", c_int32), ("path_points", POINTER(_Pt2)) 

class _AStar(Structure):
	???


*/

DLL_EXPORT AStar* a_start_new(const int rows, const int cols, const float* weights)
{
	return new AStar(rows, cols, weights);
}
DLL_EXPORT void   a_start_del(AStar* a_star)
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
	p->path_points = (Pt2*)malloc(sizeof(Pt2) * n_points);
	assert(p->path_points);
	return p;
}
DLL_EXPORT void      path_del(Path* path)
{
	if (path == NULL)return;
	if (path->path_points != NULL)free(path->path_points);
	free(path);
}
DLL_EXPORT Path*    find_path(AStar* path_finder, const Pt2* start, const  Pt2* end)
{
	if (!path_finder->search(Point(start->row, start->col), Point(end->row, end->col)))
	{
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
	return path;
}


int main(int argc, char* argv[])
{
    const float* raw_map = new float[64]
    {
        0.0f, 0.0f, 1.0f, 1.0f, 1.0f, 1.0f, 0.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 1.0f,
        1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 1.0f,
        1.0f, 0.0f, 0.0f, 0.0f, 1.0f, 1.0f, 0.0f, 0.0f,
        1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f,
        1.0f, 0.0f, 1.0f, 1.0f, 1.0f, 1.0f, 0.0f, 1.0f,
        1.0f, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
        1.0f, 1.0f, 1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f
    };

    WeightMap map(8, 8, raw_map);
    std::cout << map;
    std::cout << "\n";
    AStar a_star(8, 8, raw_map);
    a_star.search();
    std::cout << a_star;

    return 0;
}

