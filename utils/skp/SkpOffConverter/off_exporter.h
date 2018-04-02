#pragma once

#include <string>
#include <vector>
#include <map>

#include <SketchUpAPI/model/defs.h>
#include <SketchUpAPI/transformation.h>

#include "off_file.h"
#include "geom_utils.h"
#include "off_triangle.h"

class OffExporter
{
public:
  OffExporter(const std::string& src, const std::string& dst);
  ~OffExporter();

  bool convert();

private:

  class IndexGenerator
  {
  public:
    int get() { return index++; }

  private:
    int index = 0;
  };

  void releaseModelObjects();

  void writeGeometry();

  void collectTrianglesAndVertices(SUEntitiesRef entities, const SUTransformation& transformation);
  std::vector<SUFaceRef> extractFaces(SUEntitiesRef entities);
  void collectTrianglesAndVerticesFromFaces(const std::vector<SUFaceRef>& faces, const SUTransformation& transformation);
  void computeTrianglesAndVerticesFromFace(SUFaceRef face, const SUTransformation& transformation);
  void updateIndices();

  OffFile file;
  std::string sourceFilePath;
  SUModelRef model;

  std::vector<Triangle> meshTriangles;

  std::map<GeomUtils::CPoint3d, int> ptIndexMap;

  IndexGenerator idxGen;
};