#pragma once

#include <string>
#include <fstream>
#include <vector>
#include <map>

#include "geom_utils.h"

#include "off_triangle.h"

class OffFile
{
public:
  OffFile(const std::string& fname);
  ~OffFile();

  bool open();
  void close();

  void writeHeader();
  void writeVertsFacesEdges(size_t vertsNum, size_t facesNum, size_t edgesNum);
  void writeVertices(const std::map<GeomUtils::CPoint3d, int>& vertices);
  void writeTriangles(const std::vector<Triangle>& triangles, const std::map<GeomUtils::CPoint3d, int>& ptIndexMap);

  std::string name() const;

private:
  std::string header = "OFF";

  std::string filename;

  std::ofstream fileStream;
};